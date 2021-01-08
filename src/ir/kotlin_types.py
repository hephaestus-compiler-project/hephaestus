# pylint: disable=abstract-method
from src.ir.types import Builtin


class AnyType(Builtin):
    def __init__(self, name="Any"):
        super().__init__(name)


class NothingType(Builtin):
    def __init__(self, name="Nothing"):
        super().__init__(name)

    def is_subtype(self, other):
        return True


class UnitType(AnyType):
    def __init__(self, name="Unit"):
        super().__init__(name)
        self.supertypes.append(AnyType())


class NumberType(AnyType):
    def __init__(self, name="Number"):
        super().__init__(name)
        self.supertypes.append(AnyType())


class IntegerType(NumberType):
    def __init__(self, name="Int"):
        super().__init__(name)
        self.supertypes.append(NumberType())


class ShortType(NumberType):
    def __init__(self, name="Short"):
        super().__init__(name)
        self.supertypes.append(NumberType())


class LongType(NumberType):
    def __init__(self, name="Long"):
        super().__init__(name)
        self.supertypes.append(NumberType())


class ByteType(NumberType):
    def __init__(self, name="Byte"):
        super().__init__(name)
        self.supertypes.append(NumberType())


class FloatType(NumberType):
    def __init__(self, name="Float"):
        super().__init__(name)
        self.supertypes.append(NumberType())

class DoubleType(NumberType):
    def __init__(self, name="Double"):
        super().__init__(name)
        self.supertypes.append(NumberType())

class CharType(AnyType):
    def __init__(self, name="Char"):
        super().__init__(name)
        self.supertypes.append(AnyType())

class StringType(AnyType):
    def __init__(self, name="String"):
        super().__init__(name)
        self.supertypes.append(AnyType())

class BooleanType(AnyType):
    def __init__(self, name="Boolean"):
        super().__init__(name)
        self.supertypes.append(AnyType())


Any = AnyType()
Nothing = NothingType()
Unit = UnitType()
Number = NumberType()
Integer = IntegerType()
Short = ShortType()
Long = LongType()
Byte = ByteType()
Float = FloatType()
Double = DoubleType()
Char = CharType()
String = StringType()
Boolean = BooleanType()
NonNothingTypes = [Any, Number, Integer, Short, Long, Byte, Float,
                   Double, Char, String, Boolean]
