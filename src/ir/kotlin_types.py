# pylint: disable=abstract-method, useless-super-delegation,too-many-ancestors
from src.ir.types import Builtin


import src.ir.builtins as bt


class KotlinBuiltinFactory(bt.BuiltinFactory):
    def get_builtin(self):
        return KotlinBuiltin

    def get_void_type(self):
        return UnitType()

    def get_any_type(self):
        return AnyType()

    def get_number_type(self):
        return NumberType()

    def get_integer_type(self):
        return IntegerType()

    def get_byte_type(self):
        return ByteType()

    def get_short_type(self):
        return ShortType()

    def get_long_type(self):
        return LongType()

    def get_float_type(self):
        return FloatType()

    def get_double_type(self):
        return DoubleType()

    def get_big_decimal_type(self):
        return DoubleType()

    def get_boolean_type(self):
        return BooleanType()

    def get_char_type(self):
        return CharType()

    def get_string_type(self):
        return StringType()

    def get_nothing(self):
        return NothingType()


class KotlinBuiltin(Builtin):
    def __str__(self):
        return str(self.name) + "(kotlin-builtin)"


class AnyType(KotlinBuiltin, ):
    def __init__(self, name="Any"):
        super().__init__(name)

    def get_builtin_type(self):
        return bt.Any


class NothingType(KotlinBuiltin):
    def __init__(self, name="Nothing"):
        super().__init__(name)

    def is_subtype(self, other):
        return True

    def get_builtin_type(self):
        return bt.Nothing


class UnitType(AnyType):
    def __init__(self, name="Unit"):
        super().__init__(name)
        self.supertypes.append(AnyType())

    def get_builtin_type(self):
        return bt.Void


class NumberType(AnyType):
    def __init__(self, name="Number"):
        super().__init__(name)
        self.supertypes.append(AnyType())

    def get_builtin_type(self):
        return bt.Number


class IntegerType(NumberType):
    def __init__(self, name="Int"):
        super().__init__(name)
        self.supertypes.append(NumberType())

    def get_builtin_type(self):
        return bt.Integer


class ShortType(NumberType):
    def __init__(self, name="Short"):
        super().__init__(name)
        self.supertypes.append(NumberType())

    def get_builtin_type(self):
        return bt.Short


class LongType(NumberType):
    def __init__(self, name="Long"):
        super().__init__(name)
        self.supertypes.append(NumberType())

    def get_builtin_type(self):
        return bt.Long


class ByteType(NumberType):
    def __init__(self, name="Byte"):
        super().__init__(name)
        self.supertypes.append(NumberType())

    def get_builtin_type(self):
        return bt.Byte


class FloatType(NumberType):
    def __init__(self, name="Float"):
        super().__init__(name)
        self.supertypes.append(NumberType())

    def get_builtin_type(self):
        return bt.Float


class DoubleType(NumberType):
    def __init__(self, name="Double"):
        super().__init__(name)
        self.supertypes.append(NumberType())

    def get_builtin_type(self):
        return bt.Double


class CharType(AnyType):
    def __init__(self, name="Char"):
        super().__init__(name)
        self.supertypes.append(AnyType())

    def get_builtin_type(self):
        return bt.Char


class StringType(AnyType):
    def __init__(self, name="String"):
        super().__init__(name)
        self.supertypes.append(AnyType())

    def get_builtin_type(self):
        return bt.String


class BooleanType(AnyType):
    def __init__(self, name="Boolean"):
        super().__init__(name)
        self.supertypes.append(AnyType())

    def get_builtin_type(self):
        return bt.Boolean


### WARNING: use them only for testing ###
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
