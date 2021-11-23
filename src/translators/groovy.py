# pylint: disable=protected-access,too-many-instance-attributes,too-many-locals
# pylint: disable=too-many-statements
from collections import OrderedDict

from src.ir import ast, groovy_types as gt, types as tp, type_utils as tu
from src.transformations.base import change_namespace
from src.translators.base import BaseTranslator


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


class GroovyTranslator(BaseTranslator):

    filename = "Main.groovy"
    incorrect_filename = "incorrect.groovy"
    executable = "Main.jar"
    ident_value = " "

    def __init__(self, package=None,
                 options={}):
        super().__init__(package, options)
        self.types = []
        self._children_res = []
        self.ident = 0
        self.is_unit = False
        self.context = None
        self._cast_number = False

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
        self.always_cast_numbers = options.get('cast_numbers', False)

        # FIXME remove this option when they fix the bugs
        self.always_cast_ftypes = True

        # A set of numbers where numbers is the number of type parameters that
        # an interface for a function should have.
        # TODO pass it as option, or produce the list during the AST traverse
        self._function_interfaces = {0,1,2,3}

        self._nodes_stack = [None]

    def _reset_state(self):
        # Clear the state
        self.types = []
        self._main_method = ""
        self._main_children = []
        self._inside_is = False
        self._inside_is_function = False
        self.context = None
        self._cast_number = False
        self.ident = 0
        self.is_unit = False
        self._namespace = ast.GLOBAL_NAMESPACE
        self._children_res = []
        self._function_interfaces = {0,1,2,3}
        self._nodes_stack = [None]

    def get_ident(self, extra=0, old_ident=None):
        if old_ident:
            return old_ident * self.ident_value
        return (self.ident + extra) * self.ident_value

    @staticmethod
    def get_filename():
        return GroovyTranslator.filename

    @staticmethod
    def get_incorrect_filename():
        return GroovyTranslator.incorrect_filename

    def type_arg2str(self, t_arg):
        if not isinstance(t_arg, tp.WildCardType):
            return self.get_type_name(t_arg)
        if t_arg.variance == tp.Invariant:
            return "?"
        elif t_arg.variance == tp.Covariant:
            return "? extends " + self.get_type_name(t_arg.bound)
        else:
            return "? super " + self.get_type_name(t_arg.bound)

    def get_type_name(self, t):
        if t.is_wildcard():
            t = t.get_bound_rec()
            return self.get_type_name(t)
        t_constructor = getattr(t, 't_constructor', None)
        if not t_constructor:
            return t.get_name()
        if isinstance(t_constructor, gt.ArrayType):
            return "{}[]".format(self.get_type_name(t.type_args[0]))
        return "{}<{}>".format(t.name, ", ".join([self.type_arg2str(ta)
                                                  for ta in t.type_args]))

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
            type_params = ", ".join(
                ["A" + str(i + 1) if i < number else "R"
                 for i in range(0, number + 1)]
            )
            res += template.format(
                number,
                type_params,
                2 * self.ident_value,
                "R",
                ", ".join(["A" + str(i + 1) + " a" + str(i + 1)
                          for i in range(0, number)]),
            )
        res = "\n\n" + res if res != "" else ""
        return res

    def _parent_is_func_ref(self):
        # The second node is the parent node
        return isinstance(self._nodes_stack[-2], ast.FunctionReference)

    def visit_program(self, node):
        self.types = node.get_types()
        self.context = node.context
        children = node.children()
        for c in children:
            c.accept(self)
        if self.package:
            package_str = 'package ' + self.package + '\n\n'
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
        children_len = len(children)
        for i, c in enumerate(children):
            # Cast return statement if it's a number literal
            if node.is_func_block and not self.is_unit and i == children_len - 1:
                prev_cast_number = self._cast_number
                self._cast_number = False
                c.accept(self)
                self._cast_number = prev_cast_number
            else:
                c.accept(self)
        children_res = self.pop_children_res(children)
        if len(children_res) == 0:  # empty block
            res = "{ }"
        elif len(children_res) == 1:  # single statement
            res = "{{\n{ident}{stmt}\n{old_ident}}}".format(
                ident=self.get_ident(),
                stmt=children_res[0],
                old_ident=self.get_ident(extra=-2)
            )
        else:
            res = "{{\n{stmts}\n{old_ident}}}".format(
                stmts=";\n".join(children_res),
                old_ident=self.get_ident(extra=-2)
            )
        # When block is inside is then it is recognised as closure, thus
        # we must append () to call it.
        if self._inside_is and not self._inside_is_function:
            res += "()"
        return res

    @append_to
    def visit_super_instantiation(self, node):
        return self.get_type_name(node.class_type)

    @append_to
    @change_namespace
    def visit_class_decl(self, node):
        def get_superclasses_interfaces():
            # In correct programs len(superclasses) must be at most 1.
            superclasses = []
            interfaces = []
            for cls_inst in node.superclasses:
                cls_name = cls_inst.class_type.name
                cls_inst = self.get_type_name(cls_inst.class_type)
                cls_decl = self.context.get_classes(
                    self._namespace, glob=True)[cls_name]
                if cls_decl.class_type == ast.ClassDeclaration.INTERFACE:
                    interfaces.append(cls_inst)
                else:
                    superclasses.append(cls_inst)
            return superclasses, interfaces

        def get_constructor_params():
            # Maybe we have to do for the transitive closure
            constructor_fields = OrderedDict()
            for field in node.fields:
                constructor_fields[field.name] = self.get_type_name(
                    field.field_type)
            return constructor_fields

        def construct_constructor():
            params = [tname + ' ' + name
                      for name, tname in
                      get_constructor_params().items()]
            constructor_params = ",".join(params)
            fields = ["this." + f.name + ' = ' + f.name for f in node.fields]
            constructor_fields = "\n" + self.get_ident(extra=2) if fields \
                else ""
            constructor_fields += ("\n" + self.get_ident(extra=2)).join(fields)
            return ("{ident}public {name}({params}) {{{fields}{new_line}"
                    "{close_ident}}}").format(
                ident=self.get_ident(),
                name=node.name,
                params=constructor_params,
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
        if function_res or field_res:
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
            bound=' extends ' + self.get_type_name(node.bound)
            if node.bound is not None else ''
        )

    @append_to
    def visit_var_decl(self, node):
        prev_cast_number = self._cast_number
        self._cast_number = not bool(node.var_type)
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        # Global variables declared as fields in Main, thus we must specify
        # their type.
        var_type = ""
        if (node.var_type is not None or
                self._namespace == ast.GLOBAL_NAMESPACE):
            var_type = self.get_type_name(node.inferred_type) + " "
        main_prefix = self._get_main_prefix('vars', node.name) \
            if self._namespace != ast.GLOBAL_NAMESPACE else ""
        expr = children_res[0].lstrip()
        res = "{ident}{final}{var_type}{main_prefix}{name} = {expr}".format(
            ident=self.get_ident(),
            final="final " if node.is_final else "",
            var_type=var_type or "def ",
            main_prefix=main_prefix,
            name=node.name,
            expr=expr
        )
        self._cast_number = prev_cast_number
        return res

    @append_to
    def visit_call_argument(self, node):
        old_ident = self.ident
        self.ident = 0
        children = node.children()
        for c in node.children():
            c.accept(self)
        self.ident = old_ident
        children_res = self.pop_children_res(children)
        return children_res[0]

    @append_to
    def visit_field_decl(self, node):
        return "public {final}{field_type} {name}".format(
            final="final " if node.is_final else "",
            field_type=self.get_type_name(node.field_type),
            name=node.name
        )

    @append_to
    def visit_param_decl(self, node):
        old_ident = self.ident
        self.ident = 0
        children = node.children()
        for c in node.children():
            c.accept(self)
        self.ident = old_ident
        vararg_str = '...' if node.vararg else ''
        # Recall that varargs ara actually arrays in the signature of
        # the corresponding parameters.
        param_type = (
            node.param_type.type_args[0]
            if node.vararg and isinstance(node.param_type,
                                          tp.ParameterizedType)
            else node.param_type)
        res = self.get_type_name(param_type) + vararg_str + " " + node.name
        if len(children):
            children_res = self.pop_children_res(children)
            res += " = " + children_res[0]
        return res

    @append_to
    @change_namespace
    def visit_func_decl(self, node):
        def is_closure():
            """Return true if we need to declare the function as closure.

            We can declare functions as normal functions only inside classes
            or in the global scope.
            """
            parent_node = self._nodes_stack[-2]
            if parent_node is None:
                return False
            if isinstance(parent_node, ast.ClassDeclaration):
                return False
            return True

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
        prev = self.is_unit
        self.is_unit = node.get_type() == gt.Void
        is_expression = not isinstance(node.body, ast.Block)
        if is_expression:
            self._cast_number = False
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        len_params = len(node.params)
        len_type_params = len(node.type_parameters)
        param_res = [children_res[i] for i, _ in enumerate(node.params)]
        type_parameters_res = ", ".join(
            children_res[len_params:len_type_params + len_params])
        body_res = children_res[-1] if node.body else ''
        body = ""
        if body_res:
            if is_expression:
                body = "{{\n{body}\n{ident}}}".format(
                    body=body_res,
                    ident=self.get_ident(old_ident=old_ident)
                )
            else:
                body = body_res
        if is_closure():
            ret_type = node.get_type()
            ret_type = (ret_type if not ret_type.is_primitive()
                        else ret_type.box_type())
            prefix = (
                "def"
                if not node.ret_type or node.ret_type == gt.Void
                else "Closure<{}>".format(self.get_type_name(ret_type))
            )
            res = "{ident}{prefix} {name} = {{ {params} -> {body}}}".format(
                ident=self.get_ident(old_ident=old_ident),
                prefix=prefix,
                name=node.name,
                params=", ".join(param_res),
                body=body_res
            )
        else:
            res = ("{ident}{final}{abstract}{type_params}{ret_type} "
                   "{name}({params}) {body}").format(
                ident=self.get_ident(old_ident=old_ident),
                final="final " if node.is_final else "",
                abstract="abstract " if body == "" else "",
                type_params=(
                    "<" + type_parameters_res + ">"
                    if type_parameters_res else ""
                ),
                ret_type=self.get_type_name(node.inferred_type),
                name=node.name,
                params=", ".join(param_res),
                body=body
            )
        if (self._namespace[-2],) == ast.GLOBAL_NAMESPACE:
            old_ident -= 2
        self.ident = old_ident
        self.is_unit = prev
        self._cast_number = prev_cast_number
        if self._inside_is:
            self._inside_is_function = prev_inside_is_function
        return res

    def _get_signature(self, node):
        function_type = gt.GroovyBuiltinFactory().get_function_type(
            len(node.params)
        )
        return node.get_signature(function_type)

    @append_to
    @change_namespace
    def visit_lambda(self, node):
        old_ident = self.ident
        if (self._namespace[-2],) == ast.GLOBAL_NAMESPACE:
            old_ident += 2
            self.ident += 2
        self.ident += 2
        prev_cast_number = self._cast_number
        children = node.children()
        prev = self.is_unit
        self.is_unit = node.get_type() == gt.Void
        is_expression = not isinstance(node.body, ast.Block)
        if is_expression:
            self._cast_number = False
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        param_res = [children_res[i] for i, _ in enumerate(node.params)]
        body_res = children_res[-1] if node.body else ''

        ret_type = node.get_type()
        ret_type = (ret_type if not ret_type.is_primitive()
                    else ret_type.box_type())

        cast = ""
        if self.always_cast_ftypes:
            cast = " as " + self.get_type_name(self._get_signature(node))

        res = "{{ {params} -> {body}}} {cast}".format(
            params=", ".join(param_res),
            body=body_res,
            cast=cast
        )

        if (self._namespace[-2],) == ast.GLOBAL_NAMESPACE:
            old_ident -= 2
        self.ident = old_ident
        self.is_unit = prev
        self._cast_number = prev_cast_number
        return res

    @append_to
    def visit_bottom_constant(self, node):
        return self.get_ident() + "{}{}null{}".format(
            '(' if self._parent_is_func_ref() else '',
            '(' + self.get_type_name(node.t) + ') ' if node.t else '',
            ')' if self._parent_is_func_ref() else ''
        )

    @append_to
    def visit_integer_constant(self, node):
        if not self._cast_number and (
                not self.always_cast_numbers and
                node.integer_type.is_primitive()):
            return "{ident}{literal}".format(
                ident=self.get_ident(),
                literal=str(node.literal)
            )
        integer_types = {
            gt.Long: "(Long) ",
            gt.Short: "(Short) ",
            gt.Byte: "(Byte) ",
            gt.Number: "(Number) ",
            gt.BigInteger: "(BigInteger) ",
        }
        cast = integer_types.get(node.integer_type, "")
        return "{ident}{cast}{literal}".format(
            ident=self.get_ident(),
            cast=cast,
            literal=str(node.literal)
        )

    @append_to
    def visit_real_constant(self, node):
        if not self._cast_number and (
                not self.always_cast_numbers and
                node.real_type.is_primitive()):
            return "{ident}{literal}".format(
                ident=self.get_ident(),
                literal=str(node.literal)
            )
        real_types = {
            gt.Double: "(Double) ",
            gt.Float: "(Float) ",
            gt.Number: "(Number) ",
        }
        cast = real_types.get(node.real_type, "")
        return "{ident}{cast}{literal}".format(
            ident=self.get_ident(),
            cast=cast,
            literal=str(node.literal)
        )

    @append_to
    def visit_char_constant(self, node):
        return "{ident}(Character) '{literal}'".format(
            ident=self.get_ident(),
            literal=node.literal
        )

    @append_to
    def visit_string_constant(self, node):
        return "{ident}\"{literal}\"".format(
            ident=self.get_ident(),
            literal=node.literal
        )

    @append_to
    def visit_array_expr(self, node):
        if not node.length:
            return "{ident}new {array}[0]".format(
                ident=self.get_ident(),
                array=self.get_type_name(node.array_type.type_args[0])
            )
        old_ident = self.ident
        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        self.ident = old_ident
        return "{ident}new {etype}{{{exprs}}}".format(
            ident=self.get_ident(),
            exprs=", ".join(children_res),
            etype=self.get_type_name(node.array_type)
        )

    @append_to
    def visit_boolean_constant(self, node):
        return "{ident}{literal}".format(
            ident=self.get_ident(),
            literal=str(node.literal)
        )

    @append_to
    def visit_variable(self, node):
        return "{ident}{main_prefix}{name}".format(
            ident=self.get_ident(),
            main_prefix=self._get_main_prefix('vars', node.name),
            name=node.name
        )

    @append_to
    def visit_binary_op(self, node):
        old_ident = self.ident
        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        res = "{ident}({left} {operator} {right})".format(
            ident=self.get_ident(old_ident=old_ident),
            left=children_res[0],
            operator=node.operator,
            right=children_res[1]
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
        prev_namespace = self._namespace
        self._inside_is = True
        old_ident = self.ident
        self.ident += 2
        children = node.children()
        children[0].accept(self)  # cond
        self._namespace = prev_namespace + ('true_block',)
        children[1].accept(self)  # true branch
        self._namespace = prev_namespace + ('false_block',)
        children[2].accept(self)  # false branch
        self._namespace = prev_namespace
        children_res = self.pop_children_res(children)
        res = "{ident}(({if_condition}) ?\n{body} : \n {else_body})".format(
            ident=self.get_ident(old_ident=old_ident),
            if_condition=children_res[0].lstrip(),
            body=children_res[1],
            else_body=children_res[2]
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
        res = "{ident}{expr} {is_lit} {type_to_check}".format(
            ident=self.get_ident(old_ident=old_ident),
            expr=children_res[0],
            is_lit="!instanceof" if node.operator.is_not else "instanceof",
            type_to_check=self.get_type_name(node.rexpr))
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
            cls = self.get_type_name(node.class_type)
        res = "{ident}new {cls}({args})".format(
            ident=self.get_ident(),
            cls=cls,
            args=", ".join(children_res)
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
        receiver = (
            '({})'.format(children_res[0])
            if isinstance(node.expr, ast.BottomConstant)
            else children_res[0]
        )
        return "{ident}{expr}.{field}".format(
            ident=self.get_ident(),
            expr=receiver,
            field=node.field
        )

    def _get_function_reference_signature(self, func_ref):
        func_name = func_ref.func
        receiver = func_ref.receiver
        receiver_type = None
        if receiver:
            receiver_type = tu.get_type_hint(
                receiver, self.context,
                self._namespace, gt.GroovyBuiltinFactory(),
                self.types
            )
        func_decl = tu.get_func_decl(self.context, func_name, receiver_type)
        if func_decl:
            function_type = gt.GroovyBuiltinFactory().get_function_type(
                len(func_decl.params)
            )
            signature = func_decl.get_signature(function_type)
            return self.get_type_name(signature)
        return None

    @append_to
    def visit_func_ref(self, node):
        old_ident = self.ident

        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)

        self.ident = old_ident

        children_res = self.pop_children_res(children)

        cast = ""
        if self.always_cast_ftypes:
            signature = self.get_type_name(node.get_signature())
            cast = " as " + signature

        receiver = children_res[0] if children_res else "Main"
        receiver += "::" # We can also use .&
        res = "{ident}{receiver}{name}{cast}".format(
            ident=self.get_ident(),
            receiver=receiver,
            name=node.func,
            cast=cast
        )
        return res

    @append_to
    def visit_func_call(self, node):
        old_ident = self.ident
        self.ident = 0
        prev_cast_number = self._cast_number
        self._cast_number = True
        children = node.children()
        for c in children:
            c.accept(self)
        self.ident = old_ident
        children_res = self.pop_children_res(children)
        main_prefix = self._get_main_prefix('funcs', node.func)
        if main_prefix == "":
            main_prefix = self._get_main_prefix('vars', node.func)
        func = main_prefix + node.func
        receiver = children_res[0] if node.receiver else None
        args = children_res[1:] if node.receiver else children_res
        if receiver:
            receiver_expr = (
                '({}).'.format(children_res[0])
                if isinstance(node.receiver, ast.BottomConstant)
                else children_res[0] + '.'
            )
        else:
            receiver_expr = ''
        res = "{ident}{receiver}{name}{apply}({args})".format(
            ident=self.get_ident(),
            receiver=receiver_expr,
            name=func,
            apply=".apply" if node.is_ref_call else "",
            args=", ".join(args)
        )
        self._cast_number = prev_cast_number
        return res

    @append_to
    def visit_assign(self, node):
        old_ident = self.ident
        self.ident = 0
        prev_cast_number = self._cast_number
        self._cast_number = False
        children = node.children()
        for c in children:
            c.accept(self)
        self.ident = old_ident
        children_res = self.pop_children_res(children)
        name = self._get_main_prefix('vars', node.name) + node.name
        receiver = children_res[0] if node.receiver else None
        expr = children_res[1] if node.receiver else children_res[0]
        if receiver:
            receiver_expr = (
                '({}).'.format(children_res[0])
                if isinstance(node.receiver, ast.BottomConstant)
                else children_res[0] + '.'
            )
        else:
            receiver_expr = ''
        res = "{ident}{receiver}{name} = {expr}".format(
            ident=self.get_ident(old_ident=old_ident),
            receiver=receiver_expr,
            name=name,
            expr=expr
        )
        self.ident = old_ident
        self._cast_number = prev_cast_number
        return res
