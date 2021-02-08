from src.ir.ast import *
from src.ir.groovy_types import *
from src.ir.context import *


a_a_field = FieldDeclaration("a", StringType(), is_final=True)
a_foo = FunctionDeclaration(
    "foo",
    [],
    Void,
    Block([
        FunctionCall("println", [FunctionCall("bar", [Variable("a")])]),
        FunctionCall("println", [FunctionCall("bar", [Variable("z")])])
    ]),
    FunctionDeclaration.CLASS_METHOD,
    is_final=False
)
a_cls = ClassDeclaration(
    "A",
    [],
    ClassDeclaration.REGULAR,
    fields=[a_a_field],
    functions=[a_foo],
    is_final=False
)

var_z = VariableDeclaration("z", StringConstant("z"), var_type=StringType())
var_y = VariableDeclaration("y", StringConstant("y"), var_type=StringType())

param_y = ParameterDeclaration("y", String)
fun_bar = FunctionDeclaration(
    "bar",
    [param_y],
    String,
    ArithExpr(Variable("z"), Variable("y"), Operator('+')),
    FunctionDeclaration.FUNCTION
)

fun_buz = FunctionDeclaration(
    "buz",
    [],
    a_cls.get_type(),
    New(a_cls.get_type(), [StringConstant("a")]),
    FunctionDeclaration.FUNCTION
)

main_a = VariableDeclaration(
    "a",
    New(a_cls.get_type(), [StringConstant("a")]),
    is_final=False,
    var_type=a_cls.get_type()
)
main_fun = FunctionDeclaration(
    "main",
    [],
    VoidType(),
    Block([
        main_a,
        FunctionCall("foo", [], Variable("a")),
        FunctionCall("foo", [], FunctionCall("buz", []))
    ]),
    FunctionDeclaration.FUNCTION
)


ctx = Context()
ctx.add_class(GLOBAL_NAMESPACE, a_cls.name, a_cls)
ctx.add_var(GLOBAL_NAMESPACE + ('A',), a_a_field.name, a_a_field)
ctx.add_func(GLOBAL_NAMESPACE + ('A',), a_foo.name, a_foo)
ctx.add_var(GLOBAL_NAMESPACE, var_z.name, var_z)
ctx.add_var(GLOBAL_NAMESPACE, var_y.name, var_y)
ctx.add_func(GLOBAL_NAMESPACE, fun_bar.name, fun_bar)
ctx.add_var(GLOBAL_NAMESPACE + ('bar',), param_y.name, param_y)
ctx.add_func(GLOBAL_NAMESPACE, fun_buz.name, fun_buz)
ctx.add_func(GLOBAL_NAMESPACE, main_fun.name, main_fun)
ctx.add_var(GLOBAL_NAMESPACE + ('main',), main_a.name, main_a)
program = Program(ctx, language="groovy")
