from src.ir.ast import *
from src.ir.kotlin_types import *
from src.ir.types import *
from src.ir.keywords import Keywords


t_generic_type = TypeParameterDecleration("T", TypeParameter.CONTRAVARIANT)

foo_body_generic = Block(body=[])
foo_func_generic = FunctionDeclaration(
    "foo",
    params=[ParameterDeclaration("t", t_generic_type)],
    ret_type=None,
    body=foo_body_generic
)


in_interface = ParameterizedClassDeclaration(
    "In",
    [t_generic_type],
    superclasses=[],
    class_type=ClassDeclaration.INTERFACE,
    fields=[],
    functions=[foo_func_generic]
)


foo_body = Block(body=[])
foo_func = FunctionDeclaration(
    "foo",
    params=[ParameterDeclaration("t", String)],
    ret_type=None,
    body=foo_body,
    keywords=[Keywords.override]
)

in_concrete_type = ConcreteTypeDecleration(in_interface.get_type(), [String])
instring_cls = ClassDeclaration(
    "InString",
    superclasses=[in_concrete_type],
    class_type=ClassDeclaration.REGULAR,
    fields=[],
    functions=[foo_func]
)

s_generic_type = TypeParameterDecleration("S", TypeParameter.CONTRAVARIANT)

select_body=Block(body=["x"])
select_func = ParameterizedFunctionDeclaration(
    "select",
    [s_generic_type.get_type()],
    params=[
        ParameterDeclaration('x', s_generic_type),
        ParameterDeclaration('y', s_generic_type)
    ],
    ret_type=s_generic_type,
    body=select_body
)

any_object = ObjectDecleration("AnyObject")

t2_generic_type = TypeParameterDecleration("T", TypeParameter.INVARIANT)
foo2_body = Block(body=[
    FunctionCall(
        "foo",
        args=[any_object],
        receiver=FunctionCall(
            "select",
            args=[Variable('a'), Variable('a')],
            receiver=None
        )
    )
])
foo2_func = ParameterizedFunctionDeclaration(
    "foo",
    [t2_generic_type.get_type()],
    params=[
        ParameterDeclaration('x', in_concrete_type),
        ParameterDeclaration('y', in_concrete_type)
    ],
    ret_type=None,
    body=foo2_body
)

main_body = Block(
    body=[
        VariableDeclaration(
            "a",
            expr=New("InString", args=[]),
            var_type=None
        ),
        FunctionCall(
            "foo",
            args=[Variable('a'), Variable('a')]
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

print(in_interface)
print(instring_cls)
print(select_func)
print(any_object)
print(foo2_func)
print(main_func)
