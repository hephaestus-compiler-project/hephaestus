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

    name = "OOP features"


class ParametricPolymorphism(CharacteristicCategory):
    """
    This category includes features related to parametric polymorphism,
    e.g., declaration of parameterized classes / functions, use of
    parameterized types, etc.
    """
    name = "Parametric polymorphism"


class FunctionalProgramming(CharacteristicCategory):
    """
    This category includes features related to functional programming and
    the use of functions as first-class citizens. For example, use of lambdas,
    declaration of higher-order functions, use of function types, etc.
    """

    name = "Functional programming"


class StandardLibrary(CharacteristicCategory):
    """
    This category indicates that the input program uses the standard library
    of the language, e.g., collection API (lists, map, sets, etc.).
    """

    name = "Standard library"


class TypeInference(CharacteristicCategory):
    """
    This category includes related to type inference. For example, the
    input program declares a function whose return type is omitted and inferred
    by the compiler.
    """

    name = "Type inference"


class TypeSystem(CharacteristicCategory):
    """
    This category includes features associated with the type system of
    the language. For example, subtyping, intersection types,
    dependent types, type projections, etc.
    """

    name = "Type system features"


class SpecialFeatures(CharacteristicCategory):
    """
    This category includes other language features that are not related to
    any of the categories above.
    """
    name = "Other"


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
    """
    The test case contains a class that overrides a specific method or field.
    """
    name = "Overriding"
    category = OOPFeatures()
    characteristic_type = Declaration()
    is_common = True


class Overloading(Characteristic):
    """
    The test case contains overloaded methods.
    """
    name = "Overloading"
    category = OOPFeatures()
    characteristic_type = Declaration()
    is_common = True


class SecondaryConstructor(Characteristic):
    """
    The test case contains a secondary constructor (Kotlin only).
    """
    name = "Secondary constructor"
    category = OOPFeatures()
    characteristic_type = Declaration()
    is_common = False


class Subtyping(Characteristic):
    """
    The test case uses types for which the subtyping relation holds.

    Example:
      class A {}
      class B extends A {}

      val x: A = new B() // here we have subtyping
    """
    name = "Subtyping"
    category = TypeSystem()
    characteristic_type = Types()
    is_common = True


class JavaInterop(Characteristic):
    """
    The test case is written in a language other than Java, but uses part of
    code written in Java (e.g., a library, imports a Java class, uses the
    standard library of Java, etc.)
    """
    name = "Java Interop"
    category = SpecialFeatures()
    characteristic_type = None
    is_common = True


class Import(Characteristic):
    """
    The test cases imports another source file.
    """
    name = "Import"
    category = StandardFeatures()
    characteristic_type = Statements()
    is_common = True


class Enums(Characteristic):
    """
    The test case declares an enumeration.
    """
    name = "Enums"
    category = StandardFeatures()
    characteristic_type = Declaration()
    is_common = True


class SealedClasses(Characteristic):
    """
    The test case declares a sealed class.
    """
    name = "Sealed Classes"
    category = OOPFeatures()
    characteristic_type = Declaration()
    is_common = True


class SAM(Characteristic):
    """
    The test case defines a Single Abstract Method (SAM) type.

    For more details see:

    https://stackoverflow.com/questions/17913409/what-is-a-sam-type-in-java
    """
    name = "Single Abstract Method"
    category = FunctionalProgramming()
    characteristic_type = Declaration()
    is_common = True


class Property(Characteristic):
    """
    The test case defines a property.
    """
    name = "Property"
    category = OOPFeatures()
    characteristic_type = Declaration()
    is_common = True


class ArithmeticExpressions(Characteristic):
    """
    The test case contains arithmetic expressions (e.g., a + b).
    """
    name = "Arithmetic Expressions"
    category = StandardFeatures()
    characteristic_type = Expressions()
    is_common = True


class AugmentedAssignmentOperator(Characteristic):
    """
    The test case contains an augmented assignment operator (x += 1).
    """
    name = "Augmented Assignment Operator"
    category = StandardFeatures()
    characteristic_type = Expressions()
    is_common = True


class Lambdas(Characteristic):
    """
    The test case contains a lambda expression.
    """
    name = "Lambdas"
    category = FunctionalProgramming()
    characteristic_type = Expressions()
    is_common = True


