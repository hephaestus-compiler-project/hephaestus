class CharacteristicCategory():
    """
    This is a base class for describing a general category that includes.
    many program characteristics.

    The main general categories of program characteristics are:

      * Standard features of programming languages
      * Features of object-oriented programming languages
      * Features related to parametric polymorphism
      * Features related to higher-order programming,
        and functional programming
      * Use of standard library
      * Features related to type inference
      * Advanced features of type system
      * Other special features
    """

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.__repr__()


class StandardFeatures(CharacteristicCategory):
    """
    This category includes features that can be found in every modern
    programming language (e.g., method calls, arithmetic expressions, binary
    operations, assignments, type casting, etc.).
    """

    name = "Standard features"


class OOPFeatures(CharacteristicCategory):
    """
    This category includes features that are related to object-oriented
    programming, e.g., classes, fields, methods, inheritance, object
    initialization, overriding, etc.
    """

    name = "OOP langauges"


class ParametricPolymorphism(CharacteristicCategory):
    """
    This category includes features related to parametric polymorphism,
    e.g., declaration of parameterized classes / functions, use of
    parameterized types, etc.
    """
    name = "Parametric Polymorphism"


class FunctionalProgramming(CharacteristicCategory):
    """
    This category includes features related to functional programming and
    the use of functions as first-class citizens. For example, use of lambdas,
    declaration of higher-order functions, use of function types, etc.
    """

    name = "Functional Programming"


class StandardLibrary(CharacteristicCategory):
    """
    This category indicates that the input program uses the standard library
    of the language, e.g., collection API (lists, map, sets, etc.).
    """

    name = "Standard Library"


class TypeInference(CharacteristicCategory):
    """
    This category includes related to type inference. For example, the
    input program declares a function whose return type is omitted and inferred
    by the compiler.
    """

    name = "Type Inference"


class SpecialTypes(CharacteristicCategory):
    """
    This category includes features associated with advanced topics of
    the type system of the language. For example, intersection types,
    dependent types, type projections, etc.
    """

    name = "Special features of type systems"


class SpecialFeatures(CharacteristicCategory):
    """
    This category includes other language features that are not related to
    any of the categories above.
    """
    name = "Special features"


class CharacteristicType():
    def __repr__(self):
        return self.name

    def __str__(self):
        return self.__repr__()


class Declaration(CharacteristicType):
    name = "Declarations"


class Expressions(CharacteristicType):
    name = "Expressions"


class Types(CharacteristicType):
    name = "Types"


class Statements(CharacteristicType):
    name = "Statements"


class Misc(CharacteristicType):
    name = "Misc"


class Characteristic():
    name: str = ""
    category: CharacteristicCategory = None
    characteristic_type: CharacteristicType = None
    is_common: bool = False

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.__repr__()


class Overriding(Characteristic):
    name = "Overriding"
    category = OOPFeatures()
    characteristic_type = Declaration()
    is_common = True


class Overloading(Characteristic):
    name = "Overloading"
    category = OOPFeatures()
    characteristic_type = Declaration()
    is_common = True


class Subtyping(Characteristic):
    name = "Subtyping"
    category = StandardFeatures()
    characteristic_type = Types()
    is_common = True


class JavaInterop(Characteristic):
    name = "Java Interop"
    category = SpecialTypes()
    characteristic_type = None
    is_common = True


class AbstractClasses(Characteristic):
    name = "Abstract Classes"
    category = OOPFeatures()
    characteristic_type = Declaration()
    is_common = True


class Import(Characteristic):
    name = "Import"
    category = StandardFeatures()
    characteristic_type = Statements()
    is_common = True


class Enums(Characteristic):
    name = "Enums"
    category = StandardFeatures()
    characteristic_type = Declaration()
    is_common = True


class SealedClasses(Characteristic):
    name = "Sealed Classes"
    category = OOPFeatures()
    characteristic_type = Declaration()
    is_common = True


class SAM(Characteristic):
    name = "Single Abstract Method"
    category = FunctionalProgramming()
    characteristic_type = Declaration()
    is_common = True


class Property(Characteristic):
    name = "Property"
    category = OOPFeatures()
    characteristic_type = Declaration()
    is_common = True


class ArithmeticExpressions(Characteristic):
    name = "Arithmetic Expressions"
    category = StandardFeatures()
    characteristic_type = Expressions()
    is_common = True


class Lambdas(Characteristic):
    name = "Lambdas"
    category = FunctionalProgramming()
    characteristic_type = Expressions()
    is_common = True


class TypeLambdas(Characteristic):
    name = "Type Lambdas"
    category = SpecialFeatures()
    characteristic_type = Types()
    is_common = False


