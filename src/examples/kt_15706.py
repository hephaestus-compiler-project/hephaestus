from src.ir.ast import *
from src.ir.kotlin_types import *


child_cls = ClassDeclaration(
    "Child",
    superclasses=[],
    class_type=ClassDeclaration.REGULAR,
    fields=[],
    functions=[]
)

test_body=Block(body=[
    VariableDeclaration(
        "child",
        expr=Variable('t'),
        var_type=child_cls.get_type()
    )
])
test_func = FunctionDeclaration(
    "test",
    params=[
        ParameterDeclaration("t", child_cls.get_type())
    ],
    ret_type=Unit,
    func_type=FunctionDeclaration.FUNCTION,
    body=test_body
)

main_body = Block(
    body=[
        FunctionCall(
            "test",
            args=[New(child_cls.get_type(), args=[])]
        )
    ]
)
main_func = FunctionDeclaration(
    "main",
    params=[],
    ret_type=Unit,
    func_type=FunctionDeclaration.FUNCTION,
    body=main_body
)

program = Program(
    declarations=[child_cls, test_func, main_func]
)