class TypeLambdas(Characteristic):
    """
    The test case contains a type lambda expression (Scala only).
    """
    name = "Type Lambdas"
    category = TypeSystem()
    characteristic_type = Types()
    is_common = False


class FunctionReferences(Characteristic):
    """
    The test contains a function reference expression.

    Example:
       class X { static String foo() }
       bar(X::foo) // here we have the function reference
    """
    name = "Function references"
    category = FunctionalProgramming()
    characteristic_type = Expressions()
    is_common = True


class ExtensionFunctions(Characteristic):
    """
    The test case defines an extension function or property.

    For more details:

    https://kotlinlang.org/docs/extensions.html
    """
    name = "Extensions"
    category = SpecialFeatures()
    characteristic_type = Declaration()
    is_common = False


class This(Characteristic):
    """
    The test contains a 'this' expression.
    """
    name = "this"
    category = OOPFeatures()
    characteristic_type = Expressions()
    is_common = True


class IntersectionTypes(Characteristic):
    """
    The test case makes use of intersection types.
    """
    name = "Intersection types"
    category = TypeSystem()
    characteristic_type = Types()
    is_common = False


class UnionTypes(Characteristic):
    """
    The test case makes use of union types.
    """
    name = "Union types"
    category = TypeSystem()
    characteristic_type = Types()
    is_common = False


class FlowTyping(Characteristic):
    """
    The test case makes use of implicit casts made by the compiler.

    For more details see:
    https://en.wikipedia.org/wiki/Flow-sensitive_typing
    """
    name = "Flow typing"
    category = TypeInference()
    characteristic_type = None
    is_common = False


class ParameterizedFunctions(Characteristic):
    """
    The test case declares a parameterized function.
    """
    name = "Parameterized Functions"
    category = ParametricPolymorphism()
    characteristic_type = Declaration()
    is_common = True


class ParameterizedClasses(Characteristic):
    """
    The test case declares a parameterized class.
    """
    name = "Parameterized Classes"
    category = ParametricPolymorphism()
    characteristic_type = Declaration()
    is_common = True


class Varargs(Characteristic):
    """
    The test case contains a method that takes variable arguments.

    Example:
      String foo(String x, Integer... y) // The '...' in Java denotes a vararg.
    """
    name = "Variable arguments"
    category = StandardFeatures()
    characteristic_type = Declaration()
    is_common = True


class Nullables(Characteristic):
    """
    The test case uses nullable types (Kotlin only).
    """
    name = "Nullable types"
    category = TypeSystem()
    characteristic_type = Types()
    is_common = False


class BoundedPolymorphism(Characteristic):
    """
    The test case defines a type parameter with a bound.

    Example:
       class X<T extends Object> {}
    """
    name = "Bounded Quantification"
    category = ParametricPolymorphism()
    characteristic_type = Types()
    is_common = True


class MultiBounds(Characteristic):
    """
    The test case defines a type parameter with multiple bounds.
    """
    name = "Multi-bounds"
    category = BoundedPolymorphism()
    characteristic_type = Types()
    is_common = False


class FBounded(Characteristic):
    """
    The test case contains a type parameter with a recursive bound.

    Example:
      class X<T extends X<T>> {}
    """
    name = "F-bounds"
    category = BoundedPolymorphism()
    characteristic_type = Types()
    is_common = True


class VarTypeInference(Characteristic):
    """
    The test contains a variable declaration whose declared type is omitted.

    Example:
       val x = "foo" // The inferred type is String.
    """
    name = "Variable type inference"
    category = TypeInference()
    characteristic_type = Declaration()
    is_common = True


class BuilderInference(Characteristic):
    """
    The test contains BuilderInference annotations (kotlin only).

    Example:
       fun <K> foo(@BuilderInference block: Inv<K>.() -> Unit) {}
    """
    name = "Variable type inference"
    category = TypeInference()
    characteristic_type = Declaration()
    is_common = False


class ParamTypeInference(Characteristic):
    """
    The test case contains a function or lambda whose parameter types are
    omitted.
    """
    name = "Parameter type inference"
    category = TypeInference()
    characteristic_type = Declaration()
    is_common = True


