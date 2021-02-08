from src.ir import types as tp, kotlin_types as kt
from src.ir import ast, type_utils as tutils, context as ctx


def test_update_type_builtins():
    new_type = tutils.update_type(kt.Integer, kt.Unit)
    assert new_type == kt.Integer

    new_type = tutils.update_type(kt.Short, tp.SimpleClassifier("A", []))
    assert new_type == kt.Short

    cls_type = tp.SimpleClassifier("A", [])
    new_type = tutils.update_type(cls_type, kt.Integer)
    assert new_type == cls_type


def test_update_type_simple_classifier():
    foo = tp.SimpleClassifier("Foo", [])
    new_type = tp.SimpleClassifier("Foo", [tp.SimpleClassifier("New")])

    new_foo = tutils.update_type(foo, new_type)
    assert new_foo == new_type

    new_type = tp.ParameterizedType(
        tp.TypeConstructor("Foo", [tp.TypeParameter("T")]),
        [kt.String]
    )
    new_foo = tutils.update_type(foo, new_type)
    assert new_foo == new_type


def test_update_type_supertypes():

    foo = tp.SimpleClassifier("Foo", [])
    bar = tp.SimpleClassifier("Bar", [foo])
    baz = tp.SimpleClassifier("Baz", [bar])

    supertypes = baz.get_supertypes()
    assert supertypes == {bar, foo, baz}
    new_type = tp.SimpleClassifier("Foo", [tp.SimpleClassifier("New")])
    new_baz = tutils.update_type(baz, new_type)
    supertypes = new_baz.get_supertypes()
    assert len(supertypes) == 4
    assert new_type in new_baz.get_supertypes()
    assert new_type in bar.get_supertypes()
    assert bar.supertypes == [new_type]


def test_update_type_supertypes_type_con():
    foo = tp.SimpleClassifier("Foo", [])
    bar = tp.SimpleClassifier("Bar", [foo])
    baz_con = tp.TypeConstructor("Baz", [tp.TypeParameter("T")],
                                 supertypes=[bar])
    baz = tp.ParameterizedType(baz_con, [kt.String])
    new_foo = tp.SimpleClassifier("Foo", [tp.SimpleClassifier("New")])

    assert baz.get_supertypes() == {bar, foo, baz}
    new_type = tutils.update_type(baz, new_foo)
    supertypes = new_type.get_supertypes()
    assert len(supertypes) == 4
    assert new_foo in new_type.get_supertypes()


def test_update_type_type_arg():

    foo = tp.SimpleClassifier("Foo", [])

    bar_con = tp.TypeConstructor("Bar", [tp.TypeParameter("T")])
    bar = tp.ParameterizedType(bar_con, [foo])

    baz_con = tp.TypeConstructor("Baz", [tp.TypeParameter("T")])
    baz = tp.ParameterizedType(baz_con, [bar])

    foo_con = tp.TypeConstructor("Foo", [tp.TypeParameter("T")])
    new_foo = tp.ParameterizedType(foo_con, [kt.String])

    new_type = tutils.update_type(baz, new_foo)

    assert isinstance(new_type, tp.ParameterizedType)
    assert len(new_type.type_args) == 1

    assert isinstance(new_type.type_args[0], tp.ParameterizedType)
    assert new_type.type_args[0].name == "Bar"
    assert len(new_type.type_args[0].type_args) == 1
    assert new_type.type_args[0].type_args[0] == new_foo


def test_update_supertypes_type_arg():
    foo = tp.SimpleClassifier("Foo", [])
    bar_con = tp.TypeConstructor("Bar", [tp.TypeParameter("T")])
    bar = tp.ParameterizedType(bar_con, [foo])

    baz_con = tp.TypeConstructor("Baz", [tp.TypeParameter("T")])
    baz = tp.ParameterizedType(baz_con, [bar])

    new_foo = tp.SimpleClassifier("Foo", [tp.SimpleClassifier("New")])

    new_type = tutils.update_type(baz, new_foo)
    assert isinstance(new_type, tp.ParameterizedType)
    assert len(new_type.type_args) == 1

    assert isinstance(new_type.type_args[0], tp.ParameterizedType)
    assert new_type.type_args[0].name == "Bar"
    assert len(new_type.type_args[0].type_args) == 1
    assert new_type.type_args[0].type_args[0] == new_foo


