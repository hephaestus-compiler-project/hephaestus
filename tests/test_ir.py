import pytest
from src.ir.ast import *
from src.ir.types import *
from src.ir.kotlin_types import *


def test_simple_classifier():
    short = ShortType()
    assert short.get_supertypes() == {AnyType(), NumberType()}
    assert short.is_subtype(AnyType())
    assert short.is_subtype(NumberType())
    assert short.is_subtype(ShortType())
    assert short.is_subtype(short)
    assert not short.is_subtype(IntegerType())
    cls1 = SimpleClassifier("Cls1", [])
    assert cls1.name == "Cls1"
    assert cls1.get_supertypes() == set()
    assert cls1.supertypes == []
    assert cls1.is_subtype(cls1)
    assert not cls1.is_subtype(ShortType())
    cls2 = SimpleClassifier("Cls2", [cls1])
    assert cls2.get_supertypes() == {cls1}
    assert cls2.is_subtype(cls1)
    assert cls2.is_subtype(cls2)
    cls3 = SimpleClassifier("Cls3", [cls2, ShortType()])
    assert (cls3.get_supertypes() ==
            {cls1, cls2, ShortType(), NumberType(), AnyType()})
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
            {cls1, cls2, p_type_i})
    assert cls4.is_subtype(p_type_i)
    assert cls4.is_subtype(cls1)
    assert cls4.is_subtype(cls2)
    assert cls4.is_subtype(cls4)
    assert not cls4.is_subtype(IntegerType())


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
