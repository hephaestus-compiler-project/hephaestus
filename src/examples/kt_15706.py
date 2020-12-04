from src.ir.ast import *
from src.ir.kotlin_types import *
from src.ir.context import *


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

ctx = Context()
ctx.add_class(GLOBAL_NAMESPACE, child_cls.name, child_cls)
ctx.add_func(GLOBAL_NAMESPACE, test_func.name, test_func)
ctx.add_func(GLOBAL_NAMESPACE, main_func.name, main_func)
program = Program(ctx)