def test_update_bound():
    foo = tp.SimpleClassifier("Foo", [])
    bar_con = tp.TypeConstructor("Bar", [tp.TypeParameter("T", bound=foo)])
    bar = tp.ParameterizedType(bar_con, [foo])
    baz = tp.SimpleClassifier("Baz", [bar])

    new_foo = tp.SimpleClassifier("Foo", [tp.SimpleClassifier("New")])
    new_type = tutils.update_type(baz, new_foo)
    supertypes = new_type.supertypes
    assert len(supertypes) == 1
    assert supertypes[0].name == 'Bar'
    assert supertypes[0].type_args == [new_foo]

    assert len(supertypes[0].t_constructor.type_parameters) == 1
    assert supertypes[0].t_constructor.type_parameters[0].bound == new_foo


def test_update_type_parameter_with_bound():
    foo = tp.SimpleClassifier("Foo", [])
    new_foo = tp.SimpleClassifier("Foo", [tp.SimpleClassifier("New")])

    t_param = tp.TypeParameter("T", bound=None)
    new_t_param = tutils.update_type(t_param, new_foo)

    assert t_param.bound is None

    t_param.bound = foo
    new_t_param = tutils.update_type(t_param, new_foo)

    assert t_param.bound == new_foo


def test_update_bound_supertypes():
    type_param1 = tp.TypeParameter("W")
    type_param2 = tp.TypeParameter("N", bound=kt.Byte)
    type_param3 = tp.TypeParameter("S")

    type_param4 = tp.TypeParameter("T")
    type_param5 = tp.TypeParameter("X")
    type_param6 = tp.TypeParameter("Z")
    foo_con = tp.TypeConstructor(
        "Foo", [type_param4, type_param5, type_param6])
    bar_con = tp.TypeConstructor(
        "Bar", [type_param1, type_param2, type_param3],
        []
    )
    initial_type = bar_con.new([kt.Integer, kt.Byte, kt.String])

    new_bar_con = tp.TypeConstructor(
        "Bar", [type_param1, type_param2, type_param3],
        [foo_con.new([type_param1, type_param2, type_param3])]
    )

    new_type = tutils.update_type(initial_type, new_bar_con)
    assert len(new_type.supertypes) == 1
    assert new_type.supertypes[0].name == 'Foo'
    assert new_type.supertypes[0].type_args == [kt.Integer, kt.Byte, kt.String]
    assert new_type.type_args == [kt.Integer, kt.Byte, kt.String]


def test_find_subtypes():
    foo = tp.SimpleClassifier("Foo", [])
    bar = tp.SimpleClassifier("Bar", [foo])
    baz = tp.SimpleClassifier("Baz", [bar])
    unrel = tp.SimpleClassifier("Unrel", [])
    qux_con = tp.TypeConstructor("Qux", [tp.TypeParameter("T")],
                                 supertypes=[foo])

    subtypes = set(tutils.find_subtypes(foo, [foo, bar, baz, qux_con, unrel]))
    assert subtypes == {bar, baz, qux_con}


def test_find_subtypes_param_type():
    foo = tp.SimpleClassifier("Foo", [])
    bar = tp.SimpleClassifier("Bar", [foo])
    baz = tp.SimpleClassifier("Baz", [bar])
    unrel = tp.SimpleClassifier("Unrel", [])
    qux_con = tp.TypeConstructor("Qux", [tp.TypeParameter("T")],
                                 supertypes=[])
    qux = tp.ParameterizedType(qux_con, [foo])
    subtypes = set(tutils.find_subtypes(qux, [foo, bar, baz, unrel, qux_con]))
    assert subtypes == set()

    fox = tp.SimpleClassifier("Fox", [qux])
    po = tp.SimpleClassifier("Po", [fox])
    subtypes = set(tutils.find_subtypes(qux, [foo, bar, baz, unrel, qux_con,
                                        fox, po]))
    assert subtypes == {fox, po}


