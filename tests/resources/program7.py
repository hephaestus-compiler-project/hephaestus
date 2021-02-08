from src.ir import ast, kotlin_types as kt
from src.ir.context import Context

# val y = "foo"
# class A (val x: String) {
#
#     fun foo(x: String): String = x
#
#     fun bar(): String = foo(y)
# }

val_y = ast.VariableDeclaration("y", ast.StringConstant("foo"),
                                var_type=kt.String)
foo_x = ast.ParameterDeclaration("x", kt.String)
fun_foo = ast.FunctionDeclaration(
    "foo",
    params=[foo_x],
    ret_type=kt.String,
    body=ast.Variable("x"),
    func_type=ast.FunctionDeclaration.CLASS_METHOD
)

fun_bar = ast.FunctionDeclaration(
    "bar",
    params=[],
    ret_type=kt.String,
    body=ast.FunctionCall("foo", [ast.Variable("y")]),
    func_type=ast.FunctionDeclaration.CLASS_METHOD
)
cls = ast.ClassDeclaration(
    "A",
    [],
    ast.ClassDeclaration.REGULAR,
    fields=[],
    functions=[fun_bar, fun_foo]
)


ctx = Context()
ctx.add_class(ast.GLOBAL_NAMESPACE, "A", cls)
ctx.add_var(ast.GLOBAL_NAMESPACE, val_y.name, val_y)
ctx.add_func(ast.GLOBAL_NAMESPACE + ("A",), fun_bar.name, fun_bar)
ctx.add_func(ast.GLOBAL_NAMESPACE + ("A",), fun_foo.name, fun_foo)
ctx.add_var(ast.GLOBAL_NAMESPACE + ("A", "foo",), foo_x.name, foo_x)
program = ast.Program(ctx, language="kotlin")
