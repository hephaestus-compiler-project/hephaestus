from src.ir import kotlin_types as kt
from src.ir.visitors import ASTVisitor


class KotlinTranslator(ASTVisitor):
    # TODO: Add a decorator for bottom-up traversal.

    filename = "program.kt"
    executable = "program.jar"

    def __init__(self):
        self._children_res = []
        self.program = None
        self.ident = 0

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
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        res = "{\n" + "\n".join(children_res[:-1])
        if children_res[:-1]:
            res += "\n"
        res += " " * self.ident  + "return " + \
            children_res[-1][self.ident:] + "\n" + " " * (self.ident - 2) + "}"
        self._children_res.append(res)

    def visit_super_instantiation(self, node):
        old_ident = self.ident
        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        if node.args is None:
            self._children_res.append(node.name)
            return
        self._children_res.append(
            node.name + "(" + ", ".join(children_res) + ")")

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
        function_res = children_res[len_fields + len(superclasses_res):]
        prefix = " " * old_ident
        prefix += "" if node.is_final else "open "
        if not field_res:
            res = prefix + "class " + node.name
        else:
            res = prefix + "class " + node.name + "(" + ", ".join(
                field_res) + ")"
        if superclasses_res:
            res += ": " + ", ".join(superclasses_res)
        if function_res:
            res += " {\n" + "\n\n".join(
                function_res) + "\n" + " " * old_ident + "}"
        self.ident = old_ident
        self._children_res.append(res)

    def visit_var_decl(self, node):
        old_ident = self.ident
        prefix = " " * self.ident
        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        res = prefix + "val " + node.name
        if node.var_type is not None:
            res += ": " + node.var_type.name
        res += " = " + children_res[0]
        self.ident = old_ident
        self._children_res.append(res)

    def visit_field_decl(self, node):
        prefix = '' if node.is_final else 'open '
        prefix += '' if not node.override else 'override '
        res = prefix + "val " + node.name + ": " + node.field_type.name
        self._children_res.append(res)

    def visit_param_decl(self, node):
        res = node.name + ": " + node.param_type.name
        self._children_res.append(res)

    def visit_func_decl(self, node):
        old_ident = self.ident
        self.ident += 2
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        param_res = [children_res[i] for i, _ in enumerate(node.params)]
        body_res = children_res[-1]
        prefix = " " * old_ident
        prefix += "" if node.is_final else "open "
        prefix += "" if not node.override else "override "
        res = prefix + "fun " + node.name + "(" + ", ".join(param_res) + ")"
        if node.ret_type:
            res += ": " + node.ret_type.name
            if isinstance(node.ret_type, kt.UnitType):
                # Remove the last of occurrence of 'return' if the
                # return type of the function is Unit.
                body_res = "".join(body_res.rsplit("return", 1))
        res += " " + body_res
        self.ident = old_ident
        self._children_res.append(res)

    def visit_integer_constant(self, node):
        self._children_res.append(" " * self.ident + str(node.literal))

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
        res = "{}{} {} {}".format(
            " " * old_ident, children_res[0], node.operator,
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

    def visit_conditional(self, node):
        old_ident = self.ident
        self.ident += 2
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        res = "{}if ({})\n{}\n{}else\n{}".format(
            " " * old_ident, children_res[0][self.ident:], children_res[1],
            " " * old_ident, children_res[2])
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
        self._children_res.append(
            " " * self.ident + node.class_name + "(" + ", ".join(
                children_res) + ")")

    def visit_field_access(self, node):
        raise NotImplementedError('visit_field_access() must be implemented')

    def visit_func_call(self, node):
        old_ident = self.ident
        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)
        self.ident = old_ident
        children_res = self.pop_children_res(children)
        self._children_res.append(
            " " * self.ident + node.func + "(" + ", ".join(children_res) + ")")

    def visit_assign(self, node):
        raise NotImplementedError('visit_assign() must be implemented')
