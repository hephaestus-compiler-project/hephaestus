from src.ir import ast, kotlin_types as kt
from src.ir.context import Context

# class A {
#     fun foo(x: String) {
#         val y = if (true) {
#             val z = x
#             x
#         } else "foo"
#     }
#
#     fun bar(x: String) {
#         val y = if (true) {
#             val z = x
#             "bar"
#         } else "foo"
#     }
# }

foo_x = ast.ParameterDeclaration("x", kt.String)
foo_z = ast.VariableDeclaration("z", ast.Variable("x"), var_type=kt.String)
if_cond1 = ast.Conditional(
    ast.BooleanConstant("true"),
    ast.Block([foo_z, ast.Variable("z")]),
    ast.StringConstant("str"),
    kt.String
)
foo_y = ast.VariableDeclaration("y", if_cond1, var_type=kt.String)
fun_body = ast.Block([foo_y])
fun_foo = ast.FunctionDeclaration(
    "foo",
    params=[foo_x],
    ret_type=kt.Unit,
    body=fun_body,
    func_type=ast.FunctionDeclaration.CLASS_METHOD
)


bar_x = ast.ParameterDeclaration("x", kt.String)
bar_z = ast.VariableDeclaration("z", ast.Variable("x"), var_type=kt.String)
if_cond2 = ast.Conditional(
    ast.BooleanConstant("true"),
    ast.Block([bar_z, ast.StringConstant("bar")]),
    ast.StringConstant("foo"),
    kt.String
)
bar_y = ast.VariableDeclaration("y", if_cond2, var_type=kt.String)
fun_body = ast.Block([bar_y])
fun_bar = ast.FunctionDeclaration(
    "bar",
    params=[bar_x],
    ret_type=kt.Unit,
    body=fun_body,
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
ctx.add_func(ast.GLOBAL_NAMESPACE + ("A",), fun_bar.name, fun_bar)
ctx.add_func(ast.GLOBAL_NAMESPACE + ("A",), fun_foo.name, fun_foo)
ctx.add_var(ast.GLOBAL_NAMESPACE + ("A", "foo"), foo_x.name, foo_x)
ctx.add_var(ast.GLOBAL_NAMESPACE + ("A", "foo"), foo_z.name, foo_z)
ctx.add_var(ast.GLOBAL_NAMESPACE + ("A", "foo"), foo_y.name, foo_y)
ctx.add_var(ast.GLOBAL_NAMESPACE + ("A", "bar"), bar_x.name, bar_x)
ctx.add_var(ast.GLOBAL_NAMESPACE + ("A", "bar"), bar_z.name, bar_z)
ctx.add_var(ast.GLOBAL_NAMESPACE + ("A", "bar"), bar_y.name, bar_y)
program = ast.Program(ctx, language="kotlin")