def test_find_subtypes_param_type_covariant():
    foo = tp.SimpleClassifier("Foo", [])
    bar = tp.SimpleClassifier("Bar", [foo])
    baz = tp.SimpleClassifier("Baz", [bar])
    unrel = tp.SimpleClassifier("Unrel", [])
    qux_con = tp.TypeConstructor(
        "Qux", [tp.TypeParameter("T", tp.TypeParameter.COVARIANT)],
        supertypes=[])
    qux = tp.ParameterizedType(qux_con, [foo])
    subtypes = set(tutils.find_subtypes(qux, [foo, bar, baz, unrel, qux_con]))
    assert subtypes == {
        tp.ParameterizedType(qux_con, [bar]),
        tp.ParameterizedType(qux_con, [baz])
    }

    fox = tp.SimpleClassifier("Fox", [qux])
    po = tp.SimpleClassifier("Po", [fox])
    subtypes = set(tutils.find_subtypes(qux, [foo, bar, baz, unrel, qux_con,
                                        fox, po]))
    assert subtypes == {fox, po, tp.ParameterizedType(qux_con, [bar]),
                        tp.ParameterizedType(qux_con, [baz])}


def test_find_subtypes_param_type_contravariant():
    new = tp.SimpleClassifier("New", [])
    foo = tp.SimpleClassifier("Foo", [new])
    bar = tp.SimpleClassifier("Bar", [foo])
    baz = tp.SimpleClassifier("Baz", [bar])
    unrel = tp.SimpleClassifier("Unrel", [])
    qux_con = tp.TypeConstructor(
        "Qux", [tp.TypeParameter("T", tp.TypeParameter.CONTRAVARIANT)],
        supertypes=[])
    qux = tp.ParameterizedType(qux_con, [bar])
    subtypes = set(
        tutils.find_subtypes(qux, [foo, bar, baz, unrel, qux_con, new]))
    assert subtypes == {
        tp.ParameterizedType(qux_con, [foo]),
        tp.ParameterizedType(qux_con, [new])
    }

    fox = tp.SimpleClassifier("Fox", [qux])
    po = tp.SimpleClassifier("Po", [fox])
    subtypes = set(tutils.find_subtypes(qux, [foo, bar, baz, unrel, qux_con,
                                        fox, po, new]))
    assert subtypes == {fox, po, tp.ParameterizedType(qux_con, [new]),
                        tp.ParameterizedType(qux_con, [foo])}


def test_find_subtypes_param_type_mul_args():
    new = tp.SimpleClassifier("New", [])
    foo = tp.SimpleClassifier("Foo", [new])
    bar = tp.SimpleClassifier("Bar", [foo])
    baz = tp.SimpleClassifier("Baz", [bar])
    unrel = tp.SimpleClassifier("Unrel", [])

    type_parameters = [
        tp.TypeParameter("T1", tp.TypeParameter.INVARIANT),
        tp.TypeParameter("T2", tp.TypeParameter.CONTRAVARIANT),
        tp.TypeParameter("T3", tp.TypeParameter.COVARIANT)
    ]
    qux_con = tp.TypeConstructor("Qux", type_parameters, supertypes=[])
    qux = tp.ParameterizedType(qux_con, [bar, bar, bar])
    subtypes = set(tutils.find_subtypes(
        qux, [foo, bar, baz, unrel, qux_con, new]))

    expected_subs = {
        tp.ParameterizedType(qux_con, [bar, foo, bar]),
        tp.ParameterizedType(qux_con, [bar, new, bar]),
        tp.ParameterizedType(qux_con, [bar, foo, baz]),
        tp.ParameterizedType(qux_con, [bar, new, baz]),
        tp.ParameterizedType(qux_con, [bar, bar, baz]),
        tp.ParameterizedType(qux_con, [bar, bar, baz]),
    }
    assert subtypes == expected_subs

    fox = tp.SimpleClassifier("Fox", [qux])
    po = tp.SimpleClassifier("Po", [fox])
    subtypes = set(tutils.find_subtypes(qux, [foo, bar, baz, unrel, qux_con,
                                        fox, po, new]))
    assert subtypes == {fox, po}.union(expected_subs)


