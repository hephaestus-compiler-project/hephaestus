from src.ir import ast, kotlin_types as kt
from src.ir.context import Context

# class A (val x: String) {
#
#     fun foo(): String {
#         fun bar() = x
#         return bar()
#     }
# }

field_x = ast.FieldDeclaration("x", kt.String)
fun_bar = ast.FunctionDeclaration(
    "bar",
    params=[],
    ret_type=kt.String,
    body=ast.Variable("x"),
    func_type=ast.FunctionDeclaration.FUNCTION
)
fun_foo = ast.FunctionDeclaration(
    "foo",
    params=[],
    ret_type=kt.String,
    body=ast.Block([fun_bar, ast.FunctionCall("bar", [])]),
    func_type=ast.FunctionDeclaration.CLASS_METHOD
)
cls = ast.ClassDeclaration(
    "A",
    [],
    ast.ClassDeclaration.REGULAR,
    fields=[field_x],
    functions=[fun_foo]
)


ctx = Context()
ctx.add_class(ast.GLOBAL_NAMESPACE, "A", cls)
ctx.add_func(ast.GLOBAL_NAMESPACE + ("A",), fun_foo.name, fun_foo)
ctx.add_var(ast.GLOBAL_NAMESPACE + ("A",), field_x.name, field_x)
ctx.add_func(ast.GLOBAL_NAMESPACE + ("A", "foo"), fun_bar.name, fun_bar)
program = ast.Program(ctx, language="kotlin")
