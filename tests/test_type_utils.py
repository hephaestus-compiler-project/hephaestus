from copy import deepcopy

from src.ir import types as tp, kotlin_types as kt
from src.ir import ast, type_utils as tutils, context as ctx


KT_FACTORY = kt.KotlinBuiltinFactory()


def assert_is_subset(actual, expected):
    if actual:
        assert set(actual).issubset(expected)


def test_update_type_builtins():
    up = tutils.TypeUpdater()
    new_type = up.update_type(kt.Integer, kt.Unit)
    assert new_type == kt.Integer

    new_type = up.update_type(kt.Short, tp.SimpleClassifier("A", []))
    assert new_type == kt.Short

    cls_type = tp.SimpleClassifier("A", [])
    new_type = up.update_type(cls_type, kt.Integer)
    assert new_type == cls_type


def test_update_type_simple_classifier():
    up = tutils.TypeUpdater()
    foo = tp.SimpleClassifier("Foo", [])
    new_type = tp.SimpleClassifier("Foo", [tp.SimpleClassifier("New")])

    new_foo = up.update_type(foo, new_type)
    assert new_foo == new_type

    new_type = tp.ParameterizedType(
        tp.TypeConstructor("Foo", [tp.TypeParameter("T")]),
        [kt.String]
    )
    new_foo = up.update_type(foo, new_type)
    assert new_foo == new_type


def test_update_type_supertypes():

    up = tutils.TypeUpdater()
    foo = tp.SimpleClassifier("Foo", [])
    bar = tp.SimpleClassifier("Bar", [foo])
    baz = tp.SimpleClassifier("Baz", [bar])

    supertypes = baz.get_supertypes()
    assert supertypes == {bar, foo, baz}
    new_type = tp.SimpleClassifier("Foo", [tp.SimpleClassifier("New")])
    new_baz = up.update_type(baz, new_type)
    supertypes = new_baz.get_supertypes()
    assert len(supertypes) == 4
    assert new_type in new_baz.get_supertypes()
    assert new_type in bar.get_supertypes()
    assert bar.supertypes == [new_type]


def test_update_type_supertypes_type_con():
    up = tutils.TypeUpdater()
    foo = tp.SimpleClassifier("Foo", [])
    bar = tp.SimpleClassifier("Bar", [foo])
    baz_con = tp.TypeConstructor("Baz", [tp.TypeParameter("T")],
                                 supertypes=[bar])
    baz = tp.ParameterizedType(baz_con, [kt.String])
    new_foo = tp.SimpleClassifier("Foo", [tp.SimpleClassifier("New")])

    assert baz.get_supertypes() == {bar, foo, baz}
    new_type = up.update_type(baz, new_foo)
    supertypes = new_type.get_supertypes()
    assert len(supertypes) == 4
    assert new_foo in new_type.get_supertypes()


def test_update_type_type_arg():

    up = tutils.TypeUpdater()
    foo = tp.SimpleClassifier("Foo", [])

    bar_con = tp.TypeConstructor("Bar", [tp.TypeParameter("T")])
    bar = tp.ParameterizedType(bar_con, [foo])

    baz_con = tp.TypeConstructor("Baz", [tp.TypeParameter("T")])
    baz = tp.ParameterizedType(baz_con, [bar])

    foo_con = tp.TypeConstructor("Foo", [tp.TypeParameter("T")])
    new_foo = tp.ParameterizedType(foo_con, [kt.String])

    new_type = up.update_type(baz, new_foo)

    assert isinstance(new_type, tp.ParameterizedType)
    assert len(new_type.type_args) == 1

    assert isinstance(new_type.type_args[0], tp.ParameterizedType)
    assert new_type.type_args[0].name == "Bar"
    assert len(new_type.type_args[0].type_args) == 1
    assert new_type.type_args[0].type_args[0] == new_foo


def test_update_supertypes_type_arg():
    up = tutils.TypeUpdater()
    foo = tp.SimpleClassifier("Foo", [])
    bar_con = tp.TypeConstructor("Bar", [tp.TypeParameter("T")])
    bar = tp.ParameterizedType(bar_con, [foo])

    baz_con = tp.TypeConstructor("Baz", [tp.TypeParameter("T")])
    baz = tp.ParameterizedType(baz_con, [bar])

    new_foo = tp.SimpleClassifier("Foo", [tp.SimpleClassifier("New")])

    new_type = up.update_type(baz, new_foo)
    assert isinstance(new_type, tp.ParameterizedType)
    assert len(new_type.type_args) == 1

    assert isinstance(new_type.type_args[0], tp.ParameterizedType)
    assert new_type.type_args[0].name == "Bar"
    assert len(new_type.type_args[0].type_args) == 1
    assert new_type.type_args[0].type_args[0] == new_foo


def test_update_bound():
    up = tutils.TypeUpdater()
    foo = tp.SimpleClassifier("Foo", [])
    bar_con = tp.TypeConstructor("Bar", [tp.TypeParameter("T", bound=foo)])
    bar = tp.ParameterizedType(bar_con, [foo])
    baz = tp.SimpleClassifier("Baz", [bar])

    new_foo = tp.SimpleClassifier("Foo", [tp.SimpleClassifier("New")])
    new_type = up.update_type(baz, new_foo)
    supertypes = new_type.supertypes
    assert len(supertypes) == 1
    assert supertypes[0].name == 'Bar'
    assert supertypes[0].type_args == [new_foo]

    assert len(supertypes[0].t_constructor.type_parameters) == 1
    assert supertypes[0].t_constructor.type_parameters[0].bound == new_foo


def test_update_type_parameter_with_bound():
    up = tutils.TypeUpdater()
    foo = tp.SimpleClassifier("Foo", [])
    new_foo = tp.SimpleClassifier("Foo", [tp.SimpleClassifier("New")])

    t_param = tp.TypeParameter("T", bound=None)
    new_t_param = up.update_type(t_param, new_foo)

    assert t_param.bound is None

    t_param.bound = foo
    new_t_param = up.update_type(t_param, new_foo)

    assert t_param.bound == new_foo


