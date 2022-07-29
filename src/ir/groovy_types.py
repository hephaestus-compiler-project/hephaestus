# pylint: disable=abstract-method, useless-super-delegation,too-many-ancestors
from src.ir.types import Builtin

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
        return IntegerType(primitive=False)

    def get_byte_type(self):
        return ByteType(primitive=False)

    def get_short_type(self):
        return ShortType(primitive=False)

    def get_long_type(self):
        return LongType(primitive=False)

    def get_float_type(self):
        return FloatType(primitive=False)

    def get_double_type(self):
        return DoubleType(primitive=False)

    def get_big_decimal_type(self):
        return BigDecimalType()

    def get_boolean_type(self):
        return BooleanType(primitive=False)

    def get_char_type(self):
        return CharType(primitive=False)

    def get_string_type(self):
        return StringType()

    def get_array_type(self):
        return ArrayType()

    def get_function_type(self, nr_parameters=0):
        return FunctionType(nr_parameters)

    def get_big_integer_type(self):
        return BigIntegerType()

    def get_primitive_types(self):
        return [
            ByteType(primitive=True),
            ShortType(primitive=True),
            IntegerType(primitive=True),
            LongType(primitive=True),
            FloatType(primitive=True),
            DoubleType(primitive=True),
            CharType(primitive=True),
            BooleanType(primitive=True)
        ]

    def get_null_type(self):
        # FIXME
        raise Exception("Groovy does not support null types")

    def get_non_nothing_types(self):
        return super().get_non_nothing_types() + self.get_primitive_types()

    def get_number_types(self):
        return super().get_number_types() + self.get_primitive_types()[:-1]


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
            self.supertypes = set()

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
        if not self.primitive:
            self.supertypes.append(NumberType())
        else:
            self.supertypes = set()

    def get_builtin_type(self):
        return bt.Integer

    def box_type(self):
        return IntegerType(self.name, primitive=False)

    def is_assignable(self, other):
        assignable_types = (NumberType, IntegerType,)
        return self.is_subtype(other) or type(other) in assignable_types

    def get_name(self):
        if self.is_primitive():
            return "int"
        return super().get_name()


class ShortType(NumberType):
    def __init__(self, name="Short", primitive=False):
        super().__init__(name)
        self.primitive = primitive
        if not self.primitive:
            self.supertypes.append(NumberType())
        else:
            self.supertypes = set()

    def get_builtin_type(self):
        return bt.Short

    def box_type(self):
        return ShortType(self.name, primitive=False)

    def is_assignable(self, other):
        assignable_types = (NumberType, ShortType,)
        return self.is_subtype(other) or type(other) in assignable_types

    def get_name(self):
        if self.is_primitive():
            return "short"
        return super().get_name()


class LongType(NumberType):
    def __init__(self, name="Long", primitive=False):
        super().__init__(name)
        self.primitive = primitive
        if not self.primitive:
            self.supertypes.append(NumberType())
        else:
            self.supertypes = set()

    def get_builtin_type(self):
        return bt.Long

    def box_type(self):
        return LongType(self.name, primitive=False)

    def is_assignable(self, other):
        assignable_types = (NumberType, LongType,)
        return self.is_subtype(other) or type(other) in assignable_types

    def get_name(self):
        if self.is_primitive():
            return "long"
        return super().get_name()


class BigIntegerType(NumberType):
    def __init__(self, name="BigInteger"):
        super().__init__(name)
        self.supertypes.append(NumberType())

    def get_builtin_type(self):
        return bt.BigIntegerType

    def box_type(self):
        return self

    def is_assignable(self, other):
        assignable_types = (NumberType, BigIntegerType,)
        return self.is_subtype(other) or type(other) in assignable_types


class ByteType(NumberType):
    def __init__(self, name="Byte", primitive=False):
        super().__init__(name)
        self.primitive = primitive
        if not self.primitive:
            self.supertypes.append(NumberType())
        else:
            self.supertypes = set()

    def get_builtin_type(self):
        return bt.Byte

    def box_type(self):
        return ByteType(self.name, primitive=False)

    def is_assignable(self, other):
        assignable_types = (NumberType, ByteType,)
        return self.is_subtype(other) or type(other) in assignable_types

    def get_name(self):
        if self.is_primitive():
            return "byte"
        return super().get_name()


class FloatType(NumberType):
    def __init__(self, name="Float", primitive=False):
        super().__init__(name)
        self.primitive = primitive
        if not self.primitive:
            self.supertypes.append(NumberType())
        else:
            self.supertypes = set()

    def get_builtin_type(self):
        return bt.Float

    def box_type(self):
        return FloatType(self.name, primitive=False)

    def is_assignable(self, other):
        assignable_types = (NumberType, FloatType,)
        return self.is_subtype(other) or type(other) in assignable_types

    def get_name(self):
        if self.is_primitive():
            return "float"
        return super().get_name()


class DoubleType(NumberType):
    def __init__(self, name="Double", primitive=False):
        super().__init__(name)
        self.primitive = primitive
        if not self.primitive:
            self.supertypes.append(NumberType())
        else:
            self.supertypes = set()

    def get_builtin_type(self):
        return bt.Double

    def box_type(self):
        return DoubleType(self.name, primitive=False)

    def is_assignable(self, other):
        assignable_types = (NumberType, DoubleType,)
        return self.is_subtype(other) or type(other) in assignable_types

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
        if not self.primitive:
            self.supertypes.append(ObjectType())
        else:
            self.supertypes = set()

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
        if not self.primitive:
            self.supertypes.append(ObjectType())
        else:
            self.supertypes = set()

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
            "T", variance=tp.Covariant)])
        self.supertypes.append(ObjectType())


class FunctionType(tp.TypeConstructor, ObjectType):
    def __init__(self, nr_type_parameters: int):
        name = "Function" + str(nr_type_parameters)
        type_parameters = [
            tp.TypeParameter("A" + str(i))
            for i in range(1, nr_type_parameters + 1)
        ] + [tp.TypeParameter("R")]
        self.nr_type_parameters = nr_type_parameters
        super().__init__(name, type_parameters)
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
BigInteger = BigIntegerType()
Char = CharType()
String = StringType()
Boolean = BooleanType()
Array = ArrayType()
NonNothingTypes = [Object, Number, Integer, Short, Long, Byte, Float,
                   Double, BigDecimal, BigInteger, Char, String, Boolean,
                   Array]
