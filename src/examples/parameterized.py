from src.ir.ast import *
from src.ir.kotlin_types import *
from src.ir.context import *


xB_field = FieldDeclaration(
    "x",
    StringType(),
    is_final=True,
    override=False
)

getX_func = FunctionDeclaration(
    "getX",
    params=[
        ParameterDeclaration("z", StringType())
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

foo_func = FunctionDeclaration(
    "foo",
    params=[
        ParameterDeclaration("y", StringType()),
        ParameterDeclaration("z", StringType())
    ],
    ret_type=bam_cls.get_type(),
    func_type=FunctionDeclaration.CLASS_METHOD,
    is_final=False,
    body=Block([
        VariableDeclaration("q", Variable("z"), var_type=StringType()),
        FunctionCall("bar", [Variable("y"), StringConstant("foo"), Variable("q")])
    ])
)

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

a_cls = ClassDeclaration(
    "A",
    superclasses=[],
    class_type=ClassDeclaration.REGULAR,
    is_final=False,
    fields=[xA_field],
    functions=[foo_func, bar_func, buz_func]
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
ctx.add_func(GLOBAL_NAMESPACE, bam_cls.name, bam_cls)
ctx.add_func(GLOBAL_NAMESPACE, main_func.name, main_func)
program = Program(ctx)