def test_update_type_argument():
    up = tutils.TypeUpdater()
    foo = tp.SimpleClassifier("Foo", [])
    bar = tp.SimpleClassifier("Bar", [foo])
    baz = tp.SimpleClassifier("Baz", [bar])

    targ = tp.WildCardType(foo, tp.Covariant)
    new_foo = tp.SimpleClassifier("Foo", [tp.SimpleClassifier("New")])
    new_targ = up.update_type(targ, new_foo)
    print(new_targ, type(new_targ))

    assert new_targ.bound.name == "Foo"
    assert new_targ.bound == new_foo
    assert new_targ.variance == tp.Covariant


def test_update_bound_supertypes():
    up = tutils.TypeUpdater()
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
    initial_type = bar_con.new([kt.Integer,
                                kt.Byte,
                                kt.String])

    new_bar_con = tp.TypeConstructor(
        "Bar", [type_param1, type_param2, type_param3],
        [foo_con.new([type_param1,
                      type_param2,
                      type_param3])]
    )

    new_type = up.update_type(initial_type, new_bar_con)
    assert len(new_type.supertypes) == 1
    assert new_type.supertypes[0].name == 'Foo'
    assert new_type.supertypes[0].type_args == [
        kt.Integer,
        kt.Byte,
        kt.String
    ]
    assert new_type.type_args == [
        kt.Integer, kt.Byte,
        kt.String]


def test_find_subtypes():
    foo = tp.SimpleClassifier("Foo", [])
    bar = tp.SimpleClassifier("Bar", [foo])
    baz = tp.SimpleClassifier("Baz", [bar])
    unrel = tp.SimpleClassifier("Unrel", [])
    qux_con = tp.TypeConstructor("Qux", [tp.TypeParameter("T")],
                                 supertypes=[foo])

    subtypes = set(tutils.find_subtypes(foo, [foo, bar, baz, qux_con, unrel]))
    assert_is_subset(subtypes, {bar, baz, qux_con})


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
        "Qux", [tp.TypeParameter("T", tp.Covariant)],
        supertypes=[])
    qux = tp.ParameterizedType(qux_con, [foo])
    subtypes = set(tutils.find_subtypes(qux, [foo, bar, baz, unrel, qux_con]))
    assert_is_subset(subtypes, {
        tp.ParameterizedType(qux_con, [bar]),
        tp.ParameterizedType(qux_con, [baz])
    })

    fox = tp.SimpleClassifier("Fox", [qux])
    po = tp.SimpleClassifier("Po", [fox])
    subtypes = set(tutils.find_subtypes(qux, [foo, bar, baz, unrel, qux_con,
                                        fox, po]))
    assert_is_subset(subtypes,
                     {fox, po, tp.ParameterizedType(qux_con,
                                             [bar]),
                      tp.ParameterizedType(qux_con, [baz])})


def test_find_subtypes_param_type_contravariant():
    new = tp.SimpleClassifier("New", [])
    foo = tp.SimpleClassifier("Foo", [new])
    bar = tp.SimpleClassifier("Bar", [foo])
    baz = tp.SimpleClassifier("Baz", [bar])
    unrel = tp.SimpleClassifier("Unrel", [])
    qux_con = tp.TypeConstructor(
        "Qux", [tp.TypeParameter("T", tp.Contravariant)],
        supertypes=[])
    qux = tp.ParameterizedType(qux_con, [bar])
    subtypes = set(
        tutils.find_subtypes(qux, [foo, bar, baz, unrel, qux_con, new]))
    assert_is_subset(subtypes, {
        tp.ParameterizedType(qux_con, [foo]),
        tp.ParameterizedType(qux_con, [new])
    })

    fox = tp.SimpleClassifier("Fox", [qux])
    po = tp.SimpleClassifier("Po", [fox])
    subtypes = set(tutils.find_subtypes(qux, [foo, bar, baz, unrel, qux_con,
                                        fox, po, new]))
    assert_is_subset(subtypes,
                     {fox, po, tp.ParameterizedType(qux_con,
                                             [new]),
                      tp.ParameterizedType(qux_con, [foo])})


def test_find_subtypes_param_type_mul_args():
    new = tp.SimpleClassifier("New", [])
    foo = tp.SimpleClassifier("Foo", [new])
    bar = tp.SimpleClassifier("Bar", [foo])
    baz = tp.SimpleClassifier("Baz", [bar])
    unrel = tp.SimpleClassifier("Unrel", [])

    type_parameters = [
        tp.TypeParameter("T1", tp.Invariant),
        tp.TypeParameter("T2", tp.Contravariant),
        tp.TypeParameter("T3", tp.Covariant)
    ]
    qux_con = tp.TypeConstructor("Qux", type_parameters, supertypes=[])
    qux = tp.ParameterizedType(qux_con, [bar,
                                         bar,
                                         bar])
    subtypes = set(tutils.find_subtypes(
        qux, [foo, bar, baz, unrel, qux_con, new]))

    foo_arg = foo
    bar_arg = bar
    baz_arg = baz
    new_arg = new
    expected_subs = {
        tp.ParameterizedType(qux_con, [bar_arg, foo_arg, bar_arg]),
        tp.ParameterizedType(qux_con, [bar_arg, new_arg, bar_arg]),
        tp.ParameterizedType(qux_con, [bar_arg, foo_arg, baz_arg]),
        tp.ParameterizedType(qux_con, [bar_arg, new_arg, baz_arg]),
        tp.ParameterizedType(qux_con, [bar_arg, bar_arg, baz_arg]),
        tp.ParameterizedType(qux_con, [bar_arg, bar_arg, baz_arg]),
    }
    assert_is_subset(subtypes, expected_subs)

    fox = tp.SimpleClassifier("Fox", [qux])
    po = tp.SimpleClassifier("Po", [fox])
    subtypes = set(tutils.find_subtypes(qux, [foo, bar, baz, unrel, qux_con,
                                        fox, po, new]))
    assert_is_subset(subtypes, {fox, po}.union(expected_subs))


