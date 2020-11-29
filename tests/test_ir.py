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

def test_zero_division():
    with pytest.raises(ZeroDivisionError):
        1 / 0

def test_classifier_sypertypes():
    type_param_a = TypeParameter("A")
    pcls = ParameterizedClassifier("Pcls", [type_param_a], [IntegerType()])
    c_type_s = ConcreteType(pcls, [StringType()])
    c_type_i = ConcreteType(pcls, [IntegerType()])
    cls1 = SimpleClassifier("Cls1", [c_type_i])
    cls2 = SimpleClassifier("Cls2", [c_type_s])
    try:
        cls3 = SimpleClassifier("Cls3", [cls2, c_type_i])
        assert False
    except AssertionError as e:
        if e.args[0] == "assert False":
            assert False
        assert True
    c_type_i2 = ConcreteType(pcls, [IntegerType()])
    cls4 = SimpleClassifier("Cls4", [c_type_i2, c_type_i])