class FunctionReferences(Characteristic):
    name = "Function references"
    category = FunctionalProgramming()
    characteristic_type = Expressions()
    is_common = True


class ExtensionFunctions(Characteristic):
    name = "Extension Fucntions"
    category = SpecialFeatures()
    characteristic_type = Declaration()
    is_common = False


class This(Characteristic):
    name = "this"
    category = OOPFeatures()
    characteristic_type = Expressions()
    is_common = True


class IntersectionTypes(Characteristic):
    name = "Intersection types"
    category = SpecialTypes()
    characteristic_type = Types()
    is_common = False


class UnionTypes(Characteristic):
    name = "Union types"
    category = SpecialTypes()
    characteristic_type = Types()
    is_common = False


class FlowTyping(Characteristic):
    name = "Flow typing"
    category = TypeInference()
    characteristic_type = None
    is_common = False


class ParameterizedFunctions(Characteristic):
    name = "Parameterized Functions"
    category = ParametricPolymorphism()
    characteristic_type = Declaration()
    is_common = True


class ParameterizedClasses(Characteristic):
    name = "Parameterized Classes"
    category = ParametricPolymorphism()
    characteristic_type = Declaration()
    is_common = True


class Varargs(Characteristic):
    name = "varargs"
    category = StandardFeatures()
    characteristic_type = Declaration()
    is_common = True


class Nullables(Characteristic):
    name = "Nullable types"
    category = SpecialFeatures()
    characteristic_type = Types()
    is_common = False


class BoundedPolymorphism(Characteristic):
    name = "Bounded Quantification"
    category = ParametricPolymorphism()
    characteristic_type = Types()
    is_common = True


class Where(Characteristic):
    name = "Multi-bounds"
    category = BoundedPolymorphism()
    characteristic_type = Types()
    is_common = False


class FBounded(Characteristic):
    name = "F-bounds"
    category = BoundedPolymorphism()
    characteristic_type = Types()
    is_common = False


class VarTypeInference(Characteristic):
    name = "Variable type inference"
    category = TypeInference()
    characteristic_type = Declaration()
    is_common = True


class ParamTypeInference(Characteristic):
    name = "Parameter type inference"
    category = TypeInference()
    characteristic_type = Declaration()
    is_common = True


class TypeArgsInference(Characteristic):
    name = "Type argument type inference"
    category = TypeInference()
    characteristic_type = Expressions()
    is_common = True


class NamedArgs(Characteristic):
    name = "Named args"
    category = SpecialFeatures()
    characteristic_type = Declaration()
    is_common = False


class Coroutines(Characteristic):
    name = "Coroutines API"
    category = StandardLibrary()
    characteristic_type = Expressions()
    is_common = False


class OperatorOverloading(Characteristic):
    name = "Operator overloading"
    category = SpecialFeatures()
    characteristic_type = Declaration()
    is_common = False


class ElvisOperator(Characteristic):
    name = "Elvis operator"
    category = SpecialFeatures()
    characteristic_type = Expressions()
    is_common = False


class PropertyReference(Characteristic):
    name = "Property reference"
    category = SpecialFeatures()
    characteristic_type = Expressions()
    is_common = False


class Typedefs(Characteristic):
    name = "Type definitions"
    category = SpecialFeatures()
    characteristic_type = Declaration()
    is_common = False


class DataClasses(Characteristic):
    name = "Data classes"
    category = SpecialFeatures()
    characteristic_type = Declaration()
    is_common = False


class NullAssertion(Characteristic):
    name = "Null assertion"
    category = SpecialFeatures()
    characteristic_type = Expressions()
    is_common = False


class Inheritance(Characteristic):
    name = "Inheritance"
    category = OOPFeatures()
    characteristic_type = Declaration()
    is_common = True


class Interfaces(Characteristic):
    name = "Interfaces"
    category = OOPFeatures()
    characteristic_type = Declaration()
    is_common = True


class AccessModifiers(Characteristic):
    name = "Access modifiers"
    category = OOPFeatures()
    characteristic_type = Declaration()
    is_common = True


class Cast(Characteristic):
    name = "Cast"
    category = StandardFeatures()
    characteristic_type = Expressions()
    is_common = True


class Arrays(Characteristic):
    name = "Arrays"
    category = StandardFeatures()
    characteristic_type = Types()
    is_common = True


class Delegation(Characteristic):
    name = "Delegation"
    category = OOPFeatures()
    characteristic_type = Declaration()
    is_common = False


class Utils(Characteristic):
    name = "Utils API"
    category = StandardLibrary()
    characteristic_type = None
    is_common = False


class FunctionalInterface(Characteristic):
    name = "Function API"
    category = StandardLibrary()
    characteristic_type = None
    is_common = False


