# pylint: disable=abstract-method
from abc import ABC, abstractmethod

from src.ir.types import Builtin, TypeConstructor, TypeParameter


class BuiltinFactory(ABC):
    @abstractmethod
    def get_language(self):
        pass

    @abstractmethod
    def get_builtin(self):
        pass

    @abstractmethod
    def get_void_type(self):
        pass

    @abstractmethod
    def get_any_type(self):
        pass

    @abstractmethod
    def get_number_type(self):
        pass

    @abstractmethod
    def get_integer_type(self):
        pass

    @abstractmethod
    def get_byte_type(self):
        pass

    @abstractmethod
    def get_short_type(self):
        pass

    @abstractmethod
    def get_long_type(self):
        pass

    @abstractmethod
    def get_float_type(self):
        pass

    @abstractmethod
    def get_double_type(self):
        pass

    @abstractmethod
    def get_big_decimal_type(self):
        pass

    @abstractmethod
    def get_big_integer_type(self):
        pass

    @abstractmethod
    def get_boolean_type(self):
        pass

    @abstractmethod
    def get_char_type(self):
        pass

    @abstractmethod
    def get_string_type(self):
        pass

    @abstractmethod
    def get_array_type(self):
        pass

    @abstractmethod
    def get_function_type(self, nr_parameters=0):
        pass

    @abstractmethod
    def get_null_type(self):
        pass

    def get_non_nothing_types(self):
        return [
            self.get_any_type(),
            self.get_number_type(),
            self.get_integer_type(),
            self.get_byte_type(),
            self.get_short_type(),
            self.get_long_type(),
            self.get_float_type(),
            self.get_double_type(),
            self.get_big_decimal_type(),
            self.get_big_integer_type(),
            self.get_boolean_type(),
            self.get_char_type(),
            self.get_string_type(),
            self.get_array_type(),
        ]

    def get_number_types(self):
        return [
            self.get_byte_type(),
            self.get_short_type(),
            self.get_integer_type(),
            self.get_long_type(),
            self.get_float_type(),
            self.get_double_type(),
            self.get_big_decimal_type(),
            self.get_big_integer_type(),
        ]

    def get_function_types(self, max_parameters):
        return [self.get_function_type(i) for i in range(0, max_parameters+1)]

    def get_nothing(self):
        raise NotImplementedError

    def get_constant_candidates(self):
        """ Overwrite this function to update the generator
        constants with language-specific.
        """
        return {}


class AnyType(Builtin):
    def __init__(self, name="Any"):
        super().__init__(name)


class NothingType(Builtin):
    def __init__(self, name="Nothing"):
        super().__init__(name)

    def is_subtype(self, other):
        return True


class VoidType(AnyType):
    def __init__(self, name="Void"):
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


class BigIntegerType(NumberType):
    def __init__(self, name="BigInteger"):
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


class BigDecimalType(NumberType):
    def __init__(self, name="BigDecimal"):
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


class ArrayType(TypeConstructor):
    def __init__(self, name="Array"):
        super().__init__(name, [TypeParameter("T")])
        self.supertypes.append(AnyType())


class FunctionType(TypeConstructor):
    def __init__(self, nr_type_parameters: int):
        name = "Function" + str(nr_type_parameters)
        type_parameters = [
            TypeParameter("A" + str(i))
            for i in range(1, nr_type_parameters + 1)
        ] + [TypeParameter("R")]
        self.nr_type_parameters = nr_type_parameters
        super().__init__(name, type_parameters)
        self.supertypes.append(AnyType())


### WARNING: use them only for testing ###
Any = AnyType()
Nothing = NothingType()
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
NonNothingTypes = [Any, Number, Integer, Short, Long, Byte, Float,
                   Double, Char, String, Boolean, BigDecimal, BigInteger,
                   Array]