def test_find_subtypes_param_nested():
    new = tp.SimpleClassifier("New", [])
    foo = tp.SimpleClassifier("Foo", [new])
    bar = tp.SimpleClassifier("Bar", [foo])
    baz = tp.SimpleClassifier("Baz", [bar])
    unrel = tp.SimpleClassifier("Unrel", [])

    qux_con = tp.TypeConstructor(
        "Qux", [tp.TypeParameter("T", tp.TypeParameter.CONTRAVARIANT)])
    qux = tp.ParameterizedType(qux_con, [bar])

    fox = tp.SimpleClassifier("Fox", [qux])
    po = tp.SimpleClassifier("Po", [fox])

    quux_con = tp.TypeConstructor(
        "Quux", [tp.TypeParameter("T", tp.TypeParameter.COVARIANT)])
    quux = tp.ParameterizedType(quux_con, [qux])

    subtypes = set(tutils.find_subtypes(
        quux, [foo, bar, baz, unrel, qux_con, new, po, fox, quux_con]))

    expected_subs = {
        tp.ParameterizedType(quux_con, [po]),
        tp.ParameterizedType(quux_con, [fox]),
        tp.ParameterizedType(quux_con, [tp.ParameterizedType(qux_con, [foo])]),
        tp.ParameterizedType(quux_con, [tp.ParameterizedType(qux_con, [new])]),
    }
    assert subtypes == expected_subs


def test_find_subtypes_param_types():
    foo_con = tp.TypeConstructor(
        "Foo", [tp.TypeParameter("T")], [])
    foo = tp.ParameterizedType(foo_con, [kt.String])

    bar_con = tp.TypeConstructor(
        "Bar", [tp.TypeParameter("T")], supertypes=[foo])

    subtypes = set(tutils.find_subtypes(foo, {foo_con, foo, bar_con}))
    assert subtypes == {bar_con}


def test_find_supertypes():
    foo = tp.SimpleClassifier("Foo", [])
    bar = tp.SimpleClassifier("Bar", [foo])
    baz = tp.SimpleClassifier("Baz", [bar])
    unrel = tp.SimpleClassifier("Unrel", [])

    supertypes = set(tutils.find_supertypes(baz, {unrel, baz, bar, foo}))
    assert supertypes == {bar, foo}

    qux_con = tp.TypeConstructor("Qux", [tp.TypeParameter("T")], [])
    qux = tp.ParameterizedType(qux_con, [kt.String])
    foo.supertypes.append(qux)

    supertypes = set(tutils.find_supertypes(
        baz, {unrel, baz, bar, foo, qux_con}))
    assert supertypes == {bar, foo, qux}


def test_find_supertypes_param_type():
    new = tp.SimpleClassifier("New", [])
    foo = tp.SimpleClassifier("Foo", [new])
    bar = tp.SimpleClassifier("Bar", [foo])
    baz = tp.SimpleClassifier("Baz", [bar])
    unrel = tp.SimpleClassifier("Unrel", [])

    type_parameters = [
        tp.TypeParameter("T1", tp.TypeParameter.INVARIANT),
        tp.TypeParameter("T2", tp.TypeParameter.CONTRAVARIANT),
        tp.TypeParameter("T3", tp.TypeParameter.COVARIANT)
    ]
    qux_con = tp.TypeConstructor("Qux", type_parameters, supertypes=[])
    qux = tp.ParameterizedType(qux_con, [bar, bar, bar])
    supertypes = set(tutils.find_supertypes(
        qux, [foo, bar, baz, unrel, qux_con, new]))

    expected_supers = {
        tp.ParameterizedType(qux_con, [bar, baz, bar]),
        tp.ParameterizedType(qux_con, [bar, baz, foo]),
        tp.ParameterizedType(qux_con, [bar, baz, new]),
        tp.ParameterizedType(qux_con, [bar, bar, foo]),
        tp.ParameterizedType(qux_con, [bar, bar, new]),
    }
    assert supertypes == expected_supers


def test_find_supertypes_nested():
    new = tp.SimpleClassifier("New", [])
    foo = tp.SimpleClassifier("Foo", [new])
    bar = tp.SimpleClassifier("Bar", [foo])
    baz = tp.SimpleClassifier("Baz", [bar])
    unrel = tp.SimpleClassifier("Unrel", [])

    qux_con = tp.TypeConstructor(
        "Qux", [tp.TypeParameter("T", tp.TypeParameter.CONTRAVARIANT)])
    qux = tp.ParameterizedType(qux_con, [bar])

    fox = tp.SimpleClassifier("Fox", [qux])
    po = tp.SimpleClassifier("Po", [fox])

    quux_con = tp.TypeConstructor(
        "Quux", [tp.TypeParameter("T", tp.TypeParameter.COVARIANT)], [qux])
    quux = tp.ParameterizedType(quux_con, [qux])

    supertypes = set(tutils.find_supertypes(
        quux, [foo, bar, baz, unrel, qux_con, new, po, fox, quux_con]))

    expected_supers = {
        qux,
        tp.ParameterizedType(quux_con, [tp.ParameterizedType(qux_con, [baz])]),
    }
    assert supertypes == expected_supers