def test_find_subtypes_param_nested():
    new = tp.SimpleClassifier("New", [])
    foo = tp.SimpleClassifier("Foo", [new])
    bar = tp.SimpleClassifier("Bar", [foo])
    baz = tp.SimpleClassifier("Baz", [bar])
    unrel = tp.SimpleClassifier("Unrel", [])

    qux_con = tp.TypeConstructor(
        "Qux", [tp.TypeParameter("T", tp.Contravariant)])
    qux = tp.ParameterizedType(qux_con, [bar])

    fox = tp.SimpleClassifier("Fox", [qux])
    po = tp.SimpleClassifier("Po", [fox])

    quux_con = tp.TypeConstructor(
        "Quux", [tp.TypeParameter("T", tp.Covariant)])
    quux = tp.ParameterizedType(quux_con, [qux])

    subtypes = set(tutils.find_subtypes(
        quux, [foo, bar, baz, unrel, qux_con, new, po, fox, quux_con]))

    expected_subs = {
        tp.ParameterizedType(quux_con, [po]),
        tp.ParameterizedType(quux_con, [fox]),
        tp.ParameterizedType(quux_con,
                             [tp.ParameterizedType(
                                 qux_con, [foo])]),
        tp.ParameterizedType(quux_con,
                             [tp.ParameterizedType(
                                 qux_con, [new])]),
    }
    assert_is_subset(subtypes, expected_subs)


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
        tp.TypeParameter("T1", tp.Invariant),
        tp.TypeParameter("T2", tp.Contravariant),
        tp.TypeParameter("T3", tp.Covariant)
    ]
    qux_con = tp.TypeConstructor("Qux", type_parameters, supertypes=[])
    qux = tp.ParameterizedType(qux_con, [bar,
                                         bar,
                                         bar])
    supertypes = set(tutils.find_supertypes(
        qux, [foo, bar, baz, unrel, qux_con, new]))

    foo = foo
    bar = bar
    baz = baz
    new = new
    expected_supers = {
        tp.ParameterizedType(qux_con, [bar, baz, bar]),
        tp.ParameterizedType(qux_con, [bar, baz, foo]),
        tp.ParameterizedType(qux_con, [bar, baz, new]),
        tp.ParameterizedType(qux_con, [bar, bar, foo]),
        tp.ParameterizedType(qux_con, [bar, bar, new]),
    }
    assert_is_subset(supertypes, expected_supers)


def test_find_supertypes_nested():
    new = tp.SimpleClassifier("New", [])
    foo = tp.SimpleClassifier("Foo", [new])
    bar = tp.SimpleClassifier("Bar", [foo])
    baz = tp.SimpleClassifier("Baz", [bar])
    unrel = tp.SimpleClassifier("Unrel", [])

    qux_con = tp.TypeConstructor(
        "Qux", [tp.TypeParameter("T", tp.Contravariant)])
    qux = tp.ParameterizedType(qux_con, [bar])

    fox = tp.SimpleClassifier("Fox", [qux])
    po = tp.SimpleClassifier("Po", [fox])

    quux_con = tp.TypeConstructor(
        "Quux", [tp.TypeParameter("T", tp.Covariant)], [qux])
    quux = tp.ParameterizedType(quux_con, [qux])

    supertypes = set(tutils.find_supertypes(
        quux, [foo, bar, baz, unrel, qux_con, new, po, fox, quux_con]))

    expected_supers = {
        qux,
        tp.ParameterizedType(quux_con,
                             [tp.ParameterizedType(
                                 qux_con, [baz])]),
    }
    assert_is_subset(supertypes, expected_supers)


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
        "Qux", [tp.TypeParameter("T", tp.Contravariant,
                                 bound=foo)], [])
    qux = tp.ParameterizedType(qux_con, [baz])
    subtypes = set(tutils.find_subtypes(
        qux, {new, foo, bar, baz, unrel, qux_con}))
    assert_is_subset(subtypes, {
        tp.ParameterizedType(qux_con, [bar]),
        tp.ParameterizedType(qux_con, [foo])
    })


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
        type_parameters=[tp.TypeParameter("T", tp.Covariant)])

    classes = [foo, bar, baz, unrel, qux_cls]

    qux = tp.ParameterizedType(qux_cls.get_type(),
                               [foo.get_type()])
    subtypes = set(tutils.find_subtypes(qux, classes))
    assert_is_subset(subtypes, {
        tp.ParameterizedType(qux_cls.get_type(),
                             [bar.get_type()]),
        tp.ParameterizedType(qux_cls.get_type(),
                             [baz.get_type()])
    })

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

    ir_type = tutils.find_irrelevant_type(bar, [foo, bar, baz], KT_FACTORY)
    assert ir_type is None

    ir_type = tutils.find_irrelevant_type(bar, [foo, bar, baz, qux],
                                          KT_FACTORY)
    assert ir_type == qux


def test_find_irrelevant_type_parameterized():
    foo = tp.SimpleClassifier("Foo")
    bar = tp.SimpleClassifier("Bar", [foo])
    baz = tp.SimpleClassifier("Baz", [bar])
    qux = tp.SimpleClassifier("Qux", [])

    con = tp.TypeConstructor("X", [tp.TypeParameter("T")])
    t = con.new([bar])

    ir_type = tutils.find_irrelevant_type(t, [foo, bar, baz, con], KT_FACTORY)
    assert ir_type is not None
    assert not ir_type.is_subtype(t)
    assert not t.is_subtype(ir_type)

    ir_type = tutils.find_irrelevant_type(t, [foo, bar, baz, qux, con],
                                          KT_FACTORY)
    assert ir_type is not None
    assert not ir_type.is_subtype(t)
    assert not t.is_subtype(ir_type)

    con = tp.TypeConstructor(
        "X", [tp.TypeParameter("T", variance=tp.Covariant)])
    t = con.new([bar])
    ir_type = tutils.find_irrelevant_type(t, [foo, bar, baz, con], KT_FACTORY)
    assert ir_type is not None
    assert not ir_type.is_subtype(t)
    assert not t.is_subtype(ir_type)

    ir_type = tutils.find_irrelevant_type(t, [foo, bar, baz, qux, con],
                                          KT_FACTORY)
    assert ir_type is not None
    assert not ir_type.is_subtype(t)
    assert not t.is_subtype(ir_type)

    con = tp.TypeConstructor(
        "X", [tp.TypeParameter("T", variance=tp.Contravariant)])
    t = con.new([bar])
    ir_type = tutils.find_irrelevant_type(t, [foo, bar, baz, con], KT_FACTORY)
    assert ir_type is not None
    assert not ir_type.is_subtype(t)
    assert not t.is_subtype(ir_type)

    ir_type = tutils.find_irrelevant_type(t, [foo, bar, baz, qux, con],
                                          KT_FACTORY)
    assert ir_type is not None
    assert not ir_type.is_subtype(t)
    assert not t.is_subtype(ir_type)

