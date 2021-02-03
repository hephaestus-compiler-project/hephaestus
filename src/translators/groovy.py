# pylint: disable=protected-access
from src.ir import ast, groovy_types as gt
from src.ir.visitors import ASTVisitor
from src.transformations.base import change_namespace


def append_to(visit):
    def inner(self, node):
        res = visit(self, node)
        if (self._namespace == ast.GLOBAL_NAMESPACE and
                isinstance(node, ast.FunctionDeclaration) and
                node.name == "main"):
            self._main_method = res
        elif (self._namespace == ast.GLOBAL_NAMESPACE and
                isinstance(
                    node, (ast.VariableDeclaration, ast.FunctionDeclaration))):
            self._main_children.append(res)
        else:
            self._children_res.append(res)
    return inner


class GroovyTranslator(ASTVisitor):

    filename = "Main.groovy"
    executable = "Main.jar"

    def __init__(self, package=None):
        self._children_res = []
        self.program = None
        self.ident = 0
        self.is_func_block = False
        self.package = package

        self._namespace: tuple = ast.GLOBAL_NAMESPACE
        # We have to add all non-class declarations top-level declarations
        # into a Main static class. Moreover, they should be static and get
        # accessed with `Main.` prefix.
        self._main_children = []
        # main method should be declared public static void, it should be the
        # last element of Main's block.
        self._main_method = None

    @staticmethod
    def get_filename():
        return GroovyTranslator.filename

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

    def visit_program(self, node):
        children = node.children()
        for c in children:
            c.accept(self)
        if self.package:
            package_str = 'package ' + self.package + '\n\n'
        else:
            package_str = ''
        main_cls = "class Main {{\n{}\n{}\n}}".format(
            "\n\n\tstatic ".join(self._main_children) if self._main_children
            else '',
            "public static " + self._main_method if self._main_method else '')
        res = "\n\n".join(self.pop_children_res(children))
        self.program = "{}{}{}".format(
            package_str,
            main_cls,
            "\n\n" + res if res else '')

    @append_to
    def visit_block(self, node):
        children = node.children()
        prev = self.is_func_block
        self.is_func_block = False
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        res = "{\n" + "\n".join(children_res[:-1])
        if children_res[:-1]:
            res += "\n"
        ret_keyword = "return " if prev else ""
        if children_res:
            res += " " * self.ident + ret_keyword + \
                   children_res[-1][self.ident:] + "\n" + \
                   " " * (self.ident - 2) + "}"
        else:
            res += " " * self.ident + ret_keyword + "\n" + \
                   " " * (self.ident - 2) + "}"
        self.is_func_block = prev
        return res

    @append_to
    def visit_super_instantiation(self, node):
        self.ident = 0
        return node.class_type.get_name()

    @append_to
    @change_namespace
    def visit_class_decl(self, node):
        def construct_constructor():
            ident = self.ident + 2
            # TODO handle superclass
            params = [f.field_type.name + ' ' + f.name for f in node.fields]
            constructor_params = ",".join(params)
            # FIXME
            constructor_super = (ident + 2) * " " + "super(" + ",".join(params) + ")"
            fields = ["this." + f.name + ' = ' + f.name for f in node.fields]
            constructor_fields = (ident + 2) * " " + "\n".join(fields)
            return "{}public {}({}) {{\n{}\n{}\n}}".format(
                ident * ' ',
                node.name,
                constructor_params,
                constructor_super,
                constructor_fields
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
        superclasses_res = [children_res[i + len_fields]
                            for i, _ in enumerate(node.superclasses)]
        len_supercls = len(superclasses_res)
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
        if superclasses_res:
            res += " extends " + ", ".join(superclasses_res)
        # TODO check super
        if function_res or field_res:
            body = " {\n"
            spaces = "\n\n" + self.ident * '\t'
            if field_res:
                body += spaces.join(field_res)
            body += "\n\n" + construct_constructor() + "\n\n"
            if function_res:
                body +=  spaces.join(function_res)
            body += "\n" + " " * old_ident + "}"
            res += body
        self.ident = old_ident
        return res

    @append_to
    def visit_type_param(self, node):
        return "{}{}{}{}".format(
            node.variance_to_string(),
            ' ' if node.variance != node.INVARIANT else '',
            node.name,
            ': ' + node.bound.get_name() if node.bound is not None else ''
        )

    @append_to
    def visit_var_decl(self, node):
        old_ident = self.ident
        prefix = " " * self.ident
        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        var_type = "final " if node.is_final else ""
        res = prefix + var_type
        if node.var_type is not None:
            res += " " + node.var_type.get_name()
        res += node.name
        res += " = " + children_res[0]
        self.ident = old_ident
        return res

    @append_to
    def visit_field_decl(self, node):
        prefix = 'final ' if node.is_final else ''
        res = prefix + node.field_type.get_name() + ' ' + node.name
        return res

    @append_to
    def visit_param_decl(self, node):
        res = node.param_type.get_name() + node.name
        return res

    @append_to
    def visit_func_decl(self, node):
        old_ident = self.ident
        self.ident += 2
        children = node.children()
        prev = self.is_func_block
        self.is_func_block = node.get_type() != gt.Void
        is_expression = not isinstance(node.body, ast.Block)
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        param_res = [children_res[i] for i, _ in enumerate(node.params)]
        body_res = children_res[-1] if node.body else ''
        prefix = " " * old_ident
        prefix += "final " if node.is_final else ""
        prefix += "" if not node.override else "override "
        prefix += "" if node.body is not None else "abstract "
        res = prefix + "fun " + node.name + "(" + ", ".join(param_res) + ")"
        if node.ret_type:
            res += ": " + node.ret_type.get_name()
        if body_res:
            sign = "=" if is_expression and node.get_type() != gt.Void else ""
            res += " " + sign + "\n" + body_res
        self.ident = old_ident
        self.is_func_block = prev
        return res

    @append_to
    def visit_integer_constant(self, node):
        return " " * self.ident + str(node.literal)

    @append_to
    def visit_real_constant(self, node):
        return " " * self.ident + str(node.literal)

    @append_to
    def visit_char_constant(self, node):
        return "{}'{}'".format(" " * self.ident, node.literal)

    @append_to
    def visit_string_constant(self, node):
        return '{}"{}"'.format(" " * self.ident, node.literal)

    @append_to
    def visit_boolean_constant(self, node):
        return " " * self.ident + str(node.literal)

    @append_to
    def visit_variable(self, node):
        return " " * self.ident + node.name

    @append_to
    def visit_binary_op(self, node):
        old_ident = self.ident
        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        res = "{}({} {} {})".format(
            " " * old_ident, children_res[0], node.operator,
            children_res[1])
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
        old_ident = self.ident
        self.ident += 2
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        res = "{}(if ({})\n{}\n{}else\n{})".format(
            " " * old_ident, children_res[0][self.ident:], children_res[1],
            " " * old_ident, children_res[2])
        self.ident = old_ident
        return res

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
            node.rexpr.get_name())
        self.ident = old_ident
        return res

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
            return "{}({})".format(
                " " * self.ident + node.class_type.name,
                ", ".join(children_res))
        return "{}({})".format(
            " " * self.ident + node.class_type.get_name(),
            ", ".join(children_res))

    @append_to
    def visit_field_access(self, node):
        old_ident = self.ident
        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        self.ident = old_ident
        res = "{}{}.{}".format(" " * self.ident, children_res[0], node.field)
        return res

    @append_to
    def visit_func_call(self, node):
        old_ident = self.ident
        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)
        self.ident = old_ident
        children_res = self.pop_children_res(children)
        if node.receiver:
            return "{}{}.{}({})".format(
                " " * self.ident, children_res[0], node.func,
                ", ".join(children_res[1:]))
        return "{}{}({})".format(
            " " * self.ident, node.func, ", ".join(children_res))

    @append_to
    def visit_assign(self, node):
        old_ident = self.ident
        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)
        self.ident = old_ident
        children_res = self.pop_children_res(children)
        if node.receiver:
            res = "{}{}.{} = {}".format(" " * old_ident, children_res[0],
                                        node.name, children_res[1])
        else:
            res = "{}{} = {}".format(" " * old_ident, node.name,
                                     children_res[0])
        self.ident = old_ident
        return res
