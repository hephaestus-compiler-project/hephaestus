# pylint: disable=abstract-method, useless-super-delegation,too-many-ancestors
# pylint: disable=too-few-public-methods
from src.ir.types import Builtin


import src.ir.builtins as bt
import src.ir.types as tp


class JavaBuiltinFactory(bt.BuiltinFactory):
    def get_language(self):
        return "java"

    def get_builtin(self):
        return JavaBuiltin

    def get_void_type(self):
        return VoidType()

    def get_any_type(self):
        return ObjectType()

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

    def get_array_type(self):
        return ArrayType()


class JavaBuiltin(Builtin):
    def __str__(self):
        return str(self.name) + "(java-builtin)"


class ObjectType(JavaBuiltin):
    def __init__(self, name="Object"):
        super().__init__(name)

    def get_builtin_type(self):
        return bt.Any


class VoidType(ObjectType):
    def __init__(self, name="void"):
        super().__init__(name)
        self.supertypes.append(ObjectType())

    def get_builtin_type(self):
        return bt.Void


class NumberType(ObjectType):
    def __init__(self, name="Number"):
        super().__init__(name)
        self.supertypes.append(ObjectType())

    def get_builtin_type(self):
        return bt.Number


class IntegerType(NumberType):
    def __init__(self, name="Integer"):
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


class CharType(ObjectType):
    def __init__(self, name="Character"):
        super().__init__(name)
        self.supertypes.append(ObjectType())

    def get_builtin_type(self):
        return bt.Char


class StringType(ObjectType):
    def __init__(self, name="String"):
        super().__init__(name)
        self.supertypes.append(ObjectType())

    def get_builtin_type(self):
        return bt.String


class BooleanType(ObjectType):
    def __init__(self, name="Boolean"):
        super().__init__(name)
        self.supertypes.append(ObjectType())

    def get_builtin_type(self):
        return bt.Boolean


class ArrayType(tp.TypeConstructor, ObjectType):
    def __init__(self, name="Array"):
        # In Java, arrays are covariant.
        super().__init__(name, [tp.TypeParameter(
            "T", variance=tp.TypeParameter.COVARIANT)])
        self.supertypes.append(ObjectType())


### WARNING: use them only for testing ###
Object = ObjectType()
Void = VoidType()
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
Array = ArrayType()
NonNothingTypes = [Object, Number, Integer, Short, Long, Byte, Float,
                   Double, Char, String, Boolean, Array]