class TypeArgsInference(Characteristic):
    """
    The test case instantiates a type constructor whose type arguments
    are omitted.

    Example:
      class X<T> {}
      X<String> x = new X<>(); // Here 'X<>', we have type argument inference.
    """
    name = "Type argument type inference"
    category = TypeInference()
    characteristic_type = Expressions()
    is_common = True


class NamedArgs(Characteristic):
    """
    The test case contains a function that takes named arguments.

    Example:
       String foo(String x, String y = "foo")
    """
    name = "Named args"
    category = SpecialFeatures()
    characteristic_type = Declaration()
    is_common = False


class Coroutines(Characteristic):
    """
    The test case uses the Coroutines API (Kotlin only).
    """
    name = "Coroutines API"
    category = StandardLibrary()
    characteristic_type = Expressions()
    is_common = False


class OperatorOverloading(Characteristic):
    """
    The test case overloads an operator.
    """
    name = "Operator overloading"
    category = Overloading()
    characteristic_type = Declaration()
    is_common = False


class ElvisOperator(Characteristic):
    """
    The test case contains an elvis expression (Kotlin, Groovy only).
    """
    name = "Elvis operator"
    category = SpecialFeatures()
    characteristic_type = Expressions()
    is_common = False


class SafeNavigationOperator(Characteristic):
    """
    Or Safe Call Operator.
    The test case contains an safe navigation operator (Kotlin, Groovy only).
    """
    name = "Safe navigation operator"
    category = SpecialFeatures()
    characteristic_type = Expressions()
    is_common = False


class PropertyReference(Characteristic):
    """
    The test case contains a property reference.
    Note this is the same as function references, but it's for properties
    (Kotlin only).
    """
    name = "Property reference"
    category = OOPFeatures()
    characteristic_type = Expressions()
    is_common = False


class Typedefs(Characteristic):
    """
    The test case defines a type (Scala, Kotlin only).

    Example:
      type MyType = List[(Int, Double)]
    """
    name = "Type definitions"
    category = TypeSystem()
    characteristic_type = Declaration()
    is_common = False


class DataClasses(Characteristic):
    """
    The test case declares a data class (Kotlin only)

    For more details:
      https://kotlinlang.org/docs/data-classes.html
    """
    name = "Data classes"
    category = OOPFeatures()
    characteristic_type = Declaration()
    is_common = False


class ValueClasses(Characteristic):
    """
    The test case declares a value class (Scala only)
    """
    name = "Value classes"
    category = OOPFeatures()
    characteristic_type = Declaration()
    is_common = False


class NullAssertion(Characteristic):
    """
    The test case contains a null assertion expression (Kotlin only).

    For more details:
      https://www.baeldung.com/kotlin/not-null-assertion
    """
    name = "Null assertion"
    category = SpecialFeatures()
    characteristic_type = Expressions()
    is_common = False


class Inheritance(Characteristic):
    """
    The test case declares a class that inherits from another.
    """
    name = "Inheritance"
    category = OOPFeatures()
    characteristic_type = Declaration()
    is_common = True


class MultipleImplements(Characteristic):
    """
    The test case contains a class that implements multiple interfaces.

    Example:
      interface A {}
      interface B {}
      class C implements A, B {}
    """
    name = "Multiple implements"
    category = OOPFeatures()
    characteristic_type = Declaration()
    is_common = True


class AccessModifiers(Characteristic):
    """
    The test case makes use of access modifiers keywords (e.g., private).
    """
    name = "Access modifiers"
    category = OOPFeatures()
    characteristic_type = Declaration()
    is_common = True


class Singleton(Characteristic):
    """
    The test case declares a singleton object (Scala and Kotlin only).
    """
    name = "Singleton object"
    category = OOPFeatures()
    characteristic_type = Declaration()
    is_common = False


class Cast(Characteristic):
    """
    The test case contains a cast expression.
    """
    name = "Cast"
    category = StandardFeatures()
    characteristic_type = Expressions()
    is_common = True


class Arrays(Characteristic):
    """
    The test case declares a variable/parameter whose type is Array.

    Example:
      String foo(String[] args)
    """
    name = "Arrays"
    category = StandardFeatures()
    characteristic_type = Types()
    is_common = True


