from src.ir import kotlin_types as kt
from src.ir.visitors import ASTVisitor


class KotlinTranslator(ASTVisitor):
    # TODO: Add a decorator for bottom-up traversal.

    filename = "program.kt"
    executable = "program.jar"

    def __init__(self):
        self._children_res = []
        self.program = None

    @staticmethod
    def get_filename():
        return Kotlin.filename

    @staticmethod
    def get_executable():
        return Kotlin.executable

    @staticmethod
    def get_cmd_build(filename, executable):
        return ['kotlinc', filename, '-include-runtime', '-d', executable]

    @staticmethod
    def get_cmd_exec(executable):
        return ['java', '-jar', executable]

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
        self.program = '\n'.join(self.pop_children_res(children))
        with open(self.filename, 'w') as f:
            f.write(self.program)

    def visit_block(self, node):
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        res = "{\n  " + "\n  ".join(children_res[:-1])
        res += "\n  return " + children_res[-1] + "\n}"
        self._children_res.append(res)

    def visit_class_decl(self, node):
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        field_res = [children_res[i] for i, _ in enumerate(node.fields)]
        function_res = children_res[len(field_res):]
        if not field_res:
            res = "class " + node.name
        else:
            res = "class " + node.name + "(" + ", ".join(field_res) + ")"
        if node.superclasses:
            res += ": " + ", ".join(map(str, node.superclasses))
        if function_res:
            res += "{\n  " + "\n".join(function_res) + "\n}"
        self._children_res.append(res)

    def visit_var_decl(self, node):
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        res = "val " + node.name + " = " + children_res[0]
        self._children_res.append(res)

    def visit_field_decl(self, node):
        res = "val " + node.name + ": " + node.field_type.name
        self._children_res.append(res)

    def visit_param_decl(self, node):
        res = node.name + ": " + node.param_type.name
        self._children_res.append(res)

    def visit_func_decl(self, node):
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        param_res = [children_res[i] for i, _ in enumerate(node.params)]
        body_res = children_res[-1]
        res = "fun " + node.name + "(" + ", ".join(param_res) + ")"
        if node.ret_type:
            res += ": " + node.ret_type.name
            if isinstance(node.ret_type, kt.UnitType):
                body_res = body_res.replace("return", "")
        res += " " + body_res
        self._children_res.append(res)

    def visit_integer_constant(self, node):
        self._children_res.append(str(node.literal))

    def visit_real_constant(self, node):
        res = node.literal
        if isinstance(node, kt.FloatType):
            res = str(res) + "f"
        self._children_res.append(res)

    def visit_char_constant(self, node):
        self._children_res.append("'{}'".format(node.literal))

    def visit_string_constant(self, node):
        self._children_res.append('"{}"'.format(node.literal))

    def visit_boolean_constant(self, node):
        self._children_res.append(str(node.literal))

    def visit_variable(self, node):
        self._children_res.append(node.name)

    def visit_binary_op(self, node):
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        self._children_res.append(
            children_res[0] + " " + node.operator + " " + children_res[1])

    def visit_logical_expr(self, node):
        self.visit_binary_op(node)

    def visit_equality_expr(self, node):
        self.visit_binary_op(node)

    def visit_comparison_expr(self, node):
        self.visit_binary_op(node)

    def visit_arith_expr(self, node):
        self.visit_binary_op(node)

    def visit_conditional(self, node):
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        res = "if ({}) {} else {}".format(
            children_res[0], children_res[1], children_res[2])
        self._children_res.append(res)

    def visit_new(self, node):
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        self._children_res.append(
            node.class_name + "(" + ", ".join(children_res) + ")")

    def visit_field_access(self, node):
        raise NotImplementedError('visit_field_access() must be implemented')

    def visit_func_call(self, node):
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        self._children_res.append(
            node.func + "(" + ", ".join(children_res) + ")")

    def visit_assign(self, node):
        raise NotImplementedError('visit_assign() must be implemented')
