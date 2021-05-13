# pylint: disable=protected-access,too-many-instance-attributes,too-many-locals
# pylint: disable=too-many-statements
import re
from collections import OrderedDict


import src.utils as ut
from src.ir import ast, java_types as jt, types as tp
from src.ir.visitors import ASTVisitor
from src.ir.context import get_decl
from src.transformations.base import change_namespace
from src.translators.utils import get_type_name


def append_to(visit):
    """There are three scenarios:

    1. The node is the main function => set _main_method
    2. The node is a top level function or variable declaration => append the
        result to _main_children (nodes to declared static in Main class)
    3. All other nodes just append them to _children_res

    We also use this function to set _nodes_stack
    """
    def inner(self, node):
        self._nodes_stack.append(node)
        res = visit(self, node)
        self._nodes_stack.pop()
        if (self._namespace == ast.GLOBAL_NAMESPACE and
                isinstance(node, ast.FunctionDeclaration) and
                node.name == "main"):
            # If we want to run the program we must replace main() with
            # main(String[] args)
            self._main_method = res
        elif (self._namespace == ast.GLOBAL_NAMESPACE and
                isinstance(
                    node, (ast.VariableDeclaration, ast.FunctionDeclaration))):
            self._main_children.append(res)
        else:
            self._children_res.append(res)
    return inner


