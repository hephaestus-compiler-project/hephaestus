from src.ir.types import Builtin
import src.ir.builtins as bt
import src.ir.types as tp
import src.utils as ut
import random

class TypeScriptBuiltinFactory(bt.BuiltinFactory):
    def get_language(self):
        return "typescript"

    def get_builtin(self):
        return TypeScriptBuiltin

    def get_void_type(self):
        return VoidType()

    def get_any_type(self):
        return ObjectType()

    def get_number_type(self):
        return NumberType(primitive=False)

    def get_boolean_type(self):
        return BooleanType(primitive=False)

    def get_char_type(self):
        return StringType(primitive=False)

    def get_string_type(self):
        return StringType(primitive=False)

    def get_big_integer_type(self):
        return BigIntegerType(primitive=False)

    def get_array_type(self):
        return ArrayType()

    def get_function_type(self, nr_parameters=0):
        return FunctionType(nr_parameters)

    def get_object_type(self):
        return ObjectLowercaseType()

    def get_primitive_types(self):
        return [
            NumberType(primitive=False),
            StringType(primitive=False),
            SymbolType(primitive=False),
            BooleanType(primitive=False),
            BigIntegerType(primitive=False),
            NullType(primitive=False),
            UndefinedType(primitive=False)
        ]

    def get_integer_type(self):
        return NumberType(primitive=False)

    def get_byte_type(self):
        return NumberType(primitive=False)

    def get_short_type(self):
        return NumberType(primitive=False)

    def get_long_type(self):
        return NumberType(primitive=False)

    def get_float_type(self):
        return NumberType(primitive=False)

    def get_double_type(self):
        return NumberType(primitive=False)

    def get_big_decimal_type(self):
        return NumberType(primitive=False)

    def get_null_type(self):
        return NullType(primitive=False)

    def get_non_nothing_types(self): # Overwriting Parent method to add TS-specific types
        types = super().get_non_nothing_types()
        types.extend([
            self.get_null_type(),
            UndefinedType(primitive=False),
            literal_types.get_literal(),
        ])
        return types

    def constant_candidates(self, gen_object):
        from src.ir import ast
        return {
            "NumberLiteralType": lambda etype: ast.IntegerConstant(etype.name),
            "StringLiteralType": lambda etype: ast.StringConstant(etype.name),
        }


class TypeScriptBuiltin(Builtin):
    def __init__(self, name, primitive):
        super().__init__(name)
        self.primitive = primitive

    def __str__(self):
        if not self.is_primitive():
            return str(self.name) + "(typescript-builtin)"
        return str(self.name).lower() + "(typescript-primitive)"

    def is_primitive(self):
        return self.primitive


class ObjectType(TypeScriptBuiltin):
    def __init__(self, name="Object"):
        super().__init__(name, False)


class ObjectLowercaseType(TypeScriptBuiltin):
    def __init__(self, name="object"):
        super().__init__(name, False)
        self.supertypes.append(ObjectType())


class VoidType(TypeScriptBuiltin):
    def __init__(self, name="void"):
        super().__init__(name, False)
        self.supertypes.append(ObjectType())


class NumberType(TypeScriptBuiltin):
    def __init__(self, name="Number", primitive=False):
        super().__init__(name, primitive)
        self.supertypes.append(ObjectType())

    def is_assignable(self, other):
        return isinstance(other, NumberType)

    def box_type(self):
        return NumberType(self.name, primitive=False)

    def get_name(self):
        if self.is_primitive:
            return "number"
        return super().get_name()


class BigIntegerType(TypeScriptBuiltin):
    def __init__(self, name="BigInt", primitive=False):
        super().__init__(name, primitive)
        self.supertypes.append(ObjectType())

    def is_assignable(self, other):
        assignable_types= [BigIntegerType]
        return self.is_subtype(other) or type(other) in assignable_types

    def box_type(self):
        return BigIntegerType(self.name, primitive=False)

    def get_name(self):
        if self.is_primitive:
            return "bigint"
        return super().get_name()