def test_find_supertypes_bound():
    new = tp.SimpleClassifier("New", [])
    foo = tp.SimpleClassifier("Foo", [new])
    bar = tp.SimpleClassifier("Bar", [foo])
    baz = tp.SimpleClassifier("Baz", [bar])
    unrel = tp.SimpleClassifier("Unrel", [])

    supertypes = set(tutils.find_supertypes(
        baz, {new, foo, bar, baz, unrel}, bound=foo))
    assert supertypes == {bar, foo}


def test_find_subtypes_with_bound():
    new = tp.SimpleClassifier("New", [])
    foo = tp.SimpleClassifier("Foo", [new])
    bar = tp.SimpleClassifier("Bar", [foo])
    baz = tp.SimpleClassifier("Baz", [bar])
    unrel = tp.SimpleClassifier("Unrel", [])
    qux_con = tp.TypeConstructor(
        "Qux", [tp.TypeParameter("T", tp.TypeParameter.CONTRAVARIANT,
                                 bound=foo)], [])
    qux = tp.ParameterizedType(qux_con, [baz])
    subtypes = set(tutils.find_subtypes(
        qux, {new, foo, bar, baz, unrel, qux_con}))
    assert subtypes == {
        tp.ParameterizedType(qux_con, [bar]),
        tp.ParameterizedType(qux_con, [foo])
    }


def test_find_subtypes_with_classes():
    foo = ast.ClassDeclaration("Foo", [], 0)
    bar = ast.ClassDeclaration(
        "Bar", [ast.SuperClassInstantiation(foo.get_type())], 0)
    baz = ast.ClassDeclaration(
        "Baz", [ast.SuperClassInstantiation(bar.get_type())], 0)
    qux = ast.ClassDeclaration("Qux", [], 0)

    subtypes = set(tutils.find_subtypes(
        bar.get_type(), {foo, bar, baz, qux}, include_self=True,
        concrete_only=True))
    assert subtypes == {baz.get_type(), bar.get_type()}


def test_find_types_with_classes():
    foo = ast.ClassDeclaration("Foo", [], ast.ClassDeclaration.REGULAR,
                               fields=[], functions=[])
    bar = ast.ClassDeclaration(
        "Bar", [ast.SuperClassInstantiation(foo.get_type(), [])],
        ast.ClassDeclaration.REGULAR, fields=[], functions=[])
    baz = ast.ClassDeclaration(
        "Baz", [ast.SuperClassInstantiation(bar.get_type(), [])],
        ast.ClassDeclaration.REGULAR, fields=[], functions=[])
    unrel = ast.ClassDeclaration("Unrel", [], ast.ClassDeclaration.REGULAR,
                                 fields=[], functions=[])
    qux_cls = ast.ClassDeclaration(
        "Qux", [], ast.ClassDeclaration.REGULAR, fields=[], functions=[],
        type_parameters=[tp.TypeParameter("T", tp.TypeParameter.COVARIANT)])

    classes = [foo, bar, baz, unrel, qux_cls]

    qux = tp.ParameterizedType(qux_cls.get_type(), [foo.get_type()])
    subtypes = set(tutils.find_subtypes(qux, classes))
    assert subtypes == {
        tp.ParameterizedType(qux_cls.get_type(), [bar.get_type()]),
        tp.ParameterizedType(qux_cls.get_type(), [baz.get_type()])
    }

    subtypes = set(tutils.find_subtypes(foo.get_type(), classes))
    assert subtypes == {bar.get_type(), baz.get_type()}

    supertypes = set(tutils.find_supertypes(foo.get_type(), classes))
    assert supertypes == set()

    supertypes = set(tutils.find_supertypes(baz.get_type(), classes))
    assert supertypes == {bar.get_type(), foo.get_type()}


def test_find_irrelevant_type():
    foo = tp.SimpleClassifier("Foo")
    bar = tp.SimpleClassifier("Bar", [foo])
    baz = tp.SimpleClassifier("Baz", [bar])
    qux = tp.SimpleClassifier("Qux", [])

    ir_type = tutils.find_irrelevant_type(bar, [foo, bar, baz])
    assert ir_type is None

    ir_type = tutils.find_irrelevant_type(bar, [foo, bar, baz, qux])
    assert ir_type == qux


