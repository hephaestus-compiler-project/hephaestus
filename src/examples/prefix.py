from src.ir import ast, kotlin_types as kt
from src.ir.context import Context

# class A (val x: String) {
#
#     fun foo(): String = x
#     fun bar(): String {
#         val z = x
#         val k = z
#     }
# }

field_x = ast.FieldDeclaration("x", kt.String)
fun_foo = ast.FunctionDeclaration(
    "foo",
    params=[],
    ret_type=kt.String,
    body=ast.Variable('x'),
    func_type=ast.FunctionDeclaration.CLASS_METHOD
)
fun_bar = ast.FunctionDeclaration(
    "bar",
    params=[],
    ret_type=kt.Unit,
    body=ast.Block([
        ast.VariableDeclaration("z", ast.Variable("x"), inferred_type= kt.String),
        ast.VariableDeclaration("k", ast.Variable("z"), inferred_type= kt.String)
    ]),
    func_type=ast.FunctionDeclaration.CLASS_METHOD
)
cls = ast.ClassDeclaration(
    "AClass",
    [],
    ast.ClassDeclaration.REGULAR,
    fields=[field_x],
    functions=[fun_foo, fun_bar]
)

main_body = ast.Block(
    body=[
        ast.VariableDeclaration(
            "a",
            ast.New(cls.get_type(), [ast.StringConstant("a")]),
            inferred_type=cls.get_type()
        )
    ]
)
main_func = ast.FunctionDeclaration(
    "main",
    params=[],
    ret_type=kt.Unit,
    func_type=ast.FunctionDeclaration.FUNCTION,
    body=main_body
)


ctx = Context()
ctx.add_class(ast.GLOBAL_NAMESPACE, "AClass", cls)
ctx.add_func(ast.GLOBAL_NAMESPACE + ("AClass",), fun_foo.name, fun_foo)
ctx.add_func(ast.GLOBAL_NAMESPACE + ("AClass",), fun_bar.name, fun_bar)
ctx.add_var(ast.GLOBAL_NAMESPACE + ("AClass",), field_x.name, field_x)
ctx.add_func(ast.GLOBAL_NAMESPACE, main_func.name, main_func)
program = ast.Program(ctx)
