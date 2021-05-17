from src.ir.ast import *
from src.ir.groovy_types import *
from src.ir.context import *


def produce_program(lang, types):
    a_a_field = FieldDeclaration("a", types.StringType(), is_final=True)
    a_cls = ClassDeclaration(
        "A",
        [],
        ClassDeclaration.REGULAR,
        [a_a_field],
        is_final=False
    )

    b_a_field = FieldDeclaration(
        "a",
        types.StringType(),
        is_final=True,
        override=True
    )
    b_cls = ClassDeclaration(
        "B",
        [SuperClassInstantiation(a_cls.get_type(), [StringConstant("b")])],
        ClassDeclaration.REGULAR,
        [b_a_field],
        is_final=False
    )

    c_cls = ClassDeclaration("C", [])

    foo_b = VariableDeclaration(
        "b",
        New(b_cls.get_type(), [StringConstant("b")]),
        is_final=False,
        var_type=b_cls.get_type()
    )
    foo_a = VariableDeclaration(
        "ba",
        New(b_cls.get_type(), [StringConstant("ba")]),
        is_final=False,
        var_type=a_cls.get_type()
    )
    main_fun = FunctionDeclaration(
        "main",
        [],
        types.VoidType(),
        Block([foo_b, foo_a]),
        FunctionDeclaration.FUNCTION
    )


    ctx = Context()
    ctx.add_class(GLOBAL_NAMESPACE, a_cls.name, a_cls)
    ctx.add_var(GLOBAL_NAMESPACE + ('A',), a_a_field.name, a_a_field)
    ctx.add_class(GLOBAL_NAMESPACE, b_cls.name, b_cls)
    ctx.add_var(GLOBAL_NAMESPACE + ('B',), b_a_field.name, b_a_field)
    ctx.add_class(GLOBAL_NAMESPACE, c_cls.name, c_cls)
    ctx.add_func(GLOBAL_NAMESPACE, main_fun.name, main_fun)
    ctx.add_var(GLOBAL_NAMESPACE + ('main',), foo_b.name, foo_b)
    ctx.add_var(GLOBAL_NAMESPACE + ('main',), foo_a.name, foo_a)
    program = Program(ctx, language=lang)
    return program