def test_find_irrelevant_type_parameterized():
    foo = tp.SimpleClassifier("Foo")
    bar = tp.SimpleClassifier("Bar", [foo])
    baz = tp.SimpleClassifier("Baz", [bar])
    qux = tp.SimpleClassifier("Qux", [])

    con = tp.TypeConstructor("X", [tp.TypeParameter("T")])
    t = con.new([bar])

    ir_type = tutils.find_irrelevant_type(t, [foo, bar, baz, con])
    assert ir_type is not None
    assert not ir_type.is_subtype(t)
    assert not t.is_subtype(ir_type)

    ir_type = tutils.find_irrelevant_type(t, [foo, bar, baz, qux, con])
    assert ir_type is not None
    assert not ir_type.is_subtype(t)
    assert not t.is_subtype(ir_type)

    con = tp.TypeConstructor(
        "X", [tp.TypeParameter("T", variance=tp.TypeParameter.COVARIANT)])
    t = con.new([bar])
    ir_type = tutils.find_irrelevant_type(t, [foo, bar, baz, con])
    assert ir_type is not None
    assert not ir_type.is_subtype(t)
    assert not t.is_subtype(ir_type)

    ir_type = tutils.find_irrelevant_type(t, [foo, bar, baz, qux, con])
    assert ir_type is not None
    assert not ir_type.is_subtype(t)
    assert not t.is_subtype(ir_type)

    con = tp.TypeConstructor(
        "X", [tp.TypeParameter("T", variance=tp.TypeParameter.CONTRAVARIANT)])
    t = con.new([bar])
    ir_type = tutils.find_irrelevant_type(t, [foo, bar, baz, con])
    assert ir_type is not None
    assert not ir_type.is_subtype(t)
    assert not t.is_subtype(ir_type)

    ir_type = tutils.find_irrelevant_type(t, [foo, bar, baz, qux, con])
    assert ir_type is not None
    assert not ir_type.is_subtype(t)
    assert not t.is_subtype(ir_type)

def test_find_irrelevant_type_parameterized2():
    foo = tp.SimpleClassifier("Foo")
    con = tp.TypeConstructor("X", [tp.TypeParameter("T")])
    t = con.new([foo])
    bar = tp.SimpleClassifier("Bar", [t])

    ir_type = tutils.find_irrelevant_type(t, [foo, con, bar])
    assert ir_type is not None
    assert not ir_type.is_subtype(t)
    assert not t.is_subtype(ir_type)


def test_find_irrelevant_type_parameterized_parent():
    type_param = tp.TypeParameter("T")
    foo = ast.ClassDeclaration("Foo", [], 0)
    bar = ast.ClassDeclaration(
        "Bar", [ast.SuperClassInstantiation(foo.get_type())], 0,
        type_parameters=[type_param]
    )
    baz = ast.ClassDeclaration(
        "Baz", [ast.SuperClassInstantiation(
            bar.get_type().new([foo.get_type()]))], 0)
    qux = ast.ClassDeclaration("Qux", [], 0)

    ir_type = tutils.find_irrelevant_type(baz.get_type(), [foo, bar, baz])
    # TODO
    assert ir_type is not None


def test_find_irrelevant_type_with_given_classes():
    foo = ast.ClassDeclaration("Foo", [], 0)
    bar = ast.ClassDeclaration(
        "Bar", [ast.SuperClassInstantiation(foo.get_type())], 0)
    baz = ast.ClassDeclaration(
        "Baz", [ast.SuperClassInstantiation(bar.get_type())], 0)
    qux = ast.ClassDeclaration("Qux", [], 0)

    ir_type = tutils.find_irrelevant_type(bar.get_type(), [foo, bar, baz])
    assert ir_type is None

    ir_type = tutils.find_irrelevant_type(bar.get_type(), [foo, bar, baz, qux])
    assert ir_type == qux.get_type()


