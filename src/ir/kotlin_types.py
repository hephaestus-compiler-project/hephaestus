from src.ir.types import Builtin


class AnyType(Builtin):
    def __init__(self):
        super(AnyType, self).__init__("Any")


class NothingType(Builtin):
    def __init__(self):
        super(NothingType, self).__init__("Nothing")

    def is_subtype(self, t):
        return True


class UnitType(AnyType):
    def __init__(self):
        Builtin.__init__(self, "Unit")


class NumberType(AnyType):
    def __init__(self):
        Builtin.__init__(self, "Number")


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

class CharType(AnyType):
    def __init__(self):
        Builtin.__init__(self, "Char")


class StringType(AnyType):
    def __init__(self):
        Builtin.__init__(self, "String")


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
