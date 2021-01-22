from src.ir import ast, types, kotlin_types as kt
from src.ir.context import Context

# class AClass<T>(val x: T) {
#
#     fun foo(): String {
#         return "xxx"
#     }
# }
#
# class BClass
#
# fun bar(y : BClass) {}
#
# fun buz(): BClass {return BClass()}
#
# fun main() {
#     val a = AClass("a")
#     val b: BClass = BClass()
#     bar(BClass())
# }

tp_T = types.TypeParameter("T")
field_x = ast.FieldDeclaration("x", tp_T)
fun_foo = ast.FunctionDeclaration(
    "foo",
    params=[],
    ret_type=kt.String,
    body=ast.Block([ast.StringConstant("xxx")]),
    func_type=ast.FunctionDeclaration.CLASS_METHOD
)
cls_a = ast.ClassDeclaration(
    "AClass",
    [],
    ast.ClassDeclaration.REGULAR,
    fields=[field_x],
    functions=[fun_foo],
    type_parameters=[tp_T]
)
cls_a_str = cls_a.get_type().new([kt.String])

tp_X = types.TypeParameter("X")
tp_Y = types.TypeParameter("Y")
cls_b = ast.ClassDeclaration(
    "BClass",
    [],
    ast.ClassDeclaration.REGULAR,
    fields=[],
    functions=[],
    type_parameters=[tp_X, tp_Y]
)
cls_b_double_integer = cls_b.get_type().new([kt.Double, kt.Integer])
cls_b_any_integer = cls_b.get_type().new([kt.Any, kt.Integer])

y_param = ast.ParameterDeclaration("y", cls_b_double_integer)
fun_bar = ast.FunctionDeclaration(
    "bar",
    params=[y_param],
    ret_type=kt.Unit,
    body=ast.Block([]),
    func_type=ast.FunctionDeclaration.FUNCTION
)

fun_buz = ast.FunctionDeclaration(
    "buz",
    params=[],
    ret_type=cls_b_any_integer,
    body=ast.New(cls_b_any_integer, []),
    func_type=ast.FunctionDeclaration.FUNCTION
)

main_body = ast.Block(
    body=[
        ast.VariableDeclaration(
            "a",
            ast.New(cls_a_str, [ast.StringConstant("a")]),
            inferred_type=cls_a_str
        ),
        ast.VariableDeclaration(
            "b",
            ast.New(cls_b_any_integer, []),
            var_type=cls_b_any_integer
        ),
        ast.FunctionCall(
            "bar",
            [ast.New(cls_b_double_integer, [])]
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
ctx.add_class(ast.GLOBAL_NAMESPACE, "AClass", cls_a)
ctx.add_func(ast.GLOBAL_NAMESPACE + ("AClass",), fun_foo.name, fun_foo)
ctx.add_var(ast.GLOBAL_NAMESPACE + ("AClass",), field_x.name, field_x)
ctx.add_class(ast.GLOBAL_NAMESPACE, "BClass", cls_b)
ctx.add_func(ast.GLOBAL_NAMESPACE, fun_bar.name, fun_bar)
ctx.add_var(ast.GLOBAL_NAMESPACE + ("fun_bar",), y_param.name, y_param)
ctx.add_func(ast.GLOBAL_NAMESPACE, fun_buz.name, fun_buz)
ctx.add_func(ast.GLOBAL_NAMESPACE, main_func.name, main_func)
program = ast.Program(ctx)