class Delegation(Characteristic):
    """
    The test case uses the delegation functionality (Kotlin only).

    For more details:
    https://kotlinlang.org/docs/delegation.html
    """
    name = "Delegation"
    category = OOPFeatures()
    characteristic_type = Declaration()
    is_common = False


class FunctionAPI(Characteristic):
    """
    The test case uses the function API from the standard library of Java.
    """
    name = "Function API"
    category = StandardLibrary()
    characteristic_type = None
    is_common = True


class Streams(Characteristic):
    """
    The test case uses the Stream API from the standard library of Java.
    """
    name = "Stream API"
    category = StandardLibrary()
    characteristic_type = None
    is_common = False


class DelegationAPI(Characteristic):
    """
    The test case uses the Delegation API from the standard library of Groovy.
    """
    name = "Delegation API"
    category = StandardLibrary()
    characteristic_type = None
    is_common = False


class Collections(Characteristic):
    """
    The test case uses the collection API (e.g., it uses list types, it)
    creates sets, and more).
    """
    name = "Collection API"
    category = StandardLibrary()
    characteristic_type = None
    is_common = True


class Reflection(Characteristic):
    """
    The test case us the reflection API.

    Example:

      class A {}
      val x = new A()
      x.getClass() // here we are using the reflection API.
    """
    name = "Reflection API"
    category = StandardLibrary()
    characteristic_type = None
    is_common = True


class Inline(Characteristic):
    """
    The test case uses the inline keyword (Scala and Kotlin only).
    """
    name = "Inline"
    category = SpecialFeatures()
    characteristic_type = Declaration()
    is_common = False


class Implicits(Characteristic):
    name = "Implicits"
    category = SpecialFeatures()
    characteristic_type = Declaration()
    is_common = False


class ImplicitParameters(Characteristic):
    """
    The test case contains implicit parameters (Scala only).
    """
    name = "Implicit parameters"
    category = Implicits()
    characteristic_type = Declaration()
    is_common = False


class ImplicitDefs(Characteristic):
    """
    The test case contains implicit definitions (Scala only).
    """
    name = "Implicit definitions"
    category = Implicits()
    characteristic_type = Declaration()
    is_common = False


class PatMat(Characteristic):
    """
    The test case contains pattern matching (Scala only).

    For more details:
    https://docs.scala-lang.org/tour/pattern-matching.html
    """
    name = "Pattern matching"
    category = SpecialFeatures()
    characteristic_type = Expressions()
    is_common = False


class ErasedParameters(Characteristic):
    """
    The test case contains erased parameters (Scala only).
    """
    name = "Erased parameters"
    category = SpecialFeatures()
    characteristic_type = Declaration()
    is_common = False


class CallByName(Characteristic):
    """
    The test case contains call-by-name arguments (Scala only).
    """
    name = "Call by name"
    category = SpecialFeatures()
    characteristic_type = Declaration()
    is_common = False


class WithMultipleAssignment(Characteristic):
    """
    The test case performs multiple assignments through the with pattern
    (Groovy only).
    """
    name = "With"
    category = SpecialFeatures()
    characteristic_type = Statements()
    is_common = False


class PrimitiveTypes(Characteristic):
    """
    The test case declares a variable/parameter whose type is primitive
    (Java and Groovy only).
    """
    name = "Primitive types"
    category = TypeSystem()
    characteristic_type = Types()
    is_common = False


class WildCardType(Characteristic):
    """
    The test case contains a parameterized type that comes from the
    application of a type constructor with a wildcard type, e.g. A<?>.
    """
    name = "Wildcard Type"
    category = TypeSystem()
    characteristic_type = Types()
    is_common = True


class ParameterizedTypes(Characteristic):
    """
    The test case declares a variable/parameter whose type is parameterized.
    """
    name = "Parameterized types"
    category = ParametricPolymorphism()
    characteristic_type = Types()
    is_common = True


class FunctionTypes(Characteristic):
    """
    The test case declares a variable/parameter whose type is a function type.
    """
    name = "Function types"
    category = FunctionalProgramming()
    characteristic_type = Types()
    is_common = True


