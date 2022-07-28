from src.ir import ast, typescript_types as tst
from src.transformations.base import change_namespace
from src.ir.context import get_decl
from src.translators.base import BaseTranslator
from src.translators.utils import append_to


class TypeScriptTranslator(BaseTranslator):
    filename = "Main.ts"
    incorrect_filename = "Incorrect.ts"
    executable = "Main.js"
    ident_value = " "

    def __init__(self, package=None, options={}):
        super().__init__(package, options)
        self._children_res = []
        self.ident = 0
        self.is_interface = False
        self.is_void = False
        self.is_lambda = False
        self.current_class = None
        self.current_function = None
        self.context = None
        self._namespace: tuple = ast.GLOBAL_NAMESPACE
        self._nodes_stack = [None]

    def _reset_state(self):
        self._children_res = []
        self.ident = 0
        self.is_interface = False
        self.is_void = False
        self.is_lambda = False
        self.current_class = None
        self.current_function = None
        self.context = None
        self._namespace = ast.GLOBAL_NAMESPACE
        self._nodes_stack = [None]

    def needs_this_prefix(self, node, decl):
        func_name = tst.TypeScriptBuiltinFactory().get_function_type().name[:-1]
        if node.receiver is not None:
            return False

        if decl is None:
            return True # Function is an inherited method

        if isinstance(decl, ast.FunctionDeclaration) and decl.is_class_method():
            return True # Function is method of current class

        if (isinstance(decl, ast.FieldDeclaration) and
            decl.get_type().name[:-1] == func_name):

            return True # Function is callable field
        return False
    @staticmethod
    def get_filename():
        return TypeScriptTranslator.filename

    @staticmethod
    def get_incorrect_filename():
        return TypeScriptTranslator.incorrect_filename

    def type_arg2str(self, t_arg):
        # TypeScript does not have a Wildcard type
        return self.get_type_name(t_arg)

    def get_type_name(self, t):
        t_constructor = getattr(t, 't_constructor', None)
        if not t_constructor:
            return t.get_name()

        func_name = tst.TypeScriptBuiltinFactory().get_function_type().name[:-1]
        if t_constructor.name.startswith(func_name):
            param_types = t.type_args[:-1]
            ret_type = t.type_args[-1]
            res = "({}) => {}".format(
                ",".join([
                    "p" + str(i) + ": " + str(self.type_arg2str(pt))
                    for i, pt in enumerate(param_types)
                ]),
                self.type_arg2str(ret_type)
            )
            return res

        return "{}<{}>".format(t.name, ", ".join([self.type_arg2str(ta)
                                                  for ta in t.type_args]))

    def pop_children_res(self, children):
        len_c = len(children)
        if not len_c:
            return []
        res = self._children_res[-len_c:]
        self._children_res = self._children_res[:-len_c]
        return res

    def visit_program(self, node):
        self.context = node.context
        self.class_decls = [decl for decl in node.declarations
                            if isinstance(decl, ast.ClassDeclaration)]
        children = node.children()
        for c in children:
            c.accept(self)
        res = '\n\n'.join(self.pop_children_res(children))
        self.program = (
            res if self.package is None
            else f"module {self.package} {{\n{res}\n}}"
        )
        self._reset_state()

    @append_to
    def visit_block(self, node):
        children = node.children()
        is_void = self.is_void
        self.is_void = False
        is_interface = self.is_interface
        is_lambda = self.is_lambda
        self.is_lambda = False
        self.is_interface = False
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)

        if is_interface:
            self.is_interface = is_interface
            self.is_lambda = is_lambda
            self._children_res.append("")
            return

        res = "{" if not is_lambda else ""
        res += "\n" + ";\n".join(children_res[:-1])
        if children_res[:-1]:
            res += ";\n"
        ret_keyword = "return " if node.is_func_block and not is_void else ""
        if children_res:
            res += " "*self.ident + ret_keyword + " " + \
                    children_res[-1].strip() + ";\n" + \
                    " "*self.ident
        else:
            res += " "*self.ident + ret_keyword.strip() + ";\n" + \
                   " "*self.ident
        res += "}" if not is_lambda else ""
        self.is_void = is_void
        self.is_interface = is_interface
        self.is_lambda = is_lambda
        self._children_res.append(res)

    @append_to
    def visit_super_instantiation(self, node):
        old_ident = self.ident
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        class_type = self.get_type_name(node.class_type)
        super_call = None

        if node.args is not None:
            children_res = [c.strip() for c in children_res]
            super_call = "super(" + ", ".join(children_res) + ")"

        res = (class_type, super_call)

        self.ident = old_ident
        self._children_res.append(res)

    @append_to
    @change_namespace
    def visit_class_decl(self, node):
        old_ident = self.ident
        self.ident += 2
        prev_is_interface = self.is_interface
        self.is_interface = node.is_interface()
        prev_class = self.current_class
        self.current_class = node
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        field_res = [children_res[i]
                     for i, _ in enumerate(node.fields)]
        len_fields = len(field_res)
        field_names = [field.name  for field in node.fields]

        superclasses_res = [children_res[i + len_fields]
                            for i, _ in enumerate(node.superclasses)]
        len_supercls = len(superclasses_res)

        supertype, supercall = None, None
        if len_supercls > 0:
            supertype, supercall = superclasses_res[0]

        function_res = [children_res[i + len_fields + len_supercls]
                        for i, _ in enumerate(node.functions)]
        len_functions = len(function_res)

        if node.is_abstract() and supertype is not None and node.superclasses[0].args is None:
            # TypeScript requires abstract classes that implement interfaces
            # to either implement all methods
            # or to re-write the signatures with "abstract" in front.
            # This code block resolves the class declaration of the
            # interface supertype that the abstract class (node)
            # implements and re-visits its FunctionDeclaration children
            # in order to add them to its function_res
            abstract_funcs = [f for f in node.get_abstract_functions(self.class_decls)
                              if f.name not in [f.name for f in node.functions]]

            for func in abstract_funcs:
                func.accept(self)
            supertype_func_res = self.pop_children_res(abstract_funcs)

            function_res += supertype_func_res

        type_parameters_res = ", ".join(
            children_res[len_fields + len_supercls + len_functions:])
        class_prefix = node.get_class_prefix()

        res = "{ident}{p} {n}".format(
            ident=" " * old_ident,
            p=class_prefix,
            n=node.name,
        )

        if type_parameters_res:
            res = "{}<{}>".format(res, type_parameters_res)
        if supertype is not None:
            inheritance = (
                " extends "
                if node.is_interface() or node.superclasses[0].args is not None
                else " implements "
            )
            res += inheritance + supertype

        res += " {\n" + " "*old_ident

        # Makes constructor
        if not self.is_interface:
            class_ident = self.ident
            self.ident += 2
            body = "{"

            if supercall is not None:
                body += "\n" + " "*self.ident + supercall
            stripped_fields = [field.strip() for field in field_res]
            for var_name in field_names:
                prefix = "\n" + self.ident * " "
                body += prefix + "this." + var_name + " = " + var_name
            body += "\n" + class_ident*" " + "}\n"
            res += " "*class_ident + "constructor({f}) {b}".format(
                f = ", ".join(stripped_fields),
                b = body,
            )
            self.ident = class_ident

        if field_res:
            res += "\n\n".join(field_res) + "\n"
        if function_res:
            res += "\n\n".join(function_res) + "\n"

        res += old_ident*" " + "\n}"

        self.ident = old_ident
        self.is_interface = prev_is_interface
        self.current_class = prev_class
        self._children_res.append(res)

    @append_to
    def visit_type_param(self, node):
        res = node.name
        if node.bound:
            res += " extends " + self.get_type_name(node.bound)
        self._children_res.append(res)

    @append_to
    def visit_var_decl(self, node):
        old_ident = self.ident
        prefix = " " * self.ident
        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        var_type = "const " if node.is_final else "let "
        res = prefix + var_type + node.name

        if node.var_type is not None:
            res += ": " + self.get_type_name(node.var_type)

        res += " = " + children_res[0]
        self.ident = old_ident
        self._children_res.append(res)

    @append_to
    def visit_call_argument(self, node):
        old_ident = self.ident
        self.ident = 0
        children = node.children()
        for c in node.children():
            c.accept(self)
        self.ident = old_ident
        children_res = self.pop_children_res(children)
        res = children_res[0]
        self._children_res.append(res)

    @append_to
    def visit_field_decl(self, node):
        prefix = self.ident * " "
        res = prefix + node.name + ": " + self.get_type_name(node.field_type)
        self._children_res.append(res)

    @append_to
    def visit_param_decl(self, node):
        old_ident = self.ident
        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)
        self.ident = old_ident

        param_type = node.param_type
        res = node.name + ": " + self.get_type_name(param_type)

        res = "..." + res if node.vararg else res

        if len(children):
            children_res = self.pop_children_res(children)
            res += ("" if self.current_function.body is None
                     else " = " + children_res[0])

        self._children_res.append(res)

    @append_to
    @change_namespace
    def visit_func_decl(self, node):
        old_ident = self.ident
        self.ident += 2
        prev_function = self.current_function
        self.current_function = node
        is_in_class = node.func_type == ast.FunctionDeclaration.CLASS_METHOD
        is_interface = self.is_interface
        self.is_interface = False
        prev_is_void = self.is_void
        self.is_void = node.get_type() == tst.VoidType()

        param_len = len(node.params)

        children = node.children()
        for i, c in enumerate(children):
            prev_namespace = self._namespace
            if i < param_len:
                self._namespace = self._namespace[:-1]
            c.accept(self)
            self._namespace = prev_namespace
        children_res = self.pop_children_res(children)

        param_res = [children_res[i] for i, _ in enumerate(node.params)]
        len_params = len(node.params)

        len_type_params = len(node.type_parameters)
        type_parameters_res = ", ".join(
            children_res[len_params:len_type_params + len_params])

        body_res = children_res[-1] if node.body else ''

        prefix = " " * old_ident

        if not is_in_class:
            prefix += "function "
        elif is_in_class and not node.body and not is_interface:
            prefix += "abstract "

        type_params = (
            "<" + type_parameters_res + ">" if type_parameters_res else "")

        res = prefix + node.name + type_params + "(" + ", ".join(
            param_res) + ")"
        if node.ret_type:
            res += ": " + self.get_type_name(node.ret_type)
        if body_res and isinstance(node.body, ast.Block):
            res += " \n" + body_res
        elif body_res:
            body_res = "return " + body_res.strip() \
                        if not self.is_void \
                        else body_res.strip()
            res += "{\n" + " "*self.ident + \
                    body_res + "\n" + " "*old_ident + \
                    "}"

        self.ident = old_ident
        self.current_function = prev_function
        self.is_void = prev_is_void
        self.is_interface = is_interface
        self._children_res.append(res)

    @append_to
    @change_namespace
    def visit_lambda(self, node):

        old_ident = self.ident
        is_expression = not isinstance(node.body, ast.Block)
        self.ident = 0 if is_expression else self.ident+2

        children = node.children()

        prev_is_void = self.is_void
        self.is_void = node.get_type() == tst.VoidType()

        prev_is_lambda = self.is_lambda
        self.is_lambda = True
        for c in children:
            c.accept(self)
        self.is_lambda = True
        children_res = self.pop_children_res(children)
        self.ident = old_ident
        param_res = [children_res[i] for i, _ in enumerate (node.params)]
        body_res = children_res[-1] if node.body else ''

        if not is_expression:
            body_res = "{" + body_res + " "*old_ident + "}\n"

        res = "({params}): {ret} => {body}".format(
            params=", ".join(param_res),
            ret=self.get_type_name(node.ret_type),
            body=body_res,
        )

        self.is_void = prev_is_void
        self.is_lambda = prev_is_lambda
        self._children_res.append(res)

    @append_to
    def visit_bottom_constant(self, node):
        bottom = "(undefined as unknown)"

        if node.t:
            bottom = "(" + bottom + " as {})".format(
                self.get_type_name(node.t)
            )
        else:
            bottom = "(undefined as never)"

        res = " "*self.ident + bottom
        self._children_res.append(res)

    @append_to
    def visit_integer_constant(self, node):
        literal = "BigInt({})".format(str(node.literal)) \
                    if isinstance(node.integer_type, tst.BigIntegerType) \
                    else str(node.literal)
        self._children_res.append(" "*self.ident + literal)

    @append_to
    def visit_real_constant(self, node):
        literal = str(node.literal)
        self._children_res.append(" "*self.ident + literal)

    @append_to
    def visit_char_constant(self, node):
        # Symbol type in TypeScript
        self._children_res.append(f"'{node.literal}'")

    @append_to
    def visit_string_constant(self, node):
        self._children_res.append('"{}"'.format(node.literal))

    @append_to
    def visit_boolean_constant(self, node):
        self._children_res.append(str(node.literal))

    @append_to
    def visit_array_expr(self, node):
        if not node.length:
            return self._children_res.append("[]")
        old_ident = self.ident
        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        self.ident = old_ident
        return self._children_res.append("[{}]".format(
            ", ".join(children_res)))

    @append_to
    def visit_variable(self, node):
        res = node.name
        decl = get_decl(self.context, self._namespace, node.name)
        assert decl is not None
        _, decl = decl
        if isinstance(decl, ast.FieldDeclaration):
            res = "this." + res
        self._children_res.append(" " * self.ident + res)

    @append_to
    def visit_binary_op(self, node):
        old_ident = self.ident
        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        res = "{}(({}) {} ({}))".format(
            " "*old_ident, children_res[0], node.operator,
            children_res[1])
        self.ident = old_ident
        self._children_res.append(res)

    def visit_logical_expr(self, node):
        self.visit_binary_op(node)

    def visit_equality_expr(self, node):
        self.visit_binary_op(node)

    def visit_comparison_expr(self, node):
        self.visit_binary_op(node)

    def visit_arith_expr(self, node):
        self.visit_binary_op(node)

    @append_to
    def visit_conditional(self, node):
        old_ident = self.ident
        self.ident += 2
        prev_namespace = self._namespace
        children = node.children()

        cond = children[0]
        cond.accept(self)
        true_branch = children[1]
        false_branch = children[2]

        if isinstance(cond, ast.Is):
            self._namespace = prev_namespace + ('true_block',)
            true_branch.accept(self)
            self._namespace = prev_namespace + ('false_block',)
            false_branch.accept(self)
        else:
            true_branch.accept(self)
            false_branch.accept(self)
        self._namespace = prev_namespace

        children_res = self.pop_children_res(children)
        res = "({}{} ? {} : {})".format(
            " "*old_ident, children_res[0].strip(),
            children_res[1].strip(),
            children_res[2].strip())

        self.ident = old_ident
        self._children_res.append(res)

    @append_to
    def visit_is(self, node):
        old_ident = self.ident
        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        res = "{}{} {} {}".format(
            " " * old_ident, children_res[0], str(node.operator),
            node.rexpr.name)
        self.ident = old_ident
        self._children_res.append(res)

    @append_to
    def visit_new(self, node):
        old_ident = self.ident
        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        self.ident = old_ident
        # Remove type arguments from Parameterized Type
        if getattr(node.class_type, 'can_infer_type_args', None) is True:
            self._children_res.append("new {}({})".format(
                " " * self.ident + node.class_type.name,
                ", ".join(children_res)))
        else:
            self._children_res.append("new {}({})".format(
                " " * self.ident + self.get_type_name(node.class_type),
                ", ".join(children_res)))

    @append_to
    def visit_field_access(self, node):
        old_ident = self.ident
        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        self.ident = old_ident
        receiver_expr = (children_res[0] if children_res[0]
                        else "this")
        res = "{}.{}".format(receiver_expr, node.field)
        self._children_res.append(res)

    @append_to
    def visit_func_ref(self, node):
        old_ident = self.ident

        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)

        self.ident = old_ident
        children_res = self.pop_children_res(children)

        this_prefix = children_res[0] if children_res else ""

        decl = get_decl(self.context, self._namespace, node.func)

        if decl is not None:
            _, decl = decl

        if self.needs_this_prefix(node, decl):
            this_prefix += "this"
            # TODO Must check signatures and not names
            # (for overwritten + overloaded functions)

        res = "{}{}{}".format(
                " "*self.ident,
                "({}).".format(this_prefix) if this_prefix else "",
                node.func
            )

        self._children_res.append(res)

    @append_to
    def visit_func_call(self, node):
        old_ident = self.ident
        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)
        self.ident = old_ident
        children_res = self.pop_children_res(children)
        type_args = ""
        if not node.can_infer_type_args and node.type_args:
            type_args +=  (
                "<" + ",".join(
                [self.get_type_name(t) for t in node.type_args]) \
                + ">"
            )

        this_prefix = ""

        decl = get_decl(self.context, self._namespace, node.name)

        if decl is not None:
            _, decl = decl

        if self.needs_this_prefix(node, decl):
            this_prefix += "this."
            # FIXME Must check signatures and not names
            # (for overwritten + overloaded functions)

        if node.receiver:
            receiver_expr = children_res[0]
            res = "{}{}.{}{}({})".format(
                " " * self.ident, receiver_expr, node.func,
                type_args,
                ", ".join(children_res[1:]))
        else:
            res = "{}{}{}{}({})".format(
                " " * self.ident,
                this_prefix, node.func, type_args,
                ", ".join(children_res))
        self._children_res.append(res)

    @append_to
    def visit_assign(self, node):
        old_ident = self.ident
        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)
        self.ident = old_ident
        children_res = self.pop_children_res(children)

        decl = get_decl(self.context, self._namespace, node.name)

        if decl is not None:
            _, decl = decl

        if node.receiver or decl is None or isinstance(decl, ast.FieldDeclaration):
            receiver_expr = (children_res[0] if node.receiver else "this")
            expr = children_res[1] if node.receiver else children_res[0]
            res = "{}{}.{} = {}".format(
                " " * old_ident,
                receiver_expr,
                node.name,
                expr
            )
        else:
            res = "{}{} = {}".format(
                " " * old_ident,
                node.name,
                children_res[0]
            )

        self.ident = old_ident
        self._children_res.append(res)