def test_type_hint_constants_and_binary_ops():
    context = ctx.Context()
    expr = ast.IntegerConstant(10, kt.Long)
    assert tutils.get_type_hint(expr, context, tuple()) == kt.Long

    expr = ast.RealConstant("10.9", kt.Float)
    assert tutils.get_type_hint(expr, context, tuple()) == kt.Float

    expr = ast.BooleanConstant("true")
    assert tutils.get_type_hint(expr, context, tuple()) == kt.Boolean

    expr = ast.CharConstant("d")
    assert tutils.get_type_hint(expr, context, tuple()) == kt.Char

    expr = ast.StringConstant("true")
    assert tutils.get_type_hint(expr, context, tuple()) == kt.String

    expr = ast.LogicalExpr(ast.StringConstant("true"),
                           ast.StringConstant("false"),
                           ast.Operator("&&"))
    assert tutils.get_type_hint(expr, context, tuple()) == kt.Boolean


def test_type_hint_variables():
    context = ctx.Context()
    expr = ast.Variable("x")
    assert tutils.get_type_hint(expr, context, tuple()) is None

    decl = ast.VariableDeclaration("x", ast.StringConstant("foo"),
                                   var_type=kt.String)
    context.add_var(ast.GLOBAL_NAMESPACE, decl.name, decl)
    assert tutils.get_type_hint(expr, context, tuple()) is None
    assert tutils.get_type_hint(expr, context, ast.GLOBAL_NAMESPACE) == kt.String


def test_type_hint_new():
    context = ctx.Context()
    expr = ast.New(kt.Any, [])
    assert tutils.get_type_hint(expr, context, tuple()) == kt.Any


def test_type_hint_conditional():
    context = ctx.Context()
    decl = ast.VariableDeclaration("x", ast.StringConstant("foo"),
                                   var_type=kt.String)
    context.add_var(ast.GLOBAL_NAMESPACE, decl.name, decl)
    expr1 = ast.Variable("x")
    expr2 = ast.StringConstant("foo")
    cond1 = ast.Conditional(ast.BooleanConstant("true"), expr1, expr2)
    cond2 = ast.Conditional(ast.BooleanConstant("true"), cond1, expr1)
    cond3 = ast.Conditional(ast.BooleanConstant("true"), cond2, expr2)

    assert tutils.get_type_hint(cond3, context, ast.GLOBAL_NAMESPACE) == kt.String


def test_type_hint_func_call():
    context = ctx.Context()
    func = ast.FunctionDeclaration("func", params=[], ret_type=kt.Unit,
                                   body=None,
                                   func_type=ast.FunctionDeclaration.FUNCTION)
    context.add_func(ast.GLOBAL_NAMESPACE, func.name, func)
    expr = ast.FunctionCall("func", [])
    assert tutils.get_type_hint(expr, context, tuple()) is None
    assert tutils.get_type_hint(expr, context, ast.GLOBAL_NAMESPACE) == kt.Unit


def test_type_hint_func_call_receiver():
    context = ctx.Context()
    func = ast.FunctionDeclaration("func", params=[], ret_type=kt.Integer,
                                   body=None,
                                   func_type=ast.FunctionDeclaration.CLASS_METHOD)
    cls = ast.ClassDeclaration("Foo", [], 0, functions=[func])
    context.add_class(ast.GLOBAL_NAMESPACE, cls.name, cls)
    context.add_func(ast.GLOBAL_NAMESPACE + (cls.name,), func.name, func)

    new_expr = ast.New(cls.get_type(), [])
    decl = ast.VariableDeclaration("x", new_expr,
                                   var_type=cls.get_type())
    context.add_var(ast.GLOBAL_NAMESPACE, decl.name, decl)
    expr1 = ast.Variable("x")
    cond1 = ast.Conditional(ast.BooleanConstant("true"), expr1, new_expr)
    cond2 = ast.Conditional(ast.BooleanConstant("true"), cond1, new_expr)
    cond3 = ast.Conditional(ast.BooleanConstant("true"), cond2, expr1)

    expr = ast.FunctionCall("func", [], cond3)
    assert tutils.get_type_hint(expr, context, tuple()) is None
    assert tutils.get_type_hint(expr, context, ast.GLOBAL_NAMESPACE) == kt.Integer


