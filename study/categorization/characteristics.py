class GeneralCharacteristic():
    name = ""

    def __init__(self, *args):
        self.specific_characteristics = args

    def __repr__(self):
        return "{}({})".format(
            self.name,
            ", ".join([str(s) for s in self.specific_characteristics])
        )

    def __str__(self):
        return self.__repr__()


class StandardFeatures(GeneralCharacteristic):
    name = "Standard features of class-based languages"


class Overriding(GeneralCharacteristic):
    name = "Overriding"


class HigherOrderProgramming(GeneralCharacteristic):
    name = "Higher-order programming"


class StandardLibrary(GeneralCharacteristic):
    name = "Standard Library"


class TypeInference(GeneralCharacteristic):
    name = "Type Inference"


class SpecialTypes(GeneralCharacteristic):
    name = "Special Types"


class Overloading(GeneralCharacteristic):
    name = "Overloading"


class ParametricPolymorphism(GeneralCharacteristic):
    name = "Parametric Polymorphism"


class Subtyping(GeneralCharacteristic):
    name = "Subtyping"


class SpecialLanguageFeatures(GeneralCharacteristic):
    name = "Special Language Features"


class JavaInterop(GeneralCharacteristic):
    name = "Java Interop"


### Specific Characteristics ###
class SpecificCharacteristic:
    general_characteristic = None
    specific_category = None
    is_category = False
    name = ""

    def __init__(self, *args):
        self.specific_characteristics = args

    def __repr__(self):
        if self.specific_characteristics:
            return self.name + "(" + ", ".join(
                [str(s) for s in self.specific_characteristics]) + ")"
        return self.name

    def __str__(self):
        return self.__repr__()


class Classes(SpecificCharacteristic):
    general_characteristic = StandardFeatures
    name = "Classes"


class AbstractClasses(SpecificCharacteristic):
    general_characteristic = StandardFeatures
    name = "Abstract Classes"


class Import(SpecificCharacteristic):
    general_characteristic = StandardFeatures
    name = "Import"


class Enums(SpecificCharacteristic):
    general_characteristic = StandardFeatures
    name = "Enums"


class SealedClasses(SpecificCharacteristic):
    general_characteristic = SpecialLanguageFeatures
    name = "Sealed Classes"


class SAM(SpecificCharacteristic):
    general_characteristic = SpecialLanguageFeatures
    name = "SAM"


class Property(SpecificCharacteristic):
    general_characteristic = SpecialLanguageFeatures
    name = "Property"


class ArithmeticExpressions(SpecificCharacteristic):
    general_characteristic = StandardFeatures
    name = "Arithmetic Expressions"


class Lambdas(SpecificCharacteristic):
    general_characteristic = HigherOrderProgramming
    name = "Lambdas"


class TypeLambdas(SpecificCharacteristic):
    general_characteristic = HigherOrderProgramming
    name = "TypeLambdas"


class FunctionReferences(SpecificCharacteristic):
    general_characteristic = HigherOrderProgramming
    name = "Function Reference"


class ExtensionFunctions(SpecificCharacteristic):
    general_characteristic = HigherOrderProgramming
    name = "Extension Functions"


class This(SpecificCharacteristic):
    general_characteristic = StandardFeatures
    name = "This"


class IntersectionTypes(SpecificCharacteristic):
    general_characteristic = SpecialTypes
    name = "Intersection Types"


class FlowTyping(SpecificCharacteristic):
    general_characteristic = TypeInference
    name = "Flow Typing"


class ParameterizedFunctions(SpecificCharacteristic):
    general_characteristic = ParametricPolymorphism
    name = "Parameterized Function"


class ParameterizedClasses(SpecificCharacteristic):
    general_characteristic = ParametricPolymorphism
    name = "Parameterized Classes"


class Varargs(SpecificCharacteristic):
    general_characteristic = StandardFeatures
    name = "varargs"


class Nullables(SpecificCharacteristic):
    general_characteristic = SpecialTypes
    name = "Nullables"


class BoundedPolymorphism(SpecificCharacteristic):
    general_characteristic = ParametricPolymorphism
    name = "Bounded Polymorphism"
    is_category = True


class Where(SpecificCharacteristic):
    specific_category = BoundedPolymorphism
    name = "Where"


class FBounded(SpecificCharacteristic):
    specific_category = BoundedPolymorphism
    name = "f-bounded"


class VarTypeInference(SpecificCharacteristic):
    general_characteristic = TypeInference
    name = "Variable Type Inference"


class ParamTypeInference(SpecificCharacteristic):
    general_characteristic = TypeInference
    name = "Parameter Type Inference"


class TypeArgsInference(SpecificCharacteristic):
    general_characteristic = TypeInference
    name = "Type Arguments Inference"


class NamedArgs(SpecificCharacteristic):
    general_characteristic = SpecialLanguageFeatures
    name = "Named Args"


class Coroutines(SpecificCharacteristic):
    general_characteristic = SpecialLanguageFeatures
    name = "Coroutines"


class OperatorOverloading(SpecificCharacteristic):
    general_characteristic = SpecialLanguageFeatures
    name = "Operator Overloading"


class ElvisOperator(SpecificCharacteristic):
    general_characteristic = SpecialLanguageFeatures
    name = "Elvis Operator"


class PropertyReference(SpecificCharacteristic):
    general_characteristic = SpecialLanguageFeatures
    name = "Property Reference"


class ExactAnnotation(SpecificCharacteristic):
    general_characteristic = SpecialLanguageFeatures
    name = "Exact Annotation"


class Typealias(SpecificCharacteristic):
    general_characteristic = SpecialLanguageFeatures
    name = "Typealias"