class BooleanType(TypeScriptBuiltin):
    def __init__(self, name="Boolean", primitive=False):
        super().__init__(name, primitive)
        self.supertypes.append(ObjectType())

    def box_type(self):
        return BooleanType(self.name, primitive=False)

    def get_name(self):
        if self.is_primitive:
            return "boolean"
        return super().get_name()


class StringType(TypeScriptBuiltin):
    def __init__(self, name="String", primitive=False):
        super().__init__(name, primitive)
        self.supertypes.append(ObjectType())

    def box_type(self):
        return StringType(self.name, primitive=False)

    def get_name(self):
        if self.is_primitive:
            return "string"
        return super().get_name()


class SymbolType(TypeScriptBuiltin):
    def __init__(self, name="Symbol", primitive=False):
        super().__init__(name, primitive)
        self.supertypes.append(ObjectType())

    def box_type(self):
        return SymbolType(self.name, primitive=False)

    def get_name(self):
        if self.is_primitive():
            return "symbol"
        return super().get_name()


class NullType(ObjectType):
    def __init__(self, name="null", primitive=False):
        super().__init__(name)

    def box_type(self):
        return NullType(self.name)

    def get_name(self):
        return 'null'


class UndefinedType(ObjectType):
    def __init__(self, name="undefined", primitive=False):
        super().__init__(name)

    def box_type(self):
        return UndefinedType(self.name)

    def get_name(self):
        return 'undefined'


class NumberLiteralType(ObjectType):
    def __init__(self, name, primitive=False):
        super().__init__(str(name))

    def get_name(self):
        return self.name;

    def is_string_literal(self):
        return False


class StringLiteralType(ObjectType):
    def __init__(self, name, primitive=False):
        super().__init__(name)

    def get_name(self):
        return '"' + self.name + '"'

    def is_string_literal(self):
        return True


class LiteralTypes:
    def __init__(self, str_limit, num_limit):
        self.literals = []
        self.str_literals = []
        self.num_literals = []
        # Define max number for generated literals
        self.str_limit = str_limit
        self.num_limit = num_limit

    def get_literal(self):
        if ut.random.bool():
            return self.get_string_literal()
        return self.get_number_literal()

    def get_string_literal(self):
        lit = None
        if (len(self.str_literals) == 0 or
                (len(self.str_literals) < self.str_limit and
                ut.random.bool())):
            # If the limit for generated literals 
            # has not been surpassed, we can randomly
            # generate a new one.
            lit = StringLiteralType(ut.random.word().lower())
            self.literals.append(lit)
            self.str_literals.append(lit)
        else:
            lit = random.choice(self.str_literals)
        return lit

    def get_number_literal(self):
        lit = None
        if (len(self.num_literals) == 0 or
                (len(self.num_literals) < self.num_limit and
                ut.random.bool())):
            # If the limit for generated literals 
            # has not been surpassed, we can randomly
            # generate a new one.
            lit = NumberLiteralType(ut.random.integer(-100, 100))
            self.literals.append(lit)
            self.num_literals.append(lit)
        else:
            lit = random.choice(self.num_literals)
        return lit

    def get_generated_literals(self):
        return self.literals

    def get_string_literals(self): # Returns all GENERATED string literals
        return [l for l in self.literals
                if l.is_string_literal()]

    def get_number_literals(self): # Returns all GENERATED number literals
        return [l for l in self.literals
                if not l.is_string_literal()]


class ArrayType(tp.TypeConstructor, ObjectType):
    def __init__(self, name="Array"):
        # In TypeScript, arrays are covariant.
        super().__init__(name, [tp.TypeParameter(
            "T", variance=tp.Covariant)])


class FunctionType(tp.TypeConstructor, ObjectType):
    def __init__(self, nr_type_parameters: int):
        name = "Function" + str(nr_type_parameters)

        # In Typescript, type parameters are covariant as to the return type
        # and contravariant as to the arguments.

        type_parameters = [
            tp.TypeParameter("A" + str(i), tp.Contravariant)
            for i in range(1, nr_type_parameters + 1)
        ] + [tp.TypeParameter("R", tp.Covariant)]
        self.nr_type_parameters = nr_type_parameters
        super().__init__(name, type_parameters)
        self.supertypes.append(ObjectType())


# Literal Types

literal_types = LiteralTypes(10, 10)