def test_find_irrelevant_type_parameterized2():
    foo = tp.SimpleClassifier("Foo")
    con = tp.TypeConstructor("X", [tp.TypeParameter("T")])
    t = con.new([foo])
    bar = tp.SimpleClassifier("Bar", [t])

    ir_type = tutils.find_irrelevant_type(t, [foo, con, bar], KT_FACTORY)
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

    ir_type = tutils.find_irrelevant_type(baz.get_type(), [foo, bar, baz],
                                          KT_FACTORY)
    assert ir_type is not None


def test_find_irrelevant_type_with_given_classes():
    foo = ast.ClassDeclaration("Foo", [], 0)
    bar = ast.ClassDeclaration(
        "Bar", [ast.SuperClassInstantiation(foo.get_type())], 0)
    baz = ast.ClassDeclaration(
        "Baz", [ast.SuperClassInstantiation(bar.get_type())], 0)
    qux = ast.ClassDeclaration("Qux", [], 0)

    ir_type = tutils.find_irrelevant_type(bar.get_type(), [foo, bar, baz],
                                          KT_FACTORY)
    assert ir_type is None

    ir_type = tutils.find_irrelevant_type(bar.get_type(), [foo, bar, baz, qux],
                                          KT_FACTORY)
    assert ir_type == qux.get_type()


def test_type_hint_constants_and_binary_ops():
    context = ctx.Context()
    expr = ast.IntegerConstant(10, kt.Long)
    assert (tutils.get_type_hint(expr, context, tuple(), KT_FACTORY, []) ==
            kt.Long)

    expr = ast.RealConstant("10.9", kt.Float)
    assert (tutils.get_type_hint(expr, context, tuple(), KT_FACTORY, []) ==
            kt.Float)

    expr = ast.BooleanConstant("true")
    assert (tutils.get_type_hint(expr, context, tuple(), KT_FACTORY, []) ==
            kt.Boolean)

    expr = ast.CharConstant("d")
    assert (tutils.get_type_hint(expr, context, tuple(), KT_FACTORY, []) ==
            kt.Char)

    expr = ast.StringConstant("true")
    assert (tutils.get_type_hint(expr, context, tuple(), KT_FACTORY, []) ==
            kt.String)

    expr = ast.LogicalExpr(ast.StringConstant("true"),
                           ast.StringConstant("false"),
                           ast.Operator("&&"))
    assert (tutils.get_type_hint(expr, context, tuple(), KT_FACTORY, []) ==
            kt.Boolean)


def test_type_hint_variables():
    context = ctx.Context()
    expr = ast.Variable("x")
    assert (tutils.get_type_hint(expr, context, tuple(), KT_FACTORY, []) is
            None)

    decl = ast.VariableDeclaration("x", ast.StringConstant("foo"),
                                   var_type=kt.String)
    context.add_var(ast.GLOBAL_NAMESPACE, decl.name, decl)
    assert (tutils.get_type_hint(expr, context, tuple(), KT_FACTORY, []) is
            None)
    assert (tutils.get_type_hint(
        expr, context, ast.GLOBAL_NAMESPACE, KT_FACTORY, []) == kt.String)


def test_type_hint_new():
    context = ctx.Context()
    expr = ast.New(kt.Any, [])
    assert (tutils.get_type_hint(expr, context, tuple(), KT_FACTORY, []) ==
            kt.Any)


def test_type_hint_conditional():
    context = ctx.Context()
    decl = ast.VariableDeclaration("x", ast.StringConstant("foo"),
                                   var_type=kt.String)
    context.add_var(ast.GLOBAL_NAMESPACE, decl.name, decl)
    expr1 = ast.Variable("x")
    expr2 = ast.StringConstant("foo")
    cond1 = ast.Conditional(ast.BooleanConstant("true"), expr1, expr2, kt.String)
    cond2 = ast.Conditional(ast.BooleanConstant("true"), cond1, expr1, kt.String)
    cond3 = ast.Conditional(ast.BooleanConstant("true"), cond2, expr2, kt.String)

    assert tutils.get_type_hint(cond3, context, ast.GLOBAL_NAMESPACE,
                                KT_FACTORY, []) == kt.String


def test_type_hint_func_call():
    context = ctx.Context()
    func = ast.FunctionDeclaration("func", params=[], ret_type=kt.Unit,
                                   body=None,
                                   func_type=ast.FunctionDeclaration.FUNCTION)
    context.add_func(ast.GLOBAL_NAMESPACE, func.name, func)
    expr = ast.FunctionCall("func", [])
    assert tutils.get_type_hint(expr, context, tuple(), KT_FACTORY, []) is None
    assert (tutils.get_type_hint(
        expr, context, ast.GLOBAL_NAMESPACE, KT_FACTORY, []) == kt.Unit)


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
    cond1 = ast.Conditional(ast.BooleanConstant("true"), expr1, new_expr, cls.get_type())
    cond2 = ast.Conditional(ast.BooleanConstant("true"), cond1, new_expr, cls.get_type())
    cond3 = ast.Conditional(ast.BooleanConstant("true"), cond2, expr1, cls.get_type())

    expr = ast.FunctionCall("func", [], cond3)
    assert (tutils.get_type_hint(
        expr, context, ast.GLOBAL_NAMESPACE, KT_FACTORY, []) == kt.Integer)

