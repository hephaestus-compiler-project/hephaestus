from src.ir import ast, kotlin_types as kt
from src.ir.context import Context

# class A (val x: String) {
#
#     fun foo(x: String): String = {
#         x.length()
#         x
#     }
# }
foo_x = ast.ParameterDeclaration("x", kt.String)
fun_foo = ast.FunctionDeclaration(
    "foo",
    params=[foo_x],
    ret_type=kt.String,
    body=ast.Block([
        ast.FunctionCall("length", args=[], receiver=ast.Variable("x")),
        ast.Variable("x")
    ]),
    func_type=ast.FunctionDeclaration.CLASS_METHOD
)

cls = ast.ClassDeclaration(
    "A",
    [],
    ast.ClassDeclaration.REGULAR,
    fields=[],
    functions=[fun_foo]
)


ctx = Context()
ctx.add_class(ast.GLOBAL_NAMESPACE, "A", cls)
ctx.add_func(ast.GLOBAL_NAMESPACE + ("A",), fun_foo.name, fun_foo)
ctx.add_var(ast.GLOBAL_NAMESPACE + ("A", "foo",), foo_x.name, foo_x)
program = ast.Program(ctx, language="kotlin")
