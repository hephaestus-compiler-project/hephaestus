from src.ir.types import Builtin


class AnyType(Builtin):
    def __init__(self):
        super(AnyType, self).__init__("Any")

    def is_subtype(self, t):
        return isinstance(t, AnyType)


class NothingType(Builtin):
    def __init__(self):
        super(NothingType, self).__init__("Nothing")

    def is_subtype(self, t):
        return True


class UnitType(Builtin):
    def __init__(self):
        super(UnitType, self).__init__("Unit")

    def is_subtype(self, t):
        return isinstance(t, AnyType) or isinstance(t, UnitType)


class NumberType(Builtin):
    def __init__(self):
        super(UnitType, self).__init__("Number")

    def is_subtype(self, t):
        return isinstance(t, AnyType) or isinstance(t, NumberType)


class IntegerType(NumberType):
    def __init__(self):
        self.name = "Integer"


class ShortType(NumberType):
    def __init__(self):
        self.name = "Short"


class LongType(NumberType):
    def __init__(self):
        self.name = "Long"


class ByteType(NumberType):
    def __init__(self):
        self.name = "Byte"


class FloatType(NumberType):
    def __init__(self):
        self.name = "Float"

class DoubleType(NumberType):
    def __init__(self):
        self.name = "Double"

class CharType(Builtin):
    def __init__(self):
        super(UnitType, self).__init__("Char")

    def is_subtype(self, t):
        return isinstance(t, AnyType) or isinstance(t, CharType)


class StringType(Builtin):
    def __init__(self):
        super(UnitType, self).__init__("String")

    def is_subtype(self, t):
        return isinstance(t, AnyType) or isinstance(t, StringType)


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
