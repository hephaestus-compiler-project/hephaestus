from copy import deepcopy

import pytest

from src.ir.ast import *
from src.ir.types import *
from src.ir.kotlin_types import *


def assert_abstract_funcs(actual, expected):
    assert len(actual) == len(expected)
    table = {f.name: f for f in expected}
    for f in actual:
        exp = table.get(f.name)
        assert exp.is_equal(exp)


def test_simple_classifier():
    short = ShortType()
    assert short.get_supertypes() == {AnyType(), NumberType(), short}
    assert short.is_subtype(AnyType())
    assert short.is_subtype(NumberType())
    assert short.is_subtype(ShortType())
    assert short.is_subtype(short)
    assert not short.is_subtype(IntegerType())
    cls1 = SimpleClassifier("Cls1", [])
    assert cls1.name == "Cls1"
    assert cls1.get_supertypes() == {cls1}
    assert cls1.supertypes == []
    assert cls1.is_subtype(cls1)
    assert not cls1.is_subtype(ShortType())
    cls2 = SimpleClassifier("Cls2", [cls1])
    assert cls2.get_supertypes() == {cls1, cls2}
    assert cls2.is_subtype(cls1)
    assert cls2.is_subtype(cls2)
    cls3 = SimpleClassifier("Cls3", [cls2, ShortType()])
    assert (cls3.get_supertypes() ==
            {cls1, cls2, ShortType(), NumberType(), AnyType(), cls3})
    assert cls3.is_subtype(cls1)
    assert cls3.is_subtype(cls2)
    assert cls3.is_subtype(cls3)
    assert cls3.is_subtype(ShortType())
    assert cls3.is_subtype(NumberType())
    assert cls3.is_subtype(AnyType())
    assert not cls3.is_subtype(NothingType())
    assert not cls3.is_subtype(IntegerType())
    nothing = NothingType()
    assert nothing.is_subtype(nothing)
    assert nothing.is_subtype(AnyType())
    assert nothing.is_subtype(short)
    assert nothing.is_subtype(cls1)
    assert nothing.is_subtype(cls2)
    assert nothing.is_subtype(cls3)
    type_param_a = TypeParameter("A")
    t_constructor = TypeConstructor("Pcls", [type_param_a])
    p_type_i = ParameterizedType(t_constructor, [IntegerType()])
    cls4 = SimpleClassifier("Cls4", [cls2, p_type_i])
    assert (cls4.get_supertypes() ==
            {cls1, cls2, p_type_i, cls4})
    assert cls4.is_subtype(p_type_i)
    assert cls4.is_subtype(cls1)
    assert cls4.is_subtype(cls2)
    assert cls4.is_subtype(cls4)
    assert not cls4.is_subtype(IntegerType())


def test_parameterized_type():
    number_subtypes = [
        NumberType(), IntegerType(), ShortType(),
        LongType(), ByteType(), FloatType(), DoubleType()]

    # Invariant
    cls1 = SimpleClassifier("Cls1", [])
    tp1 = [TypeParameter("T", Invariant)]
    tc1 = TypeConstructor("Tp1", tp1, [cls1])
    ta1 = [NumberType()]
    pt1 = ParameterizedType(tc1, ta1)
    assert pt1.name == "Tp1"
    assert pt1.get_supertypes() == {cls1, pt1}
    assert pt1.is_subtype(cls1)
    assert pt1.is_subtype(pt1)
    assert not pt1.is_subtype(NumberType())
    assert not pt1.is_subtype(ParameterizedType(
        tc1, [AnyType()]))
    assert not pt1.is_subtype(
        ParameterizedType(tc1, [IntegerType()]))

    # Covariant
    tp2 = [TypeParameter("T", Covariant)]
    tc2 = TypeConstructor("Tp2", tp2, [cls1])
    ta2 = [NumberType()]
    pt2 = ParameterizedType(tc2, ta2)
    assert pt2.get_supertypes() == {cls1, pt2}
    assert pt2.is_subtype(cls1)
    assert pt2.is_subtype(pt2)
    assert pt2.is_subtype(ParameterizedType(tc2, [AnyType()]))
    assert not pt2.is_subtype(ParameterizedType(
        tc2, [IntegerType()]))

    # Contravariant
    tp3 = [TypeParameter("T", Contravariant)]
    tc3 = TypeConstructor("Tp3", tp3, [cls1])
    ta3 = [NumberType()]
    pt3 = ParameterizedType(tc3, ta3)
    assert pt3.get_supertypes() == {cls1, pt3}
    assert pt3.is_subtype(cls1)
    assert pt3.is_subtype(pt3)
    assert pt3.is_subtype(ParameterizedType(
        tc3, [IntegerType()]))
    assert not pt3.is_subtype(ParameterizedType(
        tc3, [AnyType()]))

    # Recursive
    tp4 = [TypeParameter("T", Covariant)]
    tc4 = TypeConstructor("Tp4", tp4, [cls1])
    temp_tp = [TypeParameter("T", Covariant)]
    temp_tc = TypeConstructor("Temp", temp_tp, [cls1])
    ta1 = [ParameterizedType(temp_tc, [NumberType()])]
    ta2 = [ParameterizedType(temp_tc, [AnyType()])]
    ta3 = [ParameterizedType(temp_tc, [IntegerType()])]
    pt4 = ParameterizedType(tc4, ta1)
    assert pt4.is_subtype(pt4)
    assert pt4.is_subtype(ParameterizedType(tc4, ta2))
    assert not pt4.is_subtype(ParameterizedType(tc4, ta3))