def test_type_hint_field_access():
    context = ctx.Context()
    field = ast.FieldDeclaration("f", kt.Integer)
    cls = ast.ClassDeclaration("Foo", [], 0, fields=[field])
    context.add_class(ast.GLOBAL_NAMESPACE, cls.name, cls)
    context.add_var(ast.GLOBAL_NAMESPACE + (cls.name,), field.name, field)

    new_expr = ast.New(cls.get_type(), [])
    decl = ast.VariableDeclaration("x", new_expr,
                                   var_type=cls.get_type())
    context.add_var(ast.GLOBAL_NAMESPACE, decl.name, decl)
    expr1 = ast.Variable("x")
    cond1 = ast.Conditional(ast.BooleanConstant("true"), expr1, new_expr)
    cond2 = ast.Conditional(ast.BooleanConstant("true"), cond1, new_expr)
    cond3 = ast.Conditional(ast.BooleanConstant("true"), cond2, expr1)

    expr = ast.FieldAccess(cond3, "f")
    assert tutils.get_type_hint(expr, context, tuple()) is None
    assert tutils.get_type_hint(expr, context, ast.GLOBAL_NAMESPACE) == kt.Integer


def test_type_hint_func_call_inheritance():
    context = ctx.Context()
    func = ast.FunctionDeclaration("func", params=[], ret_type=kt.Integer,
                                   body=None,
                                   func_type=ast.FunctionDeclaration.CLASS_METHOD)
    cls = ast.ClassDeclaration("Foo", [], 0, functions=[func])
    cls2 = ast.ClassDeclaration(
        "Bar", [ast.SuperClassInstantiation(cls.get_type(), [])], 0)
    cls3 = ast.ClassDeclaration(
        "Baz", [ast.SuperClassInstantiation(cls2.get_type(), [])], 0)
    context.add_class(ast.GLOBAL_NAMESPACE, cls.name, cls)
    context.add_class(ast.GLOBAL_NAMESPACE, cls2.name, cls2)
    context.add_class(ast.GLOBAL_NAMESPACE, cls3.name, cls3)
    context.add_func(ast.GLOBAL_NAMESPACE + (cls.name,), func.name, func)

    new_expr = ast.New(cls3.get_type(), [])
    decl = ast.VariableDeclaration("x", new_expr,
                                   var_type=cls3.get_type())
    context.add_var(ast.GLOBAL_NAMESPACE, decl.name, decl)
    expr1 = ast.Variable("x")
    cond1 = ast.Conditional(ast.BooleanConstant("true"), expr1, new_expr)
    cond2 = ast.Conditional(ast.BooleanConstant("true"), cond1, new_expr)
    cond3 = ast.Conditional(ast.BooleanConstant("true"), cond2, expr1)

    expr = ast.FunctionCall("func", [], cond3)
    assert tutils.get_type_hint(expr, context, tuple()) is None
    assert tutils.get_type_hint(expr, context, ast.GLOBAL_NAMESPACE) == kt.Integer


def test_type_hint_field_access_inheritance():
    context = ctx.Context()
    field = ast.FieldDeclaration("f", kt.Integer)
    cls = ast.ClassDeclaration("Foo", [], 0, fields=[field])
    cls2 = ast.ClassDeclaration(
        "Bar", [ast.SuperClassInstantiation(cls.get_type(), [])], 0)
    cls3 = ast.ClassDeclaration(
        "Baz", [ast.SuperClassInstantiation(cls2.get_type(), [])], 0)
    context.add_class(ast.GLOBAL_NAMESPACE, cls.name, cls)
    context.add_class(ast.GLOBAL_NAMESPACE, cls2.name, cls2)
    context.add_class(ast.GLOBAL_NAMESPACE, cls3.name, cls3)
    context.add_var(ast.GLOBAL_NAMESPACE + (cls.name,), field.name, field)

    new_expr = ast.New(cls3.get_type(), [])
    decl = ast.VariableDeclaration("x", new_expr,
                                   var_type=cls3.get_type())
    context.add_var(ast.GLOBAL_NAMESPACE, decl.name, decl)
    expr1 = ast.Variable("x")
    cond1 = ast.Conditional(ast.BooleanConstant("true"), expr1, new_expr)
    cond2 = ast.Conditional(ast.BooleanConstant("true"), cond1, new_expr)
    cond3 = ast.Conditional(ast.BooleanConstant("true"), cond2, expr1)

    expr = ast.FieldAccess(cond3, "f")
    assert tutils.get_type_hint(expr, context, tuple()) is None
    assert tutils.get_type_hint(expr, context, ast.GLOBAL_NAMESPACE) == kt.Integer
