from src.ir import ast, kotlin_types as kt
from src.ir.context import Context

# class A (val x: String) {
#
#     fun foo(y: String): String {
#         return y
#     }
#
#     fun bar(y: Int): Int {
#         fun baz(): String = x
#         val z = baz()
#         return quz(foo(z))
#     }
#
#     fun quz(y: String): Int = 1
# }

foo_y = ast.ParameterDeclaration("y", kt.String)
foo_body = ast.Variable("y")
foo_fun = ast.FunctionDeclaration(
    "foo",
    params=[foo_y],
    ret_type=kt.String,
    body=foo_body,
    func_type=ast.FunctionDeclaration.CLASS_METHOD
)

bar_y = ast.ParameterDeclaration("y", kt.Integer)
baz_fun = ast.FunctionDeclaration(
    "baz",
    params=[],
    ret_type=kt.String,
    body=ast.Variable("x"),
    func_type=ast.FunctionDeclaration.FUNCTION
)
bar_z = ast.VariableDeclaration("z", ast.FunctionCall("baz", []),
                                var_type=kt.String)

bar_fun = ast.FunctionDeclaration(
    "bar",
    params=[bar_y],
    ret_type=kt.Integer,
    body=ast.Block([
        baz_fun,
        bar_z,
        ast.FunctionCall("quz", [ast.FunctionCall("foo", [ast.Variable("z")])])
    ]),
    func_type=ast.FunctionDeclaration.CLASS_METHOD
)

quz_y = ast.ParameterDeclaration("y", kt.String)
quz_fun = ast.FunctionDeclaration(
    "quz",
    params=[quz_y],
    ret_type=kt.Integer,
    body=ast.IntegerConstant(1, kt.Integer),
    func_type=ast.FunctionDeclaration.CLASS_METHOD
)

field_x = ast.FieldDeclaration("x", kt.String)
cls = ast.ClassDeclaration(
    "A",
    [],
    ast.ClassDeclaration.REGULAR,
    fields=[field_x],
    functions=[foo_fun, bar_fun, quz_fun]
)


ctx = Context()
ctx.add_class(ast.GLOBAL_NAMESPACE, "A", cls)
ctx.add_func(ast.GLOBAL_NAMESPACE + ("A",), foo_fun.name, foo_fun)
ctx.add_func(ast.GLOBAL_NAMESPACE + ("A",), bar_fun.name, bar_fun)
ctx.add_func(ast.GLOBAL_NAMESPACE + ("A",), quz_fun.name, quz_fun)
ctx.add_var(ast.GLOBAL_NAMESPACE + ("A",), field_x.name, field_x)

ctx.add_var(ast.GLOBAL_NAMESPACE + ("A", "foo"), foo_y.name, foo_y)

ctx.add_func(ast.GLOBAL_NAMESPACE + ("A", "bar"), baz_fun.name, baz_fun)
ctx.add_var(ast.GLOBAL_NAMESPACE + ("A", "bar"), bar_y.name, bar_y)
ctx.add_var(ast.GLOBAL_NAMESPACE + ("A", "bar"), bar_z.name, bar_z)

ctx.add_var(ast.GLOBAL_NAMESPACE + ("A", "quz"), quz_y.name, quz_y)
program = ast.Program(ctx, language="kotlin")
