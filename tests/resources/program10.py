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
# fun foo(x: First) {
#     x.foo()
# }
#
# fun bar() {
#     val y: Second = Second()
#     y.foo()
# }
#
# class Third(val z: First) {
#     fun foo() {
#         val k = z
#         z.foo()
#     }
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
    ret_type=kt.Unit,
    body=ast.Block([ast.FunctionCall("foo", [], ast.Variable("x"))]),
    func_type=ast.FunctionDeclaration.FUNCTION
)


bar_y = ast.VariableDeclaration(
    "y",
    ast.New(cls_second.get_type(), []),
    var_type = cls_second.get_type()
)
fun_bar = ast.FunctionDeclaration(
    "bar",
    params=[],
    ret_type=kt.Unit,
    body=ast.Block([
        bar_y,
        ast.FunctionCall("foo", [], ast.Variable("y"))
    ]),
    func_type=ast.FunctionDeclaration.FUNCTION
)

third_z = ast.FieldDeclaration(
        "z",
        cls_first.get_type()
    )
third_foo_k = ast.VariableDeclaration(
    "k",
    ast.Variable("z"),
    inferred_type=third_z.get_type()
)
third_foo = ast.FunctionDeclaration(
    "foo",
    params=[],
    ret_type=kt.Unit,
    body=ast.Block([
        third_foo_k,
        ast.FunctionCall("foo", [], ast.Variable("k"))
    ]),
    func_type=ast.FunctionDeclaration.CLASS_METHOD
)
cls_third = ast.ClassDeclaration(
    "Third",
    [],
    ast.ClassDeclaration.REGULAR,
    fields=[third_z],
    functions=[third_foo],
    is_final=False
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
ctx.add_class(ast.GLOBAL_NAMESPACE, "Third", cls_third)
ctx.add_var(ast.GLOBAL_NAMESPACE + ("Third",), third_z.name, third_z)
ctx.add_func(ast.GLOBAL_NAMESPACE + ("Third",), third_foo.name, third_foo)
ctx.add_var(ast.GLOBAL_NAMESPACE + ("Third", "foo"), third_foo_k.name, third_foo_k)
program = ast.Program(ctx, language="kotlin")