class DataClasses(SpecificCharacteristic):
    general_characteristic = SpecialLanguageFeatures
    name = "Data Classes"


class NullAssertion(SpecificCharacteristic):
    general_characteristic = SpecialLanguageFeatures
    name = "Null Assertion"


class WildCards(SpecificCharacteristic):
    general_characteristic = SpecialLanguageFeatures
    name = "Wildcards"


class Inheritance(SpecificCharacteristic):
    general_characteristic = StandardFeatures
    name = "Inheritance"


class Interfaces(SpecificCharacteristic):
    general_characteristic = StandardFeatures
    name = "Interfaces"


class AccessModifiers(SpecificCharacteristic):
    general_characteristic = StandardFeatures
    name = "Access Modifiers"


class Cast(SpecificCharacteristic):
    general_characteristic = StandardFeatures
    name = "Cast"


class Arrays(SpecificCharacteristic):
    general_characteristic = StandardFeatures
    name = "Arrays"


class Delegation(SpecificCharacteristic):
    general_characteristic = StandardLibrary
    name = "Delegation API"


class Utils(SpecificCharacteristic):
    general_characteristic = StandardLibrary
    name = "Utils"


class FunctionalInterface(SpecificCharacteristic):
    general_characteristic = StandardLibrary
    name = "Functional API"


class Streams(SpecificCharacteristic):
    general_characteristic = StandardLibrary
    name = "Stream API"


class IO(SpecificCharacteristic):
    general_characteristic = StandardLibrary
    name = "IO API"


class Events(SpecificCharacteristic):
    general_characteristic = StandardLibrary
    name = "Events API"


class Collections(SpecificCharacteristic):
    general_characteristic = StandardLibrary
    name = "Collections API"


class Reflection(SpecificCharacteristic):
    general_characteristic = StandardLibrary
    name = "Reflection API"


class Inline(SpecificCharacteristic):
    general_characteristic = SpecialLanguageFeatures
    name = "Inline"


class ImplicitParameters(SpecificCharacteristic):
    general_characteristic = SpecialLanguageFeatures
    name = "Implicit parameters"


class ImplicitDefs(SpecificCharacteristic):
    general_characteristic = SpecialLanguageFeatures
    name = "Implicit defs"


class PatMat(SpecificCharacteristic):
    general_characteristic = SpecialLanguageFeatures
    name = "Pattern Matching"


class ErasedParameters(SpecificCharacteristic):
    general_characteristic = SpecialLanguageFeatures
    name = "Erased Parameters"


class CallByName(SpecificCharacteristic):
    general_characteristic = SpecialLanguageFeatures
    name = "Call by name"


class WithMultipleAssignment(SpecificCharacteristic):
    general_characteristic = SpecialLanguageFeatures
    name = "With Multiple Assignment"


class PrimitiveTypes(SpecificCharacteristic):
    general_characteristic = SpecialTypes
    name = "Primitive Types"


class ParameterizedTypes(SpecificCharacteristic):
    general_characteristic = SpecialTypes
    name = "Parameterized Types"


class FunctionTypes(SpecificCharacteristic):
    general_characteristic = SpecialTypes
    name = "Function Types"


class AlgebraicDataTypes(SpecificCharacteristic):
    general_characteristic = SpecialTypes
    name = "Algebraic Data Types"


class FlexibleTypes(SpecificCharacteristic):
    general_characteristic = SpecialTypes
    name = "Flexible Types"


class DependentTypes(SpecificCharacteristic):
    general_characteristic = SpecialTypes
    name = "Dependent Types"


class Nothing(SpecificCharacteristic):
    general_characteristic = SpecialTypes
    name = "Nothing Type"


class ExistentialTypes(SpecificCharacteristic):
    general_characteristic = SpecialTypes
    name = "Existential Types"


class HigherKindedTypes(SpecificCharacteristic):
    general_characteristic = SpecialTypes
    name = "Higher Kinded Types"


class StaticMethod(SpecificCharacteristic):
    general_characteristic = StandardFeatures
    name = "Static Method"


class NestedDeclaration(SpecificCharacteristic):
    general_characteristic = StandardFeatures
    name = "Nested Declaration"


class TypeAnnotations(SpecificCharacteristic):
    general_characteristic = SpecialLanguageFeatures
    name = "Type Annotations"


class GString(SpecificCharacteristic):
    general_characteristic = SpecialLanguageFeatures
    name = "GString"


class ReferenceTypes(SpecificCharacteristic):
    general_characteristic = SpecialTypes
    name = "Reference Types"


class Variance(SpecificCharacteristic):
    general_characteristic = ParametricPolymorphism
    name = "Variance (use-site or decl-site)"


class DeclVariance(SpecificCharacteristic):
    specific_category = Variance
    name = "Declaration-site variance"


class UseVariance(SpecificCharacteristic):
    specific_category = Variance
    name = "Use-site variance"


class Throws(SpecificCharacteristic):
    general_characteristic = StandardFeatures
    name = "Throws"


class MultiplePackages(SpecificCharacteristic):
    general_characteristic = StandardFeatures
    name = "Multiple Packages"


class TryCatch(SpecificCharacteristic):
    general_characteristic = StandardFeatures
    name = "Try Catch"


class Conditionals(SpecificCharacteristic):
    general_characteristic = StandardFeatures
    name = "Conditionals"


class Loops(SpecificCharacteristic):
    general_characteristic = StandardFeatures
    name = "Loops"


class AnonymousClass(SpecificCharacteristic):
    general_characteristic = StandardFeatures
    name = "Anonymous Class"
