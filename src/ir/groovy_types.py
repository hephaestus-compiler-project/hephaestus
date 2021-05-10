# pylint: disable=abstract-method, useless-super-delegation,too-many-ancestors
from src.ir.types import Builtin


from src import utils
import src.ir.builtins as bt
import src.ir.types as tp


class GroovyBuiltinFactory(bt.BuiltinFactory):
    def get_language(self):
        return "groovy"

    def get_builtin(self):
        return GroovyBuiltin

    def get_void_type(self):
        return VoidType()

    def get_any_type(self):
        return ObjectType()

    def get_number_type(self):
        return NumberType()

    def get_integer_type(self):
        return IntegerType()

    def get_byte_type(self):
        return ByteType(primitive=utils.random.bool())

    def get_short_type(self):
        return ShortType(primitive=utils.random.bool())

    def get_long_type(self):
        return LongType(primitive=utils.random.bool())

    def get_float_type(self):
        return FloatType(primitive=utils.random.bool())

    def get_double_type(self):
        return DoubleType(primitive=utils.random.bool())

    def get_big_decimal_type(self):
        return BigDecimalType()

    def get_boolean_type(self):
        return BooleanType(primitive=utils.random.bool())

    def get_char_type(self):
        return CharType(primitive=False)

    def get_string_type(self):
        return StringType()

    def get_array_type(self):
        return ArrayType()


class GroovyBuiltin(Builtin):
    def __init__(self, name, primitive):
        super().__init__(name)
        self.primitive = primitive

    def __str__(self):
        if not self.is_primitive():
            return str(self.name) + "(groovy-builtin)"
        return str(self.name).lower() + "(groovy-primitive)"

    def is_primitive(self):
        return self.primitive

    def box_type(self):
        raise NotImplementedError('box_type() must be implemented')


class ObjectType(GroovyBuiltin):
    def __init__(self, name="Object"):
        super().__init__(name, False)

    def get_builtin_type(self):
        return bt.Any

    def box_type(self):
        return self


class VoidType(GroovyBuiltin):
    def __init__(self, name="void", primitive=False):
        super().__init__(name, primitive)
        if not self.primitive:
            self.supertypes.append(ObjectType())
        else:
            self.supertypes = []

    def get_builtin_type(self):
        return bt.Void

    def box_type(self):
        return VoidType(self.name, primitive=False)


class NumberType(ObjectType):
    def __init__(self, name="Number"):
        super().__init__(name)
        self.supertypes.append(ObjectType())

    def get_builtin_type(self):
        return bt.Number

    def box_type(self):
        return self


class IntegerType(NumberType):
    def __init__(self, name="Integer", primitive=False):
        super().__init__(name)
        self.primitive = primitive
        self.supertypes.append(NumberType())

    def get_builtin_type(self):
        return bt.Integer

    def box_type(self):
        return IntegerType(self.name, primitive=False)

    def get_name(self):
        if self.is_primitive():
            return "int"
        return super().get_name()


class ShortType(NumberType):
    def __init__(self, name="Short", primitive=False):
        super().__init__(name)
        self.primitive = primitive
        self.supertypes.append(NumberType())

    def get_builtin_type(self):
        return bt.Short

    def box_type(self):
        return ShortType(self.name, primitive=False)

    def get_name(self):
        if self.is_primitive():
            return "short"
        return super().get_name()


class LongType(NumberType):
    def __init__(self, name="Long", primitive=False):
        super().__init__(name)
        self.primitive = primitive
        self.supertypes.append(NumberType())

    def get_builtin_type(self):
        return bt.Long

    def box_type(self):
        return LongType(self.name, primitive=False)

    def get_name(self):
        if self.is_primitive():
            return "long"
        return super().get_name()


class ByteType(NumberType):
    def __init__(self, name="Byte", primitive=False):
        super().__init__(name)
        self.primitive = primitive
        self.supertypes.append(NumberType())

    def get_builtin_type(self):
        return bt.Byte

    def box_type(self):
        return ByteType(self.name, primitive=False)

    def get_name(self):
        if self.is_primitive():
            return "byte"
        return super().get_name()


class FloatType(NumberType):
    def __init__(self, name="Float", primitive=False):
        super().__init__(name)
        self.primitive = primitive
        self.supertypes.append(NumberType())

    def get_builtin_type(self):
        return bt.Float

    def box_type(self):
        return FloatType(self.name, primitive=False)

    def get_name(self):
        if self.is_primitive():
            return "float"
        return super().get_name()


class DoubleType(NumberType):
    def __init__(self, name="Double", primitive=False):
        super().__init__(name)
        self.primitive = primitive
        self.supertypes.append(NumberType())

    def get_builtin_type(self):
        return bt.Double

    def box_type(self):
        return DoubleType(self.name, primitive=False)

    def get_name(self):
        if self.is_primitive():
            return "double"
        return super().get_name()


class BigDecimalType(NumberType):
    """Default decimal type in groovy.

    d = 10.5; assert d instanceof BigDecimal
    d = 10.5d; assert d instanceof Double
    d = 10.5f; assert d instanceof Float
    """
    def __init__(self, name="BigDecimal"):
        super().__init__(name)
        self.supertypes.append(NumberType())

    def get_builtin_type(self):
        return bt.BigDecimal

    def box_type(self):
        return self


class CharType(ObjectType):
    def __init__(self, name="Character", primitive=False):
        super().__init__(name)
        self.primitive = primitive
        self.supertypes.append(ObjectType())

    def get_builtin_type(self):
        return bt.Char

    def box_type(self):
        return CharType(self.name, primitive=False)

    def get_name(self):
        if self.is_primitive():
            return "char"
        return super().get_name()


class StringType(ObjectType):
    def __init__(self, name="String"):
        super().__init__(name)
        self.supertypes.append(ObjectType())

    def get_builtin_type(self):
        return bt.String

    def box_type(self):
        return self


class BooleanType(ObjectType):
    def __init__(self, name="Boolean", primitive=False):
        super().__init__(name)
        self.primitive = primitive
        self.supertypes.append(ObjectType())

    def get_builtin_type(self):
        return bt.Boolean

    def box_type(self):
        return BooleanType(self.name, primitive=False)

    def get_name(self):
        if self.is_primitive():
            return "boolean"
        return super().get_name()


class ArrayType(tp.TypeConstructor, ObjectType):
    def __init__(self, name="Array"):
        # In Groovy, arrays are covariant.
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
BigDecimal = BigDecimalType()
Char = CharType()
String = StringType()
Boolean = BooleanType()
Array = ArrayType()
NonNothingTypes = [Object, Number, Integer, Short, Long, Byte, Float,
                   Double, BigDecimal, Char, String, Boolean, Array]