def test_type_hint_func_call_receiver_parameterized():
    context = ctx.Context()
    type_param = tp.TypeParameter("T")
    func = ast.FunctionDeclaration("func", params=[], ret_type=type_param,
                                   body=None,
                                   func_type=ast.FunctionDeclaration.CLASS_METHOD,
                                   type_parameters=[type_param])
    cls = ast.ClassDeclaration("Foo", [], 0, functions=[func])

    context.add_class(ast.GLOBAL_NAMESPACE, cls.name, cls)
    context.add_func(ast.GLOBAL_NAMESPACE + (cls.name,), func.name, func)

    new_expr = ast.New(cls.get_type(), [])
    decl = ast.VariableDeclaration("x", new_expr,
                                   var_type=cls.get_type())
    context.add_var(ast.GLOBAL_NAMESPACE, decl.name, decl)
    expr = ast.FunctionCall("func", [], ast.Variable("x"), [kt.String])
    assert tutils.get_type_hint(
        expr, context, ast.GLOBAL_NAMESPACE, KT_FACTORY, []) == kt.String

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
    cond1 = ast.Conditional(ast.BooleanConstant("true"), expr1, new_expr, cls.get_type())
    cond2 = ast.Conditional(ast.BooleanConstant("true"), cond1, new_expr, cls.get_type())
    cond3 = ast.Conditional(ast.BooleanConstant("true"), cond2, expr1, cls.get_type())

    expr = ast.FieldAccess(cond3, "f")
    assert tutils.get_type_hint(expr, context, ast.GLOBAL_NAMESPACE,
                                KT_FACTORY, []) == kt.Integer


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
    cond1 = ast.Conditional(ast.BooleanConstant("true"), expr1, new_expr, cls3.get_type())
    cond2 = ast.Conditional(ast.BooleanConstant("true"), cond1, new_expr, cls3.get_type())
    cond3 = ast.Conditional(ast.BooleanConstant("true"), cond2, expr1, cls3.get_type())

    expr = ast.FunctionCall("func", [], cond3)
    assert tutils.get_type_hint(expr, context, ast.GLOBAL_NAMESPACE,
                                KT_FACTORY, []) == kt.Integer


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
    cond1 = ast.Conditional(ast.BooleanConstant("true"), expr1, new_expr, cls3.get_type())
    cond2 = ast.Conditional(ast.BooleanConstant("true"), cond1, new_expr, cls3.get_type())
    cond3 = ast.Conditional(ast.BooleanConstant("true"), cond2, expr1, cls3.get_type())

    expr = ast.FieldAccess(cond3, "f")

    program = ast.Program(context, language="kotlin")
    types = program.get_types()
    assert tutils.get_type_hint(expr, context, ast.GLOBAL_NAMESPACE,
                                KT_FACTORY, types) == kt.Integer


def test_type_hint_smart_cast():
    context = ctx.Context()
    field = ast.FieldDeclaration("f", kt.Integer)
    cls = ast.ClassDeclaration("Foo", [], 0, fields=[field])
    context.add_class(ast.GLOBAL_NAMESPACE, cls.name, cls)
    context.add_var(ast.GLOBAL_NAMESPACE + (cls.name,), field.name, field)

    new_expr = ast.New(cls.get_type(), [])
    decl = ast.VariableDeclaration("x", new_expr,
                                   var_type=kt.Any)
    context.add_var(ast.GLOBAL_NAMESPACE, decl.name, decl)
    expr = ast.Variable("x")

    decl2 = ast.VariableDeclaration("y", new_expr,
                                    var_type=kt.Any)
    context.add_var(ast.GLOBAL_NAMESPACE, decl2.name, decl2)
    expr2 = ast.Variable("y")

    decl3 = ast.VariableDeclaration("z", new_expr,
                                    var_type=cls.get_type())
    context.add_var(ast.GLOBAL_NAMESPACE, decl3.name, decl3)
    expr3 = ast.Variable("z")

    cond1 = ast.Conditional(ast.BooleanConstant("true"), expr2, expr3, cls.get_type())
    cond2 = ast.Conditional(ast.Is(expr2, cls.get_type()), expr2, expr3, cls.get_type())

    smart_casts = [(expr, cls.get_type())]
    program = ast.Program(context, language="kotlin")
    types = program.get_types()

    assert tutils.get_type_hint(expr, context, ast.GLOBAL_NAMESPACE,
                                KT_FACTORY, types) == kt.Any
    assert tutils.get_type_hint(expr, context, ast.GLOBAL_NAMESPACE,
                                KT_FACTORY, types,
                                smart_casts) == cls.get_type()
    assert tutils.get_type_hint(expr3, context, ast.GLOBAL_NAMESPACE,
                                KT_FACTORY, types) == cls.get_type()
    assert tutils.get_type_hint(cond1, context, ast.GLOBAL_NAMESPACE,
                                KT_FACTORY, types) == cls.get_type()
    assert tutils.get_type_hint(cond2, context, ast.GLOBAL_NAMESPACE,
                                KT_FACTORY, types) == cls.get_type()


def test_find_nearest_supertype():
    t1 = tp.SimpleClassifier("Foo", [])
    t2 = tp.SimpleClassifier("Bar", [t1])
    t3 = tp.SimpleClassifier("Baz", [t2])
    assert tutils.find_nearest_supertype(t3, [kt.Any]) == None
    assert tutils.find_nearest_supertype(t3, [t2, t1, t3]) == t2


def test_instantiate_type_constructor_simple():
    t_con = tp.TypeConstructor("Con", [tp.TypeParameter("T1"),
                                       tp.TypeParameter("T2")])
    types = [kt.String]

    ptype, params = tutils.instantiate_type_constructor(t_con, types)
    assert ptype == tp.ParameterizedType(t_con, [kt.String,
                                                 kt.String])
    params == {t_con.type_parameters[0]: kt.String,
               t_con.type_parameters[1]: kt.String}