class AlgebraicDataTypes(Characteristic):
    """
    The test contains algebraic data types (Scala only).

    For more details:
    https://alvinalexander.com/scala/fp-book/algebraic-data-types-adts-in-scala/
    """
    name = "Algebraic Data Types"
    category = TypeSystem()
    characteristic_type = Types()
    is_common = False


class DependentTypes(Characteristic):
    """
    The test case declares a variable/parameter whose type is a dependent type
    (Scala only).
    """
    name = "Dependent types"
    category = TypeSystem()
    characteristic_type = Types()
    is_common = False


class HigherKindedTypes(Characteristic):
    """
    The test cases uses higher-kinded types (Scala only).
    """
    name = "Higher-kinded types"
    category = ParametricPolymorphism()
    characteristic_type = Types()
    is_common = False


class StaticMethod(Characteristic):
    """
    The test case declares a static method (Groovy and Java only).
    """
    name = "Static Method"
    category = OOPFeatures()
    characteristic_type = Declaration()
    is_common = False


class NestedClasses(Characteristic):
    """
    The test case contains nested declarations (e.g., a class is declared
    inside another class).

    Example:
       class X {
         class Y {}
       }
    """
    name = "Nested classes"
    category = OOPFeatures()
    characteristic_type = Declaration()
    is_common = True


class TypeAnnotations(Characteristic):
    """
    The test case contains type annotations (Java only).
    """
    name = "Type annotations"
    category = SpecialFeatures()
    characteristic_type = Declaration()
    is_common = False


class ReferenceTypes(Characteristic):
    """
    The test case contains reference types (Java only).
    """
    name = "Reference types"
    category = SpecialFeatures()
    characteristic_type = Types()
    is_common = False


class DeclVariance(Characteristic):
    """
    The test case declares a type constructor with variant type arguments
    (Kotlin and Scala only).

    Example:
       class X<out T> // covariant type parameter 'T'.
    """
    name = "Declaration-site variance"
    category = ParametricPolymorphism()
    characteristic_type = Types()
    is_common = False


class UseVariance(Characteristic):
    """
    The test cases uses a parameterized type with variant type arguments
    (Kotlin, Groovy and Java only).

    Example:
        class X<T> {}
        String foo(X<? extends Number> arg)
    """
    name = "Use-site variance"
    category = ParametricPolymorphism()
    characteristic_type = Types()
    is_common = True


class TryCatch(Characteristic):
    """
    The test case contains try/catch statements or handles exceptions.
    """
    name = "Try/Catch"
    category = StandardFeatures()
    characteristic_type = Statements()
    is_common = True


class Conditionals(Characteristic):
    """
    The test case contains conditionals (e.g., if, switch, ternary operators).
    """
    name = "Conditionals"
    category = StandardFeatures()
    characteristic_type = Expressions()
    is_common = True


class Loops(Characteristic):
    """
    The test case contains loops (e.g., for, while).
    """
    name = "Loops"
    category = StandardFeatures()
    characteristic_type = Statements()
    is_common = True


class AnonymousClass(Characteristic):
    """
    The test cases declares an anonymous class.
    """
    name = "Anonymous classes"
    category = OOPFeatures()
    characteristic_type = Expressions()
    is_common = True


class Nothing(Characteristic):
    """
    The test case handles the special type 'Nothing' (Scala, Kotlin only).
    """
    name = "Nothing"
    category = TypeSystem()
    characteristic_type = Types()
    is_common = False


class DefaultInitializer(Characteristic):
    """
    The test case contains a default initializer (Scala only).

    Example:
      val x: String = _
    """
    name = "Default Initializer"
    category = SpecialFeatures()
    characteristic_type = Expressions()
    is_common = False


class TypeProjections(Characteristic):
    """
    The test case contains type projections (Scala only).

    For more details:
    https://docs.scala-lang.org/overviews/quasiquotes/type-details.html
    """
    name = "Type Projection"
    category = TypeSystem()
    characteristic_type = Types()
    is_common = False


class IOAPI(Characteristic):
    """
    The test case contains IO API calls.
    """
    name = "IO API"
    category = StandardLibrary()
    characteristic_type = None
    is_common = True
