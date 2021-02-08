from src.ir import ast, kotlin_types as kt
from src.ir.context import Context

# open class First {
#     open fun foo() {}
# }
#
# class Second(): First() {
#     override fun foo() {}
# }
#
# fun foo(x: First): First {
#     return x
# }
#
# fun bar() {
#     val y = foo()
#     y.foo()
# }

first_foo = ast.FunctionDeclaration(
    "foo",
    params=[],
    ret_type=kt.Unit,
    body=ast.Block([]),
    func_type=ast.FunctionDeclaration.CLASS_METHOD,
    is_final=False
)
cls_first = ast.ClassDeclaration(
    "First",
    [],
    ast.ClassDeclaration.REGULAR,
    fields=[],
    functions=[first_foo],
    is_final=False
)

second_foo = ast.FunctionDeclaration(
    "foo",
    params=[],
    ret_type=kt.Unit,
    body=ast.Block([]),
    func_type=ast.FunctionDeclaration.CLASS_METHOD,
    is_final=True,
    override=True
)
cls_second = ast.ClassDeclaration(
    "Second",
    [ast.SuperClassInstantiation(cls_first.get_type(), [])],
    ast.ClassDeclaration.REGULAR,
    fields=[],
    functions=[second_foo]
)

foo_x = ast.ParameterDeclaration("x", cls_first.get_type())
fun_foo = ast.FunctionDeclaration(
    "foo",
    params=[foo_x],
    ret_type=cls_first.get_type(),
    body=ast.Variable("x"),
    func_type=ast.FunctionDeclaration.FUNCTION
)


bar_y = ast.VariableDeclaration(
    "y",
    ast.FunctionCall("foo", [ast.New(cls_second.get_type(), [])]),
    inferred_type = cls_first.get_type()
)
fun_bar = ast.FunctionDeclaration(
    "bar",
    params=[],
    ret_type=kt.Unit,
    body=ast.Block([
        bar_y,
        ast.FunctionCall("foo", [], ast.Variable("y")),
    ]),
    func_type=ast.FunctionDeclaration.FUNCTION
)

ctx = Context()
ctx.add_class(ast.GLOBAL_NAMESPACE, "First", cls_first)
ctx.add_func(ast.GLOBAL_NAMESPACE + ("First",), first_foo.name, first_foo)
ctx.add_class(ast.GLOBAL_NAMESPACE, "Second", cls_second)
ctx.add_func(ast.GLOBAL_NAMESPACE + ("Second",), second_foo.name, second_foo)
ctx.add_func(ast.GLOBAL_NAMESPACE, "foo", fun_foo)
ctx.add_var(ast.GLOBAL_NAMESPACE + ("foo",), foo_x.name, foo_x)
ctx.add_func(ast.GLOBAL_NAMESPACE, "bar", fun_bar)
ctx.add_var(ast.GLOBAL_NAMESPACE + ("bar",), bar_y.name, bar_y)
program = ast.Program(ctx, language="kotlin")