def test_instantiate_type_constructor_nested():
    type_param1 = tp.TypeParameter("T1")
    type_param2 = tp.TypeParameter("T2", bound=type_param1)
    types = [kt.String]
    t_con = tp.TypeConstructor("Con",
                               type_parameters=[type_param1, type_param2])

    ptype, params = tutils.instantiate_type_constructor(t_con, types)
    assert ptype == tp.ParameterizedType(t_con, [kt.String,
                                                 kt.String])
    params == {t_con.type_parameters[0]: kt.String,
               t_con.type_parameters[1]: kt.String}


def test_instantiate_type_constructor_nested2():
    foo = tp.TypeConstructor("Foo", [tp.TypeParameter("T3")])

    type_param1 = tp.TypeParameter("T1")
    type_param2 = tp.TypeParameter("T2", bound=foo.new(
        [type_param1]))
    types = [kt.String]
    t_con = tp.TypeConstructor("Con",
                               type_parameters=[type_param1, type_param2])

    ptype, params = tutils.instantiate_type_constructor(t_con, types)

    assert ptype.type_args[0] == kt.String
    assert ptype.type_args[1].name == "Foo"
    assert ptype.type_args[1].type_args == [kt.String]

    foo_string = foo.new([kt.String])
    assert params == {
        type_param1: kt.String,
        type_param2: foo_string
    }


def test_instantiate_type_constructor_nested3():
    foo = tp.TypeConstructor("Foo", [tp.TypeParameter("T4")])
    bar = tp.TypeConstructor("Bar", [tp.TypeParameter("T3")])
    type_param1 = tp.TypeParameter("T1")
    bar_foo = bar.new([foo.new([type_param1])])
    type_param2 = tp.TypeParameter("T2", bound=bar_foo)
    types = [kt.String]
    t_con = tp.TypeConstructor("Con",
                               type_parameters=[type_param1, type_param2])

    ptype, params = tutils.instantiate_type_constructor(t_con, types)
    bar_foo_string = bar.new([foo.new([kt.String])])

    assert ptype.type_args[0] == kt.String
    assert ptype.type_args[1].name == "Bar"
    assert ptype.type_args[1] == bar_foo_string

    assert params == {
        type_param1: kt.String,
        type_param2: bar_foo_string
    }


def test_instantiate_type_constructor_bound():
    # class Foo<T>
    # class Bar<X, Y, Z>
    # class Test<K, T extends Foo<String>, R extends Bar<K, K, Int>>
    foo = tp.TypeConstructor("Foo", [tp.TypeParameter("T")])
    type_param1 = tp.TypeParameter("T1")
    type_param2 = tp.TypeParameter("T2")
    type_param3 = tp.TypeParameter("T3")
    bar = tp.TypeConstructor("Bar", [type_param1, type_param2, type_param3])

    type_param4 = tp.TypeParameter("T4")
    type_param5 = tp.TypeParameter("T5",
                                   bound=foo.new([kt.String]))
    type_param6 = tp.TypeParameter(
        "T6", bound=bar.new([type_param4,
                             type_param4,
                             kt.Integer]))
    test_con = tp.TypeConstructor("Test",
                                  [type_param4, type_param5, type_param6])

    t = tp.TypeParameter("K")
    test_t, params = tutils.instantiate_type_constructor(test_con, [t])
    assert test_t.type_args[0] == t
    assert test_t.type_args[1] == foo.new(
        [kt.String])
    assert test_t.type_args[2] == bar.new(
        [t, t, kt.Integer])


def test_instantiate_type_constructor_type_var_bound():
    type_param1 = tp.TypeParameter("T1", variance=tp.Covariant)
    type_param2 = tp.TypeParameter("T2", bound=type_param1,
                                   variance=tp.Covariant)

    foo = tp.TypeConstructor("Foo", [type_param1, type_param2])
    types = [kt.Double, kt.Integer]
    foo_t, _ = tutils.instantiate_type_constructor(foo, types=types,
                                                   type_var_map=None)
    assert foo_t in [
        foo.new([kt.Integer, kt.Integer]),
        foo.new([kt.Double, kt.Double])
    ]



def test_instantiate_type_constructor_with_type_var_map():
    type_param1 = tp.TypeParameter("T1")
    type_param2 = tp.TypeParameter("T2", bound=type_param1)
    type_param3 = tp.TypeParameter("T3")
    t_con = tp.TypeConstructor("Con", [type_param1, type_param2, type_param3])

    types = [kt.String]
    type_map = {type_param2: kt.Integer}
    ptype, params = tutils.instantiate_type_constructor(
        t_con, types=types, type_var_map=type_map)
    assert ptype.type_args == [kt.Integer,
                               kt.Integer,
                               kt.String]
    assert params == {
        type_param1: kt.Integer,
        type_param2: kt.Integer,
        type_param3: kt.String
    }

    # Change the bound of the third type parameter
    type_param3.bound = type_param2
    ptype, params = tutils.instantiate_type_constructor(
        t_con, types=types, type_var_map=type_map)
    assert ptype.type_args == [kt.Integer,
                               kt.Integer,
                               kt.Integer]
    assert params == {
        type_param1: kt.Integer,
        type_param2: kt.Integer,
        type_param3: kt.Integer
    }

    # Case 3: map to another type variable
    type_var = tp.TypeParameter("K", bound=kt.Any)
    type_map = {type_param2: type_var}
    ptype, params = tutils.instantiate_type_constructor(
        t_con, types=types, type_var_map=type_map)
    assert ptype.type_args == [type_var,
                               type_var,
                               type_var]
    assert params == {
        type_param1: type_var,
        type_param2: type_var,
        type_param3: type_var
    }


