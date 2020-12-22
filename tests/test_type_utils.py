from src.ir import types as tp, kotlin_types as kt
from src.ir import type_utils as tutils


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
