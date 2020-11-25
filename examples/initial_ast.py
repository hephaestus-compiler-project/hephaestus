from src.ir.ast import *
from src.ir.kotlin_types import *


foo_body = Block(body=[])
foo_func = FunctionDeclaration(
    "foo",
    params=[ParameterDeclaration("t", String)],
    ret_type=Unit,
    body=foo_body
)

instring_cls = ClassDeclaration(
    "InString",
    superclasses=[Any],
    class_type=ClassDeclaration.REGULAR,
    fields=[],
    functions=[foo_func]
)

select_body=Body(body=[
    FunctionCall(
        "foo",
        args=[StringConstant("foo")],
        receiver=FunctionCall(
            "select",
            args=[Variable(a), Variable(b)],
            receiver=None
        )
    )
])
select_func = FunctionDeclaration(
    "select",
    params=[
        ParameterDeclaration("x", Classifier(instring_cls.name, instring_cls.superclasses)),
        ParameterDeclaration(x, Classifier(instring_cls.name, instring_cls.superclasses))
    ],
    ret_type=None,
    body=select_body
)

main_body = Body(
    body=[
        VariableDeclaration(
            "a",
            expr=New("InString", args=[]),
            var_type=None
        ),
        FunctionCall(
            "foo",
            args=[Variable(a), Variable(a)]
        )
    ]
)
main_func = FunctionDeclaration(
    "main",
    params=[],
    ret_type=None,
    body=main_body
)

program = Program(
    declarations=[instring_cls, select_func, foo_func, main_func]
)
