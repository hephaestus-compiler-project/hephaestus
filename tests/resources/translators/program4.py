from src.ir import ast, types as tp
from src.ir.context import Context


def produce_program(lang, types):
    tp_T = tp.TypeParameter("T")
    field_x = ast.FieldDeclaration("x", tp_T)
    fun_tmp = ast.FunctionDeclaration(
        "tmp",
        params=[],
        ret_type=types.String,
        body=ast.Block([ast.StringConstant("xxx")]),
        func_type=ast.FunctionDeclaration.CLASS_METHOD
    )
    cls_a = ast.ClassDeclaration(
        "AClass",
        [],
        ast.ClassDeclaration.REGULAR,
        fields=[field_x],
        functions=[fun_tmp],
        type_parameters=[tp_T]
    )
    cls_a_str = cls_a.get_type().new([types.String])
    cls_a_any = cls_a.get_type().new([types.Object])

    tp_X = tp.TypeParameter("X")
    tp_Y = tp.TypeParameter("Y", bound=types.Object)
    cls_b = ast.ClassDeclaration(
        "BClass",
        [],
        ast.ClassDeclaration.REGULAR,
        fields=[],
        functions=[],
        type_parameters=[tp_X, tp_Y]
    )
    cls_b_double_integer = cls_b.get_type().new([types.Double, types.Integer])
    cls_b_any_integer = cls_b.get_type().new([types.Object, types.Integer])

    y_param = ast.ParameterDeclaration("y", cls_b_double_integer)
    fun_bar = ast.FunctionDeclaration(
        "bar",
        params=[y_param],
        ret_type=types.Void,
        body=ast.Block([]),
        func_type=ast.FunctionDeclaration.FUNCTION
    )

    fun_buz = ast.FunctionDeclaration(
        "buz",
        params=[],
        ret_type=cls_b_any_integer,
        body=ast.New(cls_b_any_integer, []),
        func_type=ast.FunctionDeclaration.FUNCTION
    )

    k_param = ast.ParameterDeclaration("k", cls_a_str)
    fun_foo1 = ast.FunctionDeclaration(
        "foo1",
        params=[k_param],
        ret_type=types.Void,
        body=ast.Block([]),
        func_type=ast.FunctionDeclaration.FUNCTION
    )

    n_param = ast.ParameterDeclaration("n", cls_a_any)
    fun_foo2 = ast.FunctionDeclaration(
        "foo2",
        params=[n_param],
        ret_type=types.Void,
        body=ast.Block([]),
        func_type=ast.FunctionDeclaration.FUNCTION
    )

    var_a1 = ast.VariableDeclaration(
            "a1",
            ast.New(cls_a_str, [ast.StringConstant("a1")]),
            inferred_type=cls_a_str
    )
    var_a2 = ast.VariableDeclaration(
            "a2",
            ast.New(cls_a_any, [ast.StringConstant("a2")]),
            inferred_type=cls_a_any
    )
    var_a3 = ast.VariableDeclaration(
            "a3",
            ast.New(cls_a_any, [ast.StringConstant("a3")]),
            inferred_type=cls_a_any
    )
    var_b = ast.VariableDeclaration(
            "b",
            ast.New(cls_b_any_integer, []),
            var_type=cls_b_any_integer
    )
    var_c = ast.VariableDeclaration(
            "c",
            ast.New(cls_b_double_integer, []),
            var_type=cls_b_double_integer
    )
    main_body = ast.Block(
        body=[
            var_a1, var_a2, var_a3, var_b, var_c,
            ast.FunctionCall(
                "bar",
                [ast.Variable('c')]
            ),
            ast.FunctionCall(
                "bar",
                [ast.New(cls_b_double_integer, [])]
            ),
            ast.FunctionCall(
                "foo1",
                [ast.Variable("a1")]
            ),
            ast.FunctionCall(
                "foo2",
                [ast.Variable("a2")]
            ),
        ]
    )
    main_func = ast.FunctionDeclaration(
        "main",
        params=[],
        ret_type=types.Void,
        func_type=ast.FunctionDeclaration.FUNCTION,
        body=main_body,
        is_final=False
    )


    ctx = Context()
    ctx.add_class(ast.GLOBAL_NAMESPACE, "AClass", cls_a)
    ctx.add_func(ast.GLOBAL_NAMESPACE + ("AClass",), fun_tmp.name, fun_tmp)
    ctx.add_var(ast.GLOBAL_NAMESPACE + ("AClass",), field_x.name, field_x)
    ctx.add_class(ast.GLOBAL_NAMESPACE, "BClass", cls_b)
    ctx.add_func(ast.GLOBAL_NAMESPACE, fun_bar.name, fun_bar)
    ctx.add_var(ast.GLOBAL_NAMESPACE + ("bar",), y_param.name, y_param)
    ctx.add_func(ast.GLOBAL_NAMESPACE, fun_buz.name, fun_buz)
    ctx.add_func(ast.GLOBAL_NAMESPACE, fun_foo1.name, fun_foo1)
    ctx.add_var(ast.GLOBAL_NAMESPACE + ("foo1",), k_param.name, k_param)
    ctx.add_func(ast.GLOBAL_NAMESPACE, fun_foo2.name, fun_foo2)
    ctx.add_var(ast.GLOBAL_NAMESPACE + ("foo2",), n_param.name, n_param)
    ctx.add_func(ast.GLOBAL_NAMESPACE, main_func.name, main_func)
    ctx.add_var(ast.GLOBAL_NAMESPACE + ("main",), var_a1.name, var_a1)
    ctx.add_var(ast.GLOBAL_NAMESPACE + ("main",), var_a2.name, var_a2)
    ctx.add_var(ast.GLOBAL_NAMESPACE + ("main",), var_a3.name, var_a3)
    ctx.add_var(ast.GLOBAL_NAMESPACE + ("main",), var_b.name, var_b)
    ctx.add_var(ast.GLOBAL_NAMESPACE + ("main",), var_c.name, var_c)
    program = ast.Program(ctx, language=lang)
    return program
