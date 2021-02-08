from src.ir import ast, kotlin_types as kt
from src.ir.context import Context

# open class First
# class Second(val x: First): First()
#
# fun foo(lank: First): Second =
#     Second(First())
#
# fun bar(): Second {
#     val cinches: Second = foo(First())
#     return cinches
# }

cls_first = ast.ClassDeclaration(
    "First",
    [],
    ast.ClassDeclaration.REGULAR,
    fields=[],
    functions=[],
    is_final=False
)

second_x = ast.FieldDeclaration("x", cls_first.get_type())
cls_second = ast.ClassDeclaration(
    "Second",
    [ast.SuperClassInstantiation(cls_first.get_type(), [])],
    ast.ClassDeclaration.REGULAR,
    fields=[second_x],
    functions=[]
)

foo_lank = ast.ParameterDeclaration("lank", cls_first.get_type())
fun_foo = ast.FunctionDeclaration(
    "foo",
    params=[foo_lank],
    ret_type=cls_second.get_type(),
    body=ast.New(cls_second.get_type(), [ast.Variable("lank")]),
    func_type=ast.FunctionDeclaration.FUNCTION
)


bar_cinches = ast.VariableDeclaration(
    "cinches",
    ast.FunctionCall("foo", [ast.New(cls_first.get_type(), [])]),
    var_type = cls_second.get_type()
)
fun_bar = ast.FunctionDeclaration(
    "bar",
    params=[],
    ret_type=cls_second.get_type(),
    body=ast.Block([
        bar_cinches, ast.Variable("cinches")
    ]),
    func_type=ast.FunctionDeclaration.FUNCTION
)

ctx = Context()
ctx.add_class(ast.GLOBAL_NAMESPACE, "First", cls_first)
ctx.add_class(ast.GLOBAL_NAMESPACE, "Second", cls_second)
ctx.add_class(ast.GLOBAL_NAMESPACE + ("Second",), second_x.name, second_x)
ctx.add_func(ast.GLOBAL_NAMESPACE, "foo", fun_foo)
ctx.add_var(ast.GLOBAL_NAMESPACE + ("foo",), foo_lank.name, foo_lank)
ctx.add_func(ast.GLOBAL_NAMESPACE, "bar", fun_bar)
ctx.add_var(ast.GLOBAL_NAMESPACE + ("bar",), bar_cinches.name, bar_cinches)
program = ast.Program(ctx, language="kotlin")
