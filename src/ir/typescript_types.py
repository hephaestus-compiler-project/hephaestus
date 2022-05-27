from src.ir.types import Builtin


import src.ir.builtins as bt
import src.ir.types as tp

class TypeScriptBuiltinFactory(bt.BuiltinFactory):
    def get_language(self):
        return "typescript" 

    # ! All types below are java types.
    # TODO: Change them to typescript one by one

    def get_builtin(self):
        return JavaBuiltin

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
        return DoubleType(primitive=False)

    def get_boolean_type(self):
        return BooleanType(primitive=False)

    def get_char_type(self):
        return CharType(primitive=False)

    def get_string_type(self):
        return StringType()

    def get_array_type(self):
        return ArrayType()

    def get_big_integer_type(self):
        return IntegerType(primitive=False)

    def get_function_type(self, nr_parameters=0):
        return FunctionType(nr_parameters)


# ! All types below are java types.

class JavaBuiltin(Builtin):
    def __init__(self, name, primitive):
        super().__init__(name)
        self.primitive = primitive

    def __str__(self):
        if not self.is_primitive():
            return str(self.name) + "(java-builtin)"
        return str(self.name).lower() + "(java-primitive)"

    def is_primitive(self):
        return self.primitive

    def box_type(self):
        raise NotImplementedError('box_type() must be implemented')


class ObjectType(JavaBuiltin):
    def __init__(self, name="Object"):
        super().__init__(name, False)

    def get_builtin_type(self):
        return bt.Any

    def box_type(self):
        return self


class VoidType(JavaBuiltin):
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
            self.supertypes = []

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
        # In Java, arrays are covariant.
        super().__init__(name, [tp.TypeParameter(
            "T", variance=tp.Covariant)])
        self.supertypes.append(ObjectType())


class FunctionType(tp.TypeConstructor):
    def __init__(self, nr_type_parameters: int):
        name = "Function" + str(nr_type_parameters)
        type_parameters = [
            tp.TypeParameter("A" + str(i))
            for i in range(1, nr_type_parameters + 1)
        ] + [tp.TypeParameter("R")]
        self.nr_type_parameters = nr_type_parameters
        super().__init__(name, type_parameters)