def test_unify_types():
    factory = kt.KotlinBuiltinFactory()
    type_param1 = tp.TypeParameter("T1")
    type_param2 = tp.TypeParameter("T2")
    type_param3 = tp.TypeParameter("T3")
    type_param4 = tp.TypeParameter("T4")
    foo = tp.TypeConstructor("Foo", [type_param1, type_param2])

    foo1 = foo.new([type_param3, kt.String])
    foo2 = foo.new([kt.Integer, kt.String])
    foo3 = foo.new([type_param4, kt.String])
    foo4 = foo.new([type_param4, kt.Integer])

    assert tutils.unify_types(foo1, foo2, factory) == {}
    assert tutils.unify_types(foo1, foo3, factory) == {type_param4: type_param3}
    assert tutils.unify_types(foo1, foo4, factory) == {}
    assert tutils.unify_types(foo2, foo3, factory) == {type_param4: kt.Integer}


def test_unify_type_vars():
    factory = kt.KotlinBuiltinFactory()
    type_var1 = tp.TypeParameter("T1")
    type_var2 = tp.TypeParameter("T2")

    assert tutils.unify_types(type_var1, type_var2,
                              factory) == {type_var2: type_var1}

    type_var2.bound = kt.String
    assert tutils.unify_types(type_var1, type_var2, factory) == {}

    type_var2.bound = None
    type_var1.bound = kt.String
    assert tutils.unify_types(type_var1, type_var2,
                              factory) == {type_var2: type_var1}


def test_unify_types_mul_type_var():
    factory = kt.KotlinBuiltinFactory()
    type_param1 = tp.TypeParameter("T1")
    type_param2 = tp.TypeParameter("T2")
    type_param3 = tp.TypeParameter("T3")

    foo = tp.TypeConstructor("Foo", [type_param1, type_param2])
    foo_p = foo.new([type_param3, type_param3])
    foo_e = foo.new([kt.Integer, kt.Number])
    assert tutils.unify_types(foo_p, foo_e, factory) == {}
    assert tutils.unify_types(foo_e, foo_p, factory) == {}


def test_unify_types_with_bounds():
    factory = kt.KotlinBuiltinFactory()
    type_param1 = tp.TypeParameter("T1")
    type_param2 = tp.TypeParameter("T2")
    type_param3 = tp.TypeParameter("T3")
    type_param4 = tp.TypeParameter("T4", bound=kt.String)
    foo = tp.TypeConstructor("Foo", [type_param1, type_param2])

    foo1 = foo.new([type_param3, kt.String])
    foo2 = foo.new([kt.Integer, kt.String])
    foo3 = foo.new([type_param4, kt.String])
    foo4 = foo.new([type_param4, kt.Integer])
    foo5 = foo.new([kt.String, kt.String])

    assert tutils.unify_types(foo1, foo2, factory) == {}
    assert tutils.unify_types(foo1, foo3, factory) == {}
    assert tutils.unify_types(foo1, foo4, factory) == {}
    assert tutils.unify_types(foo2, foo3, factory) == {}
    assert tutils.unify_types(foo5, foo3, factory) == {type_param4: kt.String}
    type_param3.bound = kt.String
    assert tutils.unify_types(foo1, foo3, factory) == {type_param4: type_param3}


def test_unify_types_with_paramerized_bounds():
    factory = kt.KotlinBuiltinFactory()
    type_param1 = tp.TypeParameter("T1")
    type_param2 = tp.TypeParameter("T2")
    bar = tp.TypeConstructor("Bar", [type_param1, type_param2])


    type_param3 = tp.TypeParameter("T3")
    type_param4 = tp.TypeParameter("T4", bound=bar.new(
        [kt.String, type_param3]))
    type_param5 = tp.TypeParameter("T5")
    foo = tp.TypeConstructor("Foo", [type_param3, type_param4])

    foo1 = foo.new([kt.String,
                    bar.new([kt.String,
                             kt.Integer])])
    foo2 = foo.new([type_param5,
                    bar.new([kt.String,
                             type_param5])])
    foo3 = foo.new([kt.String,
                    bar.new([kt.String,
                             kt.String])])
    assert tutils.unify_types(foo1, foo2, factory) == {}
    assert tutils.unify_types(foo3, foo2, factory) == {type_param5: kt.String}

    # test case 2
    type_param2.bound = kt.Long
    type_param4.bound = kt.Boolean
    foo = tp.TypeConstructor("Foo", [type_param1, type_param2, type_param3])
    foo_p = foo.new([type_param5, kt.Long,
                     type_param4])
    foo_e = foo.new([kt.Integer, kt.Long,
                     kt.Float])

    params = tutils.unify_types(foo_e, foo_p, factory)
    assert params == {}


def test_unify_types_with_conflicted_type_vars():
    factory = kt.KotlinBuiltinFactory()
    type_param1 = tp.TypeParameter("T1")
    type_param2 = tp.TypeParameter("T2")
    foo = tp.TypeConstructor("Foo", [type_param1, type_param2])
    bar = tp.TypeConstructor("Bar", [type_param1, type_param2])
    foo_d = foo.new([type_param1, type_param2])
    foo_a = foo.new([type_param1, type_param2])

    params = tutils.unify_types(foo_a, foo_d, factory)
    assert params == {type_param1: type_param1, type_param2: type_param2}


def test_unify_types_function_type():
    factory = kt.KotlinBuiltinFactory()
    type_param1 = tp.TypeParameter("T1")
    type_param2 = tp.TypeParameter("T2")
    t1 = kt.FunctionType(1).new([type_param1, tp.WildCardType(type_param2,
                                                              tp.Covariant)])
    t2 = kt.FunctionType(1).new([type_param1, tp.WildCardType(type_param2,
                                                              tp.Covariant)])

    params = tutils.unify_types(t1, t2, factory)
    assert params == {
        type_param1: type_param1,
        type_param2: type_param2
    }


def test_unify_types_same_parameterized_type():
    factory = kt.KotlinBuiltinFactory()
    type_param1 = tp.TypeParameter("T1")
    type_param2 = tp.TypeParameter("T2")
    type_param3 = tp.TypeParameter("T3")
    type_param4 = tp.TypeParameter("T4")
    foo = tp.TypeConstructor("Foo", [type_param1, type_param2])
    foo_type = foo.new([type_param3, type_param4])

    params = tutils.unify_types(foo_type, foo_type, factory)

    assert params == {
        type_param3: type_param3,
        type_param4: type_param4
    }


