from src.ir import types as tp, kotlin_types as kt
from src.ir import ast, type_utils as tutils


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