class JavaTranslator(ASTVisitor):

    filename = "Main.java"
    incorrect_filename = "Incorrect.java"
    executable = "Main.jar"
    ident_value = " "

    def __init__(self, package=None):
        self._children_res = []
        self.program = None
        self.ident = 0
        self.package = package
        self.context = None
        self._generator = None
        self._cast_number = False
        # Keep track if a block is in a function that has non-void return type
        self.is_func_non_void_block = False

        # Keep track if a block is in a function that is a nested function
        self.is_nested_func_block = False

        self._namespace: tuple = ast.GLOBAL_NAMESPACE
        # We have to add all non-class declarations top-level declarations
        # into a Main static class. Moreover, they should be static and get
        # accessed with `Main.` prefix.
        self._main_children = []
        # main method should be declared public static void, it should be the
        # last element of Main's block.
        self._main_method = ""

        # We need the following state vars to support blocks inside conditions.
        # In groovy the `{ ... }` is a closure. Hence, if we have a Block
        # inside a condition it means we have a closure, thus we must call it
        # immediately `()`.
        self._inside_is = False
        self._inside_is_function = False

        # A set of numbers where numbers is the number of type parameters that
        # an interface for a function should have.
        self._function_interfaces = set()

        # We need nodes_stack to set semicolons when needed.
        # For instance, in visit_func_call we use a semicolon only if parent
        # node is a block.
        self._nodes_stack = [None]

    def _reset_state(self):
        # Clear the state
        self._main_method = ""
        self._main_children = []
        self._inside_is = False
        self._inside_is_function = False
        self.context = None
        self._cast_number = False
        self.ident = 0
        self.is_func_non_void_block = False
        self.is_nested_func_block = False
        self._namespace = ast.GLOBAL_NAMESPACE
        self._children_res = []
        self._nodes_stack = [None]

    def get_ident(self, extra=0, old_ident=None):
        if old_ident:
            return old_ident * self.ident_value
        return (self.ident + extra) * self.ident_value

    @staticmethod
    def get_filename():
        return JavaTranslator.filename

    @staticmethod
    def get_incorrect_filename():
        return JavaTranslator.incorrect_filename

    def result(self) -> str:
        if self.program is None:
            raise Exception('You have to translate the program first')
        return self.program

    def pop_children_res(self, children):
        len_c = len(children)
        if not len_c:
            return []
        res = self._children_res[-len_c:]
        self._children_res = self._children_res[:-len_c]
        return res

    def _get_main_prefix(self, decl_type, name):
        ns_decls = list(self.context.get_namespaces_decls(
            self._namespace, name, decl_type))
        if len(ns_decls) == 1 and ns_decls[0][0][:-1] == ast.GLOBAL_NAMESPACE:
            return "Main."
        return ""

    def _get_functional_interfaces(self):
        """It produces the required functional interfaces.
        For each number x in _function_interfaces it creates FunctionX+1.
        The last type argument is used for the return type.
        """
        res = ""
        template = "interface Function{}<{}> {{\n{}public {} apply({});\n}}\n\n"
        for number in self._function_interfaces:
            res += template.format(
                number,
                ", ".join(["A" + str(i) for i in range(1, number + 2)]),
                2 * self.ident_value,
                "A" + str(number + 1),
                ", ".join(["A" + str(i) + " a" + str(i)
                          for i in range(1, number + 1)]),
            )
        res = "\n\n" + res if res != "" else ""
        return res

    def _parent_is_block(self):
        # The second node is the parent node
        return isinstance(self._nodes_stack[-2], ast.Block)

    def visit_program(self, node):
        self.context = node.context
        children = node.children()
        for c in children:
            c.accept(self)
        if self.package:
            package_str = 'package ' + self.package + ';\n\n'
        else:
            package_str = ''
        self.ident = 2
        main_decls = [
            self.get_ident() + "static " + d.lstrip()
            for d in self._main_children]
        main_method = self.get_ident() + "public static " + \
            self._main_method.lstrip() if self._main_method else None
        main_cls = "class Main {{\n{main_decls}{main_method}\n}}".format(
            main_decls="\n\n".join(main_decls),
            main_method="\n\n" + main_method if main_method else ""
        )
        other_classes = "\n\n".join(self.pop_children_res(children))
        self.program = "{package}{main}{f_interfaces}{other_classes}".format(
            package=package_str,
            main=main_cls,
            f_interfaces=self._get_functional_interfaces(),
            other_classes="\n\n" + other_classes if other_classes else ''
        )
        self._reset_state()

    @append_to
    def visit_block(self, node):
        children = node.children()
        is_func_non_void_block = self.is_func_non_void_block
        is_nested_func_block = self.is_nested_func_block
        self.is_func_non_void_block = False
        self.is_nested_func_block = False
        children_len = len(children)
        for i, c in enumerate(children):
            # Cast return statement if it's a number literal
            if is_func_non_void_block and i == children_len - 1:
                prev_cast_number = self._cast_number
                self._cast_number = True
                c.accept(self)
                self._cast_number = prev_cast_number
            else:
                c.accept(self)
        children_res = self.pop_children_res(children)
        self.is_func_non_void_block = is_func_non_void_block
        self.is_nested_func_block = is_nested_func_block

        # We use this return statement if the function type is void
        return_stmt = ""
        if not self.is_func_non_void_block:
            ret = "return null;" if self.is_nested_func_block else "return;"
            return_stmt = "\n" + self.get_ident() + ret

        # If return type is void, then we assign the last statement (except
        # function calls) in a variable x and then we use return_stmt.
        if self.is_func_non_void_block:
            sugar = "return "
        elif children and not isinstance(children[-1], ast.FunctionCall):
            sugar = "var x = "
        else:
            sugar = ""

        if len(children_res) == 0:  # empty block
            res = "{ }"
        elif len(children_res) == 1:  # single statement
            children_res[0] = ut.add_string_at(
                children_res[0],
                sugar,
                ut.leading_spaces(children_res[0]))
            res = "{{\n{ident}{stmt}{ret}\n{old_ident}}}".format(
                ident=self.get_ident(),
                stmt=children_res[0].strip(),
                ret=return_stmt,
                old_ident=self.get_ident(extra=-2)
            )
        else:
            children_res[-1] = ut.add_string_at(
                children_res[-1],
                sugar,
                ut.leading_spaces(children_res[-1]))
            res = "{{\n{stmts}{ret}\n{old_ident}}}".format(
                stmts="\n".join(children_res),
                ret=return_stmt,
                old_ident=self.get_ident(extra=-2)
            )
        return res

    @append_to
    def visit_super_instantiation(self, node):
        return get_type_name(node.class_type)

    @append_to
    @change_namespace
    def visit_class_decl(self, node):
        def get_superclasses_interfaces():
            # In correct programs len(superclasses) must be at most 1.
            superclasses = []
            interfaces = []
            for cls_inst in node.superclasses:
                cls_name = cls_inst.class_type.name
                cls_inst = cls_inst.class_type.get_name()
                cls_decl = self.context.get_classes(
                    self._namespace, glob=True)[cls_name]
                if cls_decl.class_type == ast.ClassDeclaration.INTERFACE:
                    interfaces.append(cls_inst)
                else:
                    superclasses.append(cls_inst)
            return superclasses, interfaces

        def get_constructor_params():
            constructor_fields = OrderedDict()
            for field in node.fields:
                constructor_fields[field.name] = get_type_name(
                    field.field_type)
            return constructor_fields

        def construct_constructor():
            params = [tname + ' ' + name
                      for name, tname in
                      get_constructor_params().items()]
            constructor_params = ",".join(params)

            fields = ["this." + f.name + ' = ' + f.name + ";"
                      for f in node.fields]
            constructor_fields = "\n" + self.get_ident(extra=2) if fields \
                else ""
            constructor_fields += ("\n" + self.get_ident(extra=2)).join(fields)

            super_call = ""
            if node.superclasses:
                supercls = node.superclasses[0]
                if not isinstance(supercls.class_type, tp.Builtin):
                    res = ""
                    if supercls.args:
                        translator = JavaTranslator()
                        translator.context = self.context
                        translator._cast_number = True
                        for expr in supercls.args:
                            translator.visit(expr)
                        res = ", ".join(translator._children_res)
                        res = re.sub(r'\s+',' ',res)
                    super_call = "\n" + self.get_ident(extra=2) + 'super(' + \
                        res + ");"
            return ("{ident}public {name}({params}) {{{super_call}{fields}"
                    "{new_line}{close_ident}}}").format(
                ident=self.get_ident(),
                name=node.name,
                params=constructor_params,
                super_call=super_call,
                fields=constructor_fields,
                new_line="\n" if fields else "",
                close_ident=self.get_ident() if fields else ""
            )

        old_ident = self.ident
        self.ident += 2
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        field_res = [children_res[i]
                     for i, _ in enumerate(node.fields)]
        len_fields = len(field_res)
        len_supercls = len(node.superclasses)
        function_res = [children_res[i + len_fields + len_supercls]
                        for i, _ in enumerate(node.functions)]
        len_functions = len(function_res)
        type_parameters_res = ", ".join(
            children_res[len_fields + len_supercls + len_functions:])
        prefix = " " * old_ident
        prefix += (
            "final "
            if node.is_final else ""
        )
        res = "{}{} {}".format(prefix, node.get_class_prefix(), node.name)
        if type_parameters_res:
            res = "{}<{}>".format(res, type_parameters_res)
        superclasses, interfaces = get_superclasses_interfaces()
        if superclasses:
            res += " extends " + ", ".join(superclasses)
        if interfaces:
            if node.class_type == ast.ClassDeclaration.INTERFACE:
                # len(interfaces) should not be more than 1.
                res += " extends " + ", ".join(interfaces)
            else:
                res += " implements " + ", ".join(interfaces)
        body = " {"
        if function_res or field_res or superclasses:
            body += "\n"
            join_separator = "\n" + self.get_ident()
            if field_res:
                body += self.get_ident()
                body += join_separator.join(field_res)
                body += "\n\n"
            if superclasses or field_res:
                body += construct_constructor()
                if function_res:
                    body += "\n\n"
            if function_res:
                body += "\n\n".join(function_res)
            body += "\n" + self.get_ident(extra=-4) + "}"
        else:
            body += "}"
        res += body
        self.ident = old_ident
        return res

    @append_to
    def visit_type_param(self, node):
        return "{name}{bound}".format(
            name=node.name,
            bound=' extends ' + get_type_name(node.bound)
            if node.bound is not None else ''
        )

    @append_to
    def visit_var_decl(self, node):
        prev_cast_number = self._cast_number
        self._cast_number = True
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        var_type = "var"
        # Global variables declared as fields in Main, thus we must specify
        # their type.
        if (node.var_type is not None or
                self._namespace == ast.GLOBAL_NAMESPACE):
            var_type = get_type_name(node.inferred_type)
        main_prefix = self._get_main_prefix('vars', node.name) \
            if self._namespace != ast.GLOBAL_NAMESPACE else ""
        expr = children_res[0].lstrip()
        res = "{ident}{final}{var_type} {main_prefix}{name} = {expr};".format(
            ident=self.get_ident(),
            final="final " if node.is_final else "",
            var_type=var_type,
            main_prefix=main_prefix,
            name=node.name,
            expr=expr
        )
        self._cast_number = prev_cast_number
        return res

    @append_to
    def visit_field_decl(self, node):
        return "public {final}{field_type} {name};".format(
            final="final " if node.is_final else "",
            field_type=get_type_name(node.field_type),
            name=node.name
        )

    @append_to
    def visit_param_decl(self, node):
        res = get_type_name(node.param_type) + " " + node.name
        return res

    @append_to
    @change_namespace
    def visit_func_decl(self, node):
        def is_nested_func():
            parent_namespace = self._namespace[:-2]
            parent_name = self._namespace[-2]
            parent_decl = self.context.get_decl(parent_namespace, parent_name)
            if isinstance(parent_decl, ast.FunctionDeclaration):
                return True
            return False

        if self._inside_is:
            prev_inside_is_function = self._inside_is_function
            self._inside_is_function = True
        old_ident = self.ident
        if (self._namespace[-2],) == ast.GLOBAL_NAMESPACE:
            old_ident += 2
            self.ident += 2
        self.ident += 2
        prev_cast_number = self._cast_number
        children = node.children()
        is_func_non_void_block = self.is_func_non_void_block
        self.is_func_non_void_block = node.get_type() != jt.Void
        is_nested_func_block = self.is_nested_func_block
        self.is_nested_func_block = is_nested_func()
        is_expression = not isinstance(node.body, ast.Block)
        if is_expression:
            self._cast_number = True
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        param_res = [children_res[i] for i, _ in enumerate(node.params)]
        body_res = children_res[-1] if node.body else ''
        body = ""
        if body_res:
            if is_expression:
                if node.get_type() != jt.Void:
                    body_res = ut.add_string_at(
                        body_res, "return ", ut.leading_spaces(body_res))
                body = "{{\n{body};\n{ident}}}".format(
                    body=body_res,
                    ident=self.get_ident(old_ident=old_ident)
                )
            else:
                body = body_res
        if is_nested_func():
            types = list(map(lambda x: x.split()[0], param_res))
            types.append(get_type_name(node.inferred_type, True))
            params = list(map(lambda x: x.split()[1], param_res))
            self._function_interfaces.add(len(params))
            res_t = "{ident}Function{n}<{tp}> {name} = ({params}) -> {body};"
            res = res_t.format(
                ident=self.get_ident(old_ident=old_ident),
                n=len(params),
                tp=", ".join(types),
                name=node.name,
                params=", ".join(params),
                body=body
            )
        else:
            res = ("{ident}{final}{abstract}{ret_type} "
                   "{name}({params}) {body}{semicolon}").format(
                ident=self.get_ident(old_ident=old_ident),
                final="final " if node.is_final else "",
                abstract="abstract " if body == "" else "",
                ret_type=get_type_name(node.inferred_type),
                name=node.name,
                params=", ".join(param_res),
                body=body,
                semicolon=";" if body == "" else ""
            )
        if (self._namespace[-2],) == ast.GLOBAL_NAMESPACE:
            old_ident -= 2
        self.ident = old_ident
        self.is_func_non_void_block = is_func_non_void_block
        self.is_nested_func_block = is_nested_func_block
        self._cast_number = prev_cast_number
        if self._inside_is:
            self._inside_is_function = prev_inside_is_function
        return res

    @append_to
    def visit_integer_constant(self, node):
        def get_cast_literal(integer_type, literal):
            if integer_type == jt.Long:
                return "(long)" + str(literal)
            if integer_type == jt.Short:
                return "(short)" + str(literal)
            if integer_type == jt.Byte:
                return "(byte)" + str(literal)
            if integer_type == jt.Number:
                return "(Number) new Long(" + str(literal) + ")"
            return str(literal)

        if not self._cast_number:
            return "{ident}{literal}{semicolon}".format(
                ident=self.get_ident(),
                literal=str(node.literal),
                semicolon=";" if self._parent_is_block() else ""
            )
        return "{ident}{cast_literal}{semicolon}".format(
            ident=self.get_ident(),
            cast_literal=get_cast_literal(node.integer_type, node.literal),
            semicolon=";" if self._parent_is_block() else ""
        )

    @append_to
    def visit_real_constant(self, node):
        def get_cast_literal(real_type, literal):
            if real_type == jt.Float:
                return "(float)" + str(literal)
            if real_type == jt.Number:
                return "(Number) new Double(" + str(literal) + ")"
            return str(literal)

        if not self._cast_number:
            return "{ident}{literal}{semicolon}".format(
                ident=self.get_ident(),
                literal=str(node.literal),
                semicolon=";" if self._parent_is_block() else ""
            )
        return "{ident}{cast_literal}{semicolon}".format(
            ident=self.get_ident(),
            cast_literal=get_cast_literal(node.real_type, node.literal),
            semicolon=";" if self._parent_is_block() else ""
        )

    @append_to
    def visit_char_constant(self, node):
        return "{ident} '{literal}'{semicolon}".format(
            ident=self.get_ident(),
            literal=node.literal,
            semicolon=";" if self._parent_is_block() else ""
        )

    @append_to
    def visit_string_constant(self, node):
        return "{ident}\"{literal}\"{semicolon}".format(
            ident=self.get_ident(),
            literal=node.literal,
            semicolon=";" if self._parent_is_block() else ""
        )

    @append_to
    def visit_boolean_constant(self, node):
        return "{ident}{literal}{semicolon}".format(
            ident=self.get_ident(),
            literal=str(node.literal),
            semicolon=";" if self._parent_is_block() else ""
        )

    @append_to
    def visit_array_expr(self, node):
        if not node.length:
            return "{ident}new {array}[0]{semicolon}".format(
                ident=self.get_ident(),
                array=get_type_name(node.array_type.type_args[0]),
                semicolon=";" if self._parent_is_block() else ""
            )
        old_ident = self.ident
        prev_cast_number = self._cast_number
        self._cast_number = True
        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        self._cast_number = prev_cast_number
        self.ident = old_ident
        return "{ident}new {etype}{{{exprs}}}{semicolon}".format(
            ident=self.get_ident(),
            exprs=", ".join(children_res),
            etype=get_type_name(node.array_type),
            semicolon=";" if self._parent_is_block() else ""
        )

    @append_to
    def visit_variable(self, node):
        return "{ident}{main_prefix}{name}{semicolon}".format(
            ident=self.get_ident(),
            main_prefix=self._get_main_prefix('vars', node.name),
            name=node.name,
            semicolon=";" if self._parent_is_block() else ""
        )

    @append_to
    def visit_binary_op(self, node):
        old_ident = self.ident
        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        res = "{ident}({left} {operator} {right}){semicolon}".format(
            ident=self.get_ident(old_ident=old_ident),
            left=children_res[0],
            operator=node.operator,
            right=children_res[1],
            semicolon=";" if self._parent_is_block() else ""
        )
        self.ident = old_ident
        return res

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
        prev_inside_is = self._inside_is
        self._inside_is = True
        old_ident = self.ident
        self.ident += 2
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        res = "{ident}(({if_condition}) ?\n{body} : \n {else_body}){semicolon}".format(
            ident=self.get_ident(old_ident=old_ident),
            if_condition=children_res[0].lstrip(),
            body=children_res[1],
            else_body=children_res[2],
            semicolon=";" if self._parent_is_block() else ""
        )
        self.ident = old_ident
        self._inside_is = prev_inside_is
        return res

    @append_to
    def visit_is(self, node):
        old_ident = self.ident
        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        res = "{ident}{not_1}{expr} instanceof {type_to_check}{not_2}".format(
            ident=self.get_ident(old_ident=old_ident),
            not_1="!(",
            expr=children_res[0],
            type_to_check=node.rexpr.get_name(),
            not_2=")")
        self.ident = old_ident
        return res

    @append_to
    def visit_new(self, node):
        old_ident = self.ident
        self.ident = 0
        prev_cast_number = self._cast_number
        self._cast_number = True
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        self.ident = old_ident
        # Remove type arguments from Parameterized Type
        if getattr(node.class_type, 'can_infer_type_args', None) is True:
            cls = node.class_type.name + "<>"
        else:
            cls = get_type_name(node.class_type)
        res = "{ident}new {cls}({args}){semicolon}".format(
            ident=self.get_ident(),
            cls=cls,
            args=", ".join(children_res),
            semicolon=";" if self._parent_is_block() else ""
        )
        self._cast_number = prev_cast_number
        return res

    @append_to
    def visit_field_access(self, node):
        old_ident = self.ident
        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        self.ident = old_ident
        return "{ident}{expr}.{field}{semicolon}".format(
            ident=self.get_ident(),
            expr=children_res[0],
            field=node.field,
            semicolon=";" if self._parent_is_block() else ""
        )

    @append_to
    def visit_func_call(self, node):
        def is_nested_func():
            # From where we are in the AST we search backwards for declarations
            # with the same name.
            decl = get_decl(self.context, self._namespace, node.func)
            # decl[0][-1] is the parent.
            if decl and decl[0][-1] != 'global' and decl[0][-1][0].islower():
                return True
            return False
        old_ident = self.ident
        self.ident = 0
        prev_cast_number = self._cast_number
        self._cast_number = True
        children = node.children()
        for c in children:
            c.accept(self)
        self.ident = old_ident
        children_res = self.pop_children_res(children)
        func = self._get_main_prefix('funcs', node.func) + node.func
        receiver = children_res[0] if node.receiver else None
        args = children_res[1:] if node.receiver else children_res
        res = "{ident}{receiver}{name}{nested}({args}){semicolon}".format(
            ident=self.get_ident(),
            receiver=receiver + "." if receiver else "",
            name=func,
            nested=".apply" if is_nested_func() else "",
            args=", ".join(args),
            semicolon=";" if self._parent_is_block() else ""
        )
        self._cast_number = prev_cast_number
        return res

    @append_to
    def visit_assign(self, node):
        old_ident = self.ident
        self.ident = 0
        prev_cast_number = self._cast_number
        self._cast_number = True
        children = node.children()
        for c in children:
            c.accept(self)
        self.ident = old_ident
        children_res = self.pop_children_res(children)
        name = self._get_main_prefix('vars', node.name) + node.name
        receiver = children_res[0] if node.receiver else None
        expr = children_res[1] if node.receiver else children_res[0]
        res = "{ident}{receiver}{name} = {expr};".format(
            ident=self.get_ident(old_ident=old_ident),
            receiver=receiver + "." if receiver else "",
            name=name,
            expr=expr
        )
        self.ident = old_ident
        self._cast_number = prev_cast_number
        return res