def test_unify_types_with_simple_and_parameterized_types():
    factory = kt.KotlinBuiltinFactory()
    type_param1 = tp.TypeParameter("T1")
    foo = tp.TypeConstructor("A", [type_param1])
    bar = tp.SimpleClassifier("B", [foo.new([kt.String])])
    foo_d = foo.new([type_param1])

    params = tutils.unify_types(bar, foo_d, factory, same_type=False)
    assert params == {type_param1: kt.String}
    assert tutils.unify_types(foo_d, bar, factory, same_type=False) == {}

    type_param2 = tp.TypeParameter("T2")
    foo = tp.TypeConstructor("A", [type_param1, type_param2])
    bar = tp.SimpleClassifier("B", [foo.new([kt.String, kt.Long])])
    foo_d = foo.new([kt.String, type_param1])
    params = tutils.unify_types(bar, foo_d, factory, same_type=False)
    assert params == {type_param1: kt.Long}

    bar = tp.TypeConstructor("B", [type_param2],
                             [foo.new([kt.String, type_param2])])
    bar_d = bar.new([kt.Long])
    params = tutils.unify_types(bar_d, foo_d, factory, same_type=False)
    assert params == {type_param1: kt.Long}


def test_build_type_variable_dependencies():
    assert tutils.build_type_variable_dependencies(kt.String, kt.String) == {}
    assert tutils.build_type_variable_dependencies(kt.String, kt.Integer) == {}

    type_param1 = tp.TypeParameter("T1")
    foo_con = tp.TypeConstructor("Foo", [type_param1])
    foo = foo_con.new([kt.String])
    assert tutils.build_type_variable_dependencies(foo, foo) == {}

    type_param2 = tp.TypeParameter("T2")
    bar = tp.TypeConstructor("Bar", [type_param2]).new([kt.String])
    assert tutils.build_type_variable_dependencies(foo, bar) == {
        foo.name: ["Foo.T1"],
        bar.name: ["Bar.T2"]
    }
    assert tutils.build_type_variable_dependencies(bar, foo) == {
        foo.name: ["Foo.T1"],
        bar.name: ["Bar.T2"]
    }

    type_param3 = tp.TypeParameter("T3")
    bar_con = tp.TypeConstructor("Bar", [type_param2, type_param3],
                                 [foo_con.new([type_param3])])
    foo_any = foo_con.new([kt.Any])
    bar = bar_con.new([kt.Integer, kt.Any])
    assert tutils.build_type_variable_dependencies(foo_any, bar) == {
        foo_any.name: ["Foo.T1"],
        bar.name: ["Bar.T2", "Bar.T3"]
    }
    assert tutils.build_type_variable_dependencies(bar, foo_any) == {
        foo_any.name: ["Foo.T1"],
        bar.name: ["Bar.T2", "Bar.T3"],
        "Foo.T1": ["Bar.T3"]
    }

    bar = bar_con.new([type_param1, kt.Any])
    baz_con = tp.TypeConstructor("Baz", [type_param1], [bar])
    baz = baz_con.new([kt.Any])
    assert tutils.build_type_variable_dependencies(foo_any, baz) == {
        foo_any.name: ["Foo.T1"],
        baz.name: ["Baz.T1"],
    }
    assert tutils.build_type_variable_dependencies(baz, foo_any) == {
        foo.name: ["Foo.T1"],
        bar.name: ["Bar.T2", "Bar.T3"],
        baz.name: ["Baz.T1"],
        "Bar.T2": ["Baz.T1"],
        "Foo.T1": ["Bar.T3"]
    }

    bar = bar_con.new([kt.Any, kt.Any])
    baz_con = tp.TypeConstructor("Baz", [type_param1], [bar])
    baz = baz_con.new([kt.Any])
    assert tutils.build_type_variable_dependencies(baz, foo_any) == {
        foo.name: ["Foo.T1"],
        bar.name: ["Bar.T2", "Bar.T3"],
        baz.name: ["Baz.T1"],
        "Foo.T1": ["Bar.T3"]
    }


def test_update_type_var_bound_rec():
    type_param1 = tp.TypeParameter("T1")
    type_param2 = tp.TypeParameter("T2", bound=type_param1)
    type_param3 = tp.TypeParameter("T3", bound=type_param2)
    type_param4 = tp.TypeParameter("T4")
    type_var_map = {
        type_param1: kt.String
    }
    indexes = {
        type_param1: 0,
        type_param2: 1,
        type_param3: 2,
        type_param4: 3,
    }
    targs = [kt.String]
    old_type_var_map = deepcopy(type_var_map)
    old_targs = deepcopy(targs)
    tutils.update_type_var_bound_rec(tp.Classifier("Foo"), kt.String,
                                     targs, indexes, type_var_map)
    assert old_targs == targs
    assert old_type_var_map == type_var_map

    tutils.update_type_var_bound_rec(type_param4, kt.Integer,
                                     targs, indexes, type_var_map)
    assert old_targs == targs
    assert old_type_var_map == type_var_map


    tutils.update_type_var_bound_rec(type_param2, kt.Integer,
                                     targs, indexes, type_var_map)
    assert type_var_map == {type_param1: kt.Integer}
    assert targs == [kt.Integer]

    type_var_map = deepcopy(old_type_var_map)
    type_var_map[type_param2] = kt.Boolean
    targs = deepcopy(old_targs)
    targs.append(kt.Boolean)

    tutils.update_type_var_bound_rec(type_param3, kt.Integer,
                                     targs, indexes, type_var_map)
    assert type_var_map == {type_param1: kt.Integer, type_param2: kt.Integer}
    assert targs == [kt.Integer, kt.Integer]

    type_var_map[type_param1] = kt.Number
    type_var_map[type_param2] = kt.Number
    targs = [kt.Number, kt.Number]
    tutils.update_type_var_bound_rec(type_param3, kt.Integer,
                                     targs, indexes, type_var_map)
    assert type_var_map == {type_param1: kt.Number, type_param2: kt.Number}
    assert targs == [kt.Number, kt.Number]
