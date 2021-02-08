from src.ir import ast, kotlin_types as kt
from src.ir.context import Context

# val y = "foo"
# fun foo(x: String) = x
# class A (val x: String) {
#
#     fun bar(): String {
#         val y = x
#         return foo(y)
#     }
#
#     fun baz(): String = y
# }

val_y = ast.VariableDeclaration("y", ast.StringConstant("foo"),
                                var_type=kt.String)
foo_x = ast.ParameterDeclaration("x", kt.String)
fun_foo = ast.FunctionDeclaration(
    "foo",
    params=[foo_x],
    ret_type=kt.String,
    body=ast.Variable("x"),
    func_type=ast.FunctionDeclaration.FUNCTION
)

bar_y = ast.VariableDeclaration("y", ast.Variable("x"), var_type=kt.String)
fun_bar = ast.FunctionDeclaration(
    "bar",
    params=[],
    ret_type=kt.String,
    body=ast.Block([bar_y, ast.FunctionCall("foo", [ast.Variable("y")])]),
    func_type=ast.FunctionDeclaration.CLASS_METHOD
)
fun_baz = ast.FunctionDeclaration(
    "baz",
    params=[],
    ret_type=kt.String,
    body=ast.Variable("y"),
    func_type=ast.FunctionDeclaration.CLASS_METHOD
)

field_x = ast.FieldDeclaration("x", kt.String)
cls = ast.ClassDeclaration(
    "A",
    [],
    ast.ClassDeclaration.REGULAR,
    fields=[field_x],
    functions=[fun_bar, fun_baz]
)


ctx = Context()
ctx.add_class(ast.GLOBAL_NAMESPACE, "A", cls)
ctx.add_func(ast.GLOBAL_NAMESPACE, fun_foo.name, fun_foo)
ctx.add_func(ast.GLOBAL_NAMESPACE, val_y.name, val_y)
ctx.add_func(ast.GLOBAL_NAMESPACE + ("foo",), foo_x.name, foo_x)
ctx.add_func(ast.GLOBAL_NAMESPACE + ("A",), fun_bar.name, fun_bar)
ctx.add_func(ast.GLOBAL_NAMESPACE + ("A",), fun_baz.name, fun_baz)
ctx.add_var(ast.GLOBAL_NAMESPACE + ("A",), field_x.name, field_x)
ctx.add_var(ast.GLOBAL_NAMESPACE + ("A", "bar"), bar_y.name, bar_y)
program = ast.Program(ctx, language="kotlin")