def test_classifier_check_supertypes():
    type_param_a = TypeParameter("A")
    t_constructor = TypeConstructor("Pcls", [type_param_a], [IntegerType()])
    p_type_s = ParameterizedType(t_constructor, [StringType()])
    p_type_i = ParameterizedType(t_constructor, [IntegerType()])
    cls1 = SimpleClassifier("Cls1", [p_type_i], True)
    cls2 = SimpleClassifier("Cls2", [p_type_s], True)
    try:
        cls3 = SimpleClassifier("Cls3", [cls2, p_type_i], True)
        assert False
    except AssertionError as e:
        if e.args[0] == "assert False":
            assert False
        assert True
    p_type_i2 = ParameterizedType(t_constructor, [IntegerType()])
    cls4 = SimpleClassifier("Cls4", [p_type_i2, p_type_i], True)


def test_inherits_from_simple():
    cls1 = ClassDeclaration("A", [], ClassDeclaration.REGULAR,)
    cls2 = ClassDeclaration("B", [SuperClassInstantiation(cls1.get_type())], 0)

    assert cls2.inherits_from(cls1)
    assert not cls1.inherits_from(cls2)


def test_inherits_from_parameterized():
    cls1 = ClassDeclaration("A", [], 0,
                            type_parameters=[TypeParameter("T")])
    cls2 = ClassDeclaration(
        "B", [SuperClassInstantiation(cls1.get_type().new(
            [String]))], 0)

    assert cls2.inherits_from(cls1)
    assert not cls1.inherits_from(cls2)


def test_inherits_from_parameterized_with_abstract():
    type_param = TypeParameter("T")
    type_param2 = TypeParameter("K", bound=Any)
    cls1 = ClassDeclaration("A", [], 0,
                            type_parameters=[type_param])
    cls2 = ClassDeclaration(
        "B", [SuperClassInstantiation(cls1.get_type().new(
            [type_param2]))], 0,
        type_parameters=[type_param2]
    )
    assert cls2.inherits_from(cls1)
    assert not cls1.inherits_from(cls2)


def test_get_abstract_functions():
    func1 = FunctionDeclaration("foo", [], String, None, 0)
    func2 = FunctionDeclaration("bar", [], Any, None, 0)
    cls1 = ClassDeclaration("A", [], 0, functions=[func1])
    cls2 = ClassDeclaration("B",
                            [SuperClassInstantiation(cls1.get_type(), [])],
                            functions=[func2])

    assert cls1.get_abstract_functions([cls1, cls2]) == {func1}
    assert_abstract_funcs(cls2.get_abstract_functions([cls1, cls2]),
                          {func1, func2})


def test_get_abstract_functions_chain():
    func1 = FunctionDeclaration("foo", [], String, None, 0)
    func2 = FunctionDeclaration("bar", [], Any, None, 0)
    cls1 = ClassDeclaration("A", [], functions=[func1])
    cls2 = ClassDeclaration("B",
                            [SuperClassInstantiation(cls1.get_type(), [])],
                            functions=[])
    cls3 = ClassDeclaration("C",
                            [SuperClassInstantiation(cls2.get_type(), [])],
                            functions=[func2])

    assert cls1.get_abstract_functions([cls1, cls2, cls3]) == {func1}
    assert_abstract_funcs(cls2.get_abstract_functions([cls1, cls2, cls3]),
                          {func1})
    assert_abstract_funcs(cls3.get_abstract_functions([cls1, cls2, cls3]),
                          {func1, func2})

    override_func = deepcopy(func1)
    func1.body = IntegerConstant(1, Integer)
    cls2.functions = [func1]
    assert_abstract_funcs(cls2.get_abstract_functions([cls1, cls2, cls3]),
                          [])
    assert_abstract_funcs(cls3.get_abstract_functions([cls1, cls2, cls3]),
                          {func2})


def test_get_abstract_functions_parameterized():
    type_param1 = TypeParameter("T")
    func1 = FunctionDeclaration(
        "foo", [ParameterDeclaration("x", type_param1)], type_param1, None, 0)
    func2 = FunctionDeclaration(
        "bar", [], type_param1, IntegerConstant(1, Integer), 0)
    cls1 = ClassDeclaration("A", [],
                            type_parameters=[type_param1],
                            functions=[func1, func2])
    cls2 = ClassDeclaration(
        "B", [SuperClassInstantiation(cls1.get_type().new([String]), [])],
        functions=[]
    )

    assert cls1.get_abstract_functions([cls1, cls2]) == {func1}
    exp_func1 = deepcopy(func1)
    exp_func1.params[0].param_type = String
    exp_func1.ret_type = String
    exp_func1.inferred_type = String
    assert_abstract_funcs(cls2.get_abstract_functions([cls1, cls2]),
                          [exp_func1])


def test_get_abstract_functions_parameterized_chain():
    type_param1 = TypeParameter("T")
    func1 = FunctionDeclaration(
        "foo", [ParameterDeclaration("x", type_param1)], type_param1, None, 0)
    cls1 = ClassDeclaration("A", [],
                            type_parameters=[type_param1],
                            functions=[func1])

    t_con = TypeConstructor("Foo", [TypeParameter("T")])
    type_param2 = TypeParameter("T")
    t = t_con.new([type_param2])
    cls2 = ClassDeclaration(
        "B", [SuperClassInstantiation(cls1.get_type().new([t]), [])],
        type_parameters=[type_param2],
        functions=[]
    )

    cls3 = ClassDeclaration(
        "C", [SuperClassInstantiation(cls2.get_type().new([String]), [])],
        functions=[]
    )
    actual_t = t_con.new([String])
    exp_func1 = deepcopy(func1)
    exp_func1.params[0].param_type = actual_t
    exp_func1.ret_type = actual_t
    exp_func1.inferred_type = actual_t
    assert_abstract_funcs(cls2.get_abstract_functions([cls1, cls2, cls3]),
                          [exp_func1])
