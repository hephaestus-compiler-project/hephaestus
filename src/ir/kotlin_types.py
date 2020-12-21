from src.ir.types import Builtin


class AnyType(Builtin):
    def __init__(self, name="Any"):
        super(AnyType, self).__init__(name)


class NothingType(Builtin):
    def __init__(self, name="Nothing"):
        super(NothingType, self).__init__(name)

    def is_subtype(self, t):
        return True


class UnitType(AnyType):
    def __init__(self, name="Unit"):
        super(UnitType, self).__init__(name)
        self.supertypes.append(AnyType())


class NumberType(AnyType):
    def __init__(self, name="Number"):
        super(NumberType, self).__init__(name)
        self.supertypes.append(AnyType())


class IntegerType(NumberType):
    def __init__(self, name="Int"):
        super(IntegerType, self).__init__(name)
        self.supertypes.append(NumberType())


class ShortType(NumberType):
    def __init__(self, name="Short"):
        super(ShortType, self).__init__(name)
        self.supertypes.append(NumberType())


class LongType(NumberType):
    def __init__(self, name="Long"):
        super(LongType, self).__init__(name)
        self.supertypes.append(NumberType())


class ByteType(NumberType):
    def __init__(self, name="Byte"):
        super(ByteType, self).__init__(name)
        self.supertypes.append(NumberType())


class FloatType(NumberType):
    def __init__(self, name="Float"):
        super(FloatType, self).__init__(name)
        self.supertypes.append(NumberType())

class DoubleType(NumberType):
    def __init__(self, name="Double"):
        super(DoubleType, self).__init__(name)
        self.supertypes.append(NumberType())

class CharType(AnyType):
    def __init__(self, name="Char"):
        super(CharType, self).__init__(name)
        self.supertypes.append(AnyType())

class StringType(AnyType):
    def __init__(self, name="String"):
        super(StringType, self).__init__(name)
        self.supertypes.append(AnyType())

class BooleanType(AnyType):
    def __init__(self, name="Boolean"):
        super(BooleanType, self).__init__(name)
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
NonNothingTypes = [Any, Unit, Number, Integer, Short, Long, Byte, Float,
    Double, Char, String, Boolean]
