from src.ir import ast, kotlin_types as kt
from src.ir.visitors import ASTVisitor


class KotlinTranslator(ASTVisitor):
    # TODO: Add a decorator for bottom-up traversal.

    filename = "program.kt"
    executable = "program.jar"

    def __init__(self):
        self._children_res = []
        self.program = None
        self.ident = 0
        self.is_func_block = False
        self._cast_integers = False

    @staticmethod
    def get_filename():
        return KotlinTranslator.filename

    @staticmethod
    def get_executable():
        return KotlinTranslator.executable

    @staticmethod
    def get_cmd_build(filename, executable):
        return ['kotlinc', filename, '-include-runtime', '-d', executable]

    @staticmethod
    def get_cmd_exec(executable):
        return ['java', '-jar', executable]

    def result(self):
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
        self.program = '\n\n'.join(self.pop_children_res(children))

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
            res += " " * self.ident  + ret_keyword + \
                   children_res[-1][self.ident:] + "\n" + \
                   " " * (self.ident - 2) + "}"
        else:
            res += " " * self.ident  + ret_keyword + "\n" + \
                   " " * (self.ident - 2) + "}"
        self.is_func_block = prev
        self._children_res.append(res)

    def visit_super_instantiation(self, node):
        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        if node.args is None:
            self._children_res.append(node.class_type.get_name())
            return
        self._children_res.append(
            node.class_type.get_name() + "(" + ", ".join(children_res) + ")")

    def visit_class_decl(self, node):
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
            "open "
            if not node.is_final and node.class_type != ast.ClassDeclaration.INTERFACE
            else ""
        )
        res = "{}{} {}".format(prefix, node.get_class_prefix(), node.name)
        if type_parameters_res:
            res = "{}<{}>".format(res, type_parameters_res)
        if field_res:
            res = "{}({})".format(
                res, ", ".join(field_res))
        if superclasses_res:
            res += ": " + ", ".join(superclasses_res)
        if function_res:
            res += " {\n" + "\n\n".join(
                function_res) + "\n" + " " * old_ident + "}"
        self.ident = old_ident
        self._children_res.append(res)

    def visit_type_param(self, node):
        self._children_res.append(str(node))

    def visit_var_decl(self, node):
        old_ident = self.ident
        prefix = " " * self.ident
        self.ident = 0
        children = node.children()
        prev = self._cast_integers
        if node.var_type is None:
            self._cast_integers = True
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        var_type = "val " if node.is_final else "var "
        res = prefix + var_type + node.name
        if node.var_type is not None:
            res += ": " + node.var_type.get_name()
        res += " = " + children_res[0]
        self.ident = old_ident
        self._cast_integers = prev
        self._children_res.append(res)

    def visit_field_decl(self, node):
        prefix = '' if node.can_override else 'open '
        prefix += '' if not node.override else 'override '
        prefix += 'val ' if node.is_final else 'var '
        res = prefix + node.name + ": " + node.field_type.get_name()
        self._children_res.append(res)

    def visit_param_decl(self, node):
        res = node.name + ": " + node.param_type.get_name()
        self._children_res.append(res)

    def visit_func_decl(self, node):
        old_ident = self.ident
        self.ident += 2
        children = node.children()
        prev = self.is_func_block
        self.is_func_block = node.get_type() != kt.Unit
        prev_c = self._cast_integers
        is_expression = not isinstance(node.body, ast.Block)
        if is_expression:
            self._cast_integers = True
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        param_res = [children_res[i] for i, _ in enumerate(node.params)]
        body_res = children_res[-1] if node.body else ''
        prefix = " " * old_ident
        prefix += "" if node.is_final else "open "
        prefix += "" if not node.override else "override "
        prefix += "" if node.body is not None else "abstract "
        res = prefix + "fun " + node.name + "(" + ", ".join(param_res) + ")"
        if node.ret_type:
            res += ": " + node.ret_type.get_name()
        if body_res:
            sign = "=" if is_expression and node.get_type() != kt.Unit else ""
            res += " " + sign + "\n" + body_res
        self.ident = old_ident
        self.is_func_block = prev
        self._cast_integers = prev_c
        self._children_res.append(res)

    def visit_integer_constant(self, node):
        if not self._cast_integers:
            self._children_res.append(" " * self.ident + str(node.literal))
            return
        integer_types = {
            kt.Long: ".toLong()",
            kt.Short: ".toShort()",
            kt.Byte: ".toByte()",
        }
        suffix = integer_types.get(node.integer_type, "")
        literal = str(node.literal)
        literal = (
            "(" + literal + ")"
            if suffix and literal[0] == '-'
            else literal
        )
        self._children_res.append(" " * self.ident + literal + suffix)

    def visit_real_constant(self, node):
        self._children_res.append(" " * self.ident + str(node.literal))

    def visit_char_constant(self, node):
        self._children_res.append("{}'{}'".format(
            " " * self.ident, node.literal))

    def visit_string_constant(self, node):
        self._children_res.append('{}"{}"'.format(
            " " * self.ident, node.literal))

    def visit_boolean_constant(self, node):
        self._children_res.append(" " * self.ident + str(node.literal))

    def visit_variable(self, node):
        self._children_res.append(" " * self.ident + node.name)

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
        self._children_res.append(res)

    def visit_logical_expr(self, node):
        self.visit_binary_op(node)

    def visit_equality_expr(self, node):
        prev = self._cast_integers
        # When we encounter equality epxressions,
        # we need to explicitly cast integer literals.
        # Kotlin does not permit operations like the following
        # val d: Short = 1
        # d == 2
        #
        # As a workaround, we can do
        # d == 2.toShort()
        self._cast_integers = True
        self.visit_binary_op(node)
        self._cast_integers = prev

    def visit_comparison_expr(self, node):
        self.visit_binary_op(node)

    def visit_arith_expr(self, node):
        self.visit_binary_op(node)

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
        self._children_res.append(res)

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
        self._children_res.append(res)

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
            self._children_res.append(
                node.class_type.name + "(" + ", ".join(children_res) + ")")
        else:
            self._children_res.append(
                " " * self.ident + node.class_type.get_name() + "(" + ", ".join(
                children_res) + ")")

    def visit_field_access(self, node):
        old_ident = self.ident
        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        self.ident = old_ident
        res = "{}{}.{}".format(" " * self.ident, children_res[0], node.field)
        self._children_res.append(res)

    def visit_func_call(self, node):
        old_ident = self.ident
        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)
        self.ident = old_ident
        children_res = self.pop_children_res(children)
        if node.receiver:
            res = "{}{}.{}({})".format(
                " " * self.ident, children_res[0], node.func,
                ", ".join(children_res[1:]))
        else:
            res = "{}{}({})".format(
                " " * self.ident, node.func, ", ".join(children_res))
        self._children_res.append(res)

    def visit_assign(self, node):
        old_ident = self.ident
        prev = self._cast_integers
        self._cast_integers = True
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
        self._cast_integers = prev
        self._children_res.append(res)
