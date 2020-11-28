from src.ir.ast import *
from src.ir.types import *
from src.ir.kotlin_types import *


def test_simple_classifier():
    cls1 = SimpleClassifier("Cls1", [])
    assert cls1.name == "Cls1"
    assert cls1.get_supertypes() == {cls1}
    assert cls1.supertypes == []
    assert not cls1.is_subtype(ShortType())
    cls2 = SimpleClassifier("Cls2", [cls1])
    assert cls2.get_supertypes() == {cls1, cls2}
    assert cls2.is_subtype(cls1)
    cls3 = SimpleClassifier("Cls3", [cls2, ShortType()])
    assert (cls3.get_supertypes() ==
            {cls1, cls2, cls3, ShortType(), NumberType(), AnyType()})
    assert cls3.is_subtype(cls1)
    assert cls3.is_subtype(cls2)
    assert cls3.is_subtype(cls3)
    assert cls3.is_subtype(ShortType())
    assert cls3.is_subtype(NumberType())
    assert cls3.is_subtype(AnyType())
    assert not cls3.is_subtype(NothingType())
    assert not cls3.is_subtype(IntegerType())