class Streams(Characteristic):
    name = "Stream API"
    category = StandardLibrary()
    characteristic_type = None
    is_common = False


class DelegationAPI(Characteristic):
    name = "Delegation API"
    category = StandardLibrary()
    characteristic_type = None
    is_common = False


class Collections(Characteristic):
    name = "Collection API"
    category = StandardLibrary()
    characteristic_type = None
    is_common = True


class Reflection(Characteristic):
    name = "Reflection API"
    category = StandardLibrary()
    characteristic_type = None
    is_common = True


class Inline(Characteristic):
    name = "Inline"
    category = SpecialFeatures()
    characteristic_type = Declaration()
    is_common = False


class ImplicitParameters(Characteristic):
    name = "Implicit parameters"
    category = SpecialFeatures()
    characteristic_type = Declaration()
    is_common = False


class ImplicitDefs(Characteristic):
    name = "Implicit definitions"
    category = SpecialFeatures()
    characteristic_type = Declaration()
    is_common = False


class PatMat(Characteristic):
    name = "Pattern matching"
    category = SpecialFeatures()
    characteristic_type = Expressions()
    is_common = False


class ErasedParameters(Characteristic):
    name = "Erased parameters"
    category = SpecialFeatures()
    characteristic_type = Declaration()
    is_common = False


class CallByName(Characteristic):
    name = "Call by name"
    category = SpecialFeatures()
    characteristic_type = Declaration()
    is_common = False


class WithMultipleAssignment(Characteristic):
    name = "With"
    category = SpecialFeatures()
    characteristic_type = Statements()
    is_common = False


class PrimitiveTypes(Characteristic):
    name = "Primitive types"
    category = SpecialTypes()
    characteristic_type = Types()
    is_common = False


class ParameterizedTypes(Characteristic):
    name = "Parameterized types"
    category = ParametricPolymorphism()
    characteristic_type = Types()
    is_common = False


class FunctionTypes(Characteristic):
    name = "Function types"
    category = FunctionalProgramming()
    characteristic_type = Types()
    is_common = False


class AlgebraicDataTypes(Characteristic):
    name = "Algebraic Data Types"
    category = SpecialTypes()
    characteristic_type = Types()
    is_common = False


class FlexibleTypes(Characteristic):
    name = "Flexible types"
    category = SpecialTypes()
    characteristic_type = Types()
    is_common = False


class DependentTypes(Characteristic):
    name = "Dependent types"
    category = SpecialTypes()
    characteristic_type = Types()
    is_common = False


class ExistentialTypes(Characteristic):
    name = "Existential types"
    category = SpecialTypes()
    characteristic_type = Types()
    is_common = False


class HigherKindedTypes(Characteristic):
    name = "Higher-kinded types"
    category = ParametricPolymorphism()
    characteristic_type = Types()
    is_common = False


class StaticMethod(Characteristic):
    name = "Static Method"
    category = OOPFeatures()
    characteristic_type = Declaration()
    is_common = False


class NestedDeclaration(Characteristic):
    name = "Nested declarations"
    category = StandardFeatures()
    characteristic_type = Declaration()
    is_common = True


class TypeAnnotations(Characteristic):
    name = "Type annotations"
    category = SpecialFeatures()
    characteristic_type = Declaration()
    is_common = False


class ReferenceTypes(Characteristic):
    name = "Reference types"
    category = SpecialFeatures()
    characteristic_type = Types()
    is_common = False


class DeclVariance(Characteristic):
    name = "Declaration-site variance"
    category = ParametricPolymorphism()
    characteristic_type = Types()
    is_common = False


class UseVariance(Characteristic):
    name = "Use-site variance"
    category = ParametricPolymorphism()
    characteristic_type = Types()
    is_common = False


class TryCatch(Characteristic):
    name = "Try/Catch"
    category = StandardFeatures()
    characteristic_type = Statements()
    is_common = True


class Conditionals(Characteristic):
    name = "Conditionals"
    category = StandardFeatures()
    characteristic_type = Expressions()
    is_common = True


class Loops(Characteristic):
    name = "Loops"
    category = StandardFeatures()
    characteristic_type = Statements()
    is_common = True


class AnonymousClass(Characteristic):
    name = "Anonymous classes"
    category = OOPFeatures()
    characteristic_type = Expressions()
    is_common = True


class Nothing(Characteristic):
    name = "Nothing"
    category = SpecialTypes()
    characteristic_type = Types()
    is_common = False


class DefaultInitializer(Characteristic):
    name = "Default Initializer"
    category = SpecialFeatures()
    characteristic_type = Expressions()
    is_common = False


class TypeProjections(Characteristic):
    name = "Type Projection"
    category = SpecialTypes()
    characteristic_type = Types()
    is_common = False
