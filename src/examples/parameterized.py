from src.ir.ast import *
from src.ir.kotlin_types import *
from src.ir.context import *


xB_field = FieldDeclaration(
    "x",
    StringType(),
    is_final=True,
    override=False
)

z_get_param = ParameterDeclaration("z", StringType())
getX_func = FunctionDeclaration(
    "getX",
    params=[
        z_get_param
    ],
    func_type=FunctionDeclaration.CLASS_METHOD,
    is_final=False,
    ret_type=StringType(),
    body=Block([
        Variable(xB_field.name)

    ])
)

bam_cls = ClassDeclaration(
    "Bam",
    superclasses=[],
    class_type=ClassDeclaration.REGULAR,
    is_final=False,
    fields=[xB_field],
    functions=[getX_func]
)

xA_field = FieldDeclaration(
    "x",
    StringType(),
    is_final=True,
    override=False
)

foo_y = ParameterDeclaration("y", StringType())
foo_z = ParameterDeclaration("z", StringType())
foo_q = VariableDeclaration("q", Variable("z"), var_type=StringType())
foo_x = VariableDeclaration("x", Variable("q"), var_type=StringType())
foo_func = FunctionDeclaration(
    "foo",
    params=[foo_y, foo_z],
    ret_type=bam_cls.get_type(),
    func_type=FunctionDeclaration.CLASS_METHOD,
    is_final=False,
    body=Block([
        foo_q,
        foo_x,
        FunctionCall("bar", [Variable("y"), StringConstant("foo"), Variable("q")])
    ])
)

bar_arg = ParameterDeclaration("arg", StringType())
bar_y = ParameterDeclaration("y", StringType())
bar_z = ParameterDeclaration("z", StringType())
bar_func = FunctionDeclaration(
    "bar",
    params=[
        ParameterDeclaration("arg", StringType()),
        ParameterDeclaration("y", StringType()),
        ParameterDeclaration("z", StringType())
    ],
    ret_type=bam_cls.get_type(),
    func_type=FunctionDeclaration.CLASS_METHOD,
    is_final=False,
    body=Block([
        New(bam_cls.get_type(), [Variable("arg")])

    ])
)

buz_func = FunctionDeclaration(
    "buz",
    params=[],
    ret_type=StringType(),
    func_type=FunctionDeclaration.CLASS_METHOD,
    is_final=False,
    body=Block([
        Variable(xA_field.name)
    ])
)

spam_func = FunctionDeclaration(
    "spam",
    params=[],
    ret_type=StringType(),
    func_type=FunctionDeclaration.CLASS_METHOD,
    is_final=False,
    body=Block([
        Conditional(BooleanConstant("true"),
                    Block([Variable(xA_field.name)]),
                    Block([StringConstant("foo")]))
    ])
)

a_cls = ClassDeclaration(
    "A",
    superclasses=[],
    class_type=ClassDeclaration.REGULAR,
    is_final=False,
    fields=[xA_field],
    #  functions=[foo_func, bar_func, buz_func]
    functions=[foo_func, bar_func, buz_func, spam_func]
)

main_body = Block(
    body=[
    ]
)

main_func = FunctionDeclaration(
    "main",
    params=[],
    ret_type=Unit,
    func_type=FunctionDeclaration.FUNCTION,
    body=main_body
)

ctx = Context()
ctx.add_class(GLOBAL_NAMESPACE, a_cls.name, a_cls)
ctx.add_var(GLOBAL_NAMESPACE + ('A',), 'x', xA_field)
ctx.add_var(GLOBAL_NAMESPACE + ('A', 'foo'), 'y', foo_y)
ctx.add_var(GLOBAL_NAMESPACE + ('A', 'foo'), 'z', foo_z)
ctx.add_var(GLOBAL_NAMESPACE + ('A', 'foo'), 'q', foo_q)
ctx.add_var(GLOBAL_NAMESPACE + ('A', 'foo'), 'x', foo_x)
ctx.add_var(GLOBAL_NAMESPACE + ('A', 'bar'), 'arg', bar_arg)
ctx.add_var(GLOBAL_NAMESPACE + ('A', 'bar'), 'y', bar_y)
ctx.add_var(GLOBAL_NAMESPACE + ('A', 'bar'), 'z', bar_z)
ctx.add_func(GLOBAL_NAMESPACE + ('A',), bar_func.name, bar_func)
ctx.add_func(GLOBAL_NAMESPACE + ('A',), foo_func.name, foo_func)
ctx.add_func(GLOBAL_NAMESPACE + ('A',), buz_func.name, buz_func)
ctx.add_func(GLOBAL_NAMESPACE + ('A',), spam_func.name, spam_func)
ctx.add_class(GLOBAL_NAMESPACE, bam_cls.name, bam_cls)
ctx.add_var(GLOBAL_NAMESPACE + ('Bam',), 'x', xB_field)
ctx.add_var(GLOBAL_NAMESPACE + ('Bam', 'getX'), 'z', z_get_param)
ctx.add_func(GLOBAL_NAMESPACE + ('Bam',), getX_func.name, getX_func)
ctx.add_func(GLOBAL_NAMESPACE, main_func.name, main_func)
program = Program(ctx)
