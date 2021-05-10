from src.ir.ast import *
from src.ir.context import *


def produce_program(lang, types):
    a_a_field = FieldDeclaration("a", types.StringType(), is_final=True)

    param_i = ParameterDeclaration("i", types.String)
    a_foo_clos_s = VariableDeclaration(
        "s", StringConstant("s"), var_type=types.String, is_final=False)
    a_foo_clos = FunctionDeclaration(
        "clos",
        [param_i],
        types.String,
        Block([a_foo_clos_s, Variable("s")]),
        FunctionDeclaration.FUNCTION
    )

    a_foo = FunctionDeclaration(
        "foo",
        [],
        types.Void,
        Block([
            a_foo_clos,
            FunctionCall("println", [FunctionCall("clos", [Variable("a")])])
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

    main_a = VariableDeclaration(
        "a",
        New(a_cls.get_type(), [StringConstant("a")]),
        is_final=False,
        var_type=a_cls.get_type()
    )
    main_fun = FunctionDeclaration(
        "main",
        [],
        types.VoidType(),
        Block([
            main_a,
            FunctionCall("foo", [], Variable("a")),
        ]),
        FunctionDeclaration.FUNCTION
    )


    ctx = Context()
    ctx.add_class(GLOBAL_NAMESPACE, a_cls.name, a_cls)
    ctx.add_var(GLOBAL_NAMESPACE + ('A',), a_a_field.name, a_a_field)
    ctx.add_func(GLOBAL_NAMESPACE + ('A',), a_foo.name, a_foo)
    ctx.add_func(GLOBAL_NAMESPACE + ('A', 'foo'), a_foo_clos.name, a_foo_clos)
    ctx.add_func(GLOBAL_NAMESPACE + ('A', 'foo'), a_foo_clos.name, a_foo_clos)
    ctx.add_func(GLOBAL_NAMESPACE + ('A', 'foo', 'clos'), param_i.name, param_i)
    ctx.add_func(GLOBAL_NAMESPACE + ('A', 'foo', 'clos'), a_foo_clos_s.name, a_foo_clos_s)
    ctx.add_func(GLOBAL_NAMESPACE, main_fun.name, main_fun)
    ctx.add_var(GLOBAL_NAMESPACE + ('main',), main_a.name, main_a)
    program = Program(ctx, language=lang)
    return program
