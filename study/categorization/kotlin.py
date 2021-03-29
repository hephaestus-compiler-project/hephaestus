from bug import KotlinBug
import categories as ct
import characteristics as pc
import symptoms as sy
import root_causes as rc


kotlin_iter1 = [
    KotlinBug(
        "1.KT-1934",
        [pc.Inheritance()],
        False,
        sy.Runtime(sy.WrongResult()),
        rc.MissingCase(),
        ct.Declarations(),  # -- During Override Resolution
        4
    ),
    KotlinBug(
        "2.KT-4814",
        [pc.ArithmeticExpressions(), pc.AugmentedAssignmentOperator()],
        False,
        sy.Runtime(sy.VerifyError()),
        rc.MissingCase(),
        ct.TypeExpression(),
        4
    ),
    KotlinBug(
        "3.KT-42175",
        [
            pc.Lambdas(),
            pc.Collections(),
            pc.This(),
            pc.AugmentedAssignmentOperator()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Inference(),  # "type variable substitution"
        8
    ),
    KotlinBug(
        "4.KT-10244",
        [pc.FlowTyping(),
         pc.Conditionals()],
        False,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.Declarations(),
        4
    ),
    KotlinBug(
        "5.KT-10472",
        [pc.Overloading(), pc.Varargs(),
         pc.ParameterizedClasses(),
         pc.ParameterizedFunctions(),
         pc.ParameterizedTypes()],
        True,
        sy.Runtime(sy.WrongResult()),
        rc.IncorrectSequence(),
        ct.Resolution(),
        8
    ),
    KotlinBug(
        "6.KT-7485",
        [pc.MultiBounds(),
         pc.BoundedPolymorphism(),
         pc.ParameterizedFunctions(),
         pc.ParameterizedClasses(),
         pc.Nullables(),
         pc.Subtyping()],
        False,
        sy.Runtime(sy.NullPointerException()),
        rc.IncorrectComputation(), # IncorrectCondition
        ct.TypeComparison(), # Declarations
        11
    ),
    KotlinBug(
        "7.KT-23748",
        [pc.ParameterizedFunctions(),
         pc.Subtyping(),
         pc.Nullables(),
         pc.ElvisOperator()],
        True,
        sy.CompileTimeError(),
        rc.IncorrectComputation(),
        ct.Inference(),  # constraint solving # TODO without fix
        9
    ),
    KotlinBug(
        "8.KT-22728",
        [pc.Lambdas(),
         pc.ExtensionFunctions(),
         pc.Typedefs(),
         pc.Import(),
         pc.FunctionTypes()],
        True,
        sy.CompileTimeError(),
        rc.WrongParams(),
        ct.Environment(),
        11
    ),
    KotlinBug(
        "9.KT-10711",
        [pc.ParameterizedFunctions(),
         pc.ParameterizedClasses(),
         pc.Collections(),
         pc.FunctionReferences()],
        True,
        sy.CompileTimeError(),
        rc.InsufficientAlgorithmImplementation(),
        ct.Inference(),  # constraint solving
        6
    ),
    KotlinBug(
        "10.KT-37249",
        [pc.Conditionals(), pc.TryCatch(), pc.Lambdas()],
        True,
        sy.CompileTimeError(),
        rc.InsufficientAlgorithmImplementation(),
        ct.Inference(),  # constraint solving
        7
    ),
    KotlinBug(
        "11.KT-11468",
        [pc.ParameterizedClasses(), pc.DeclVariance(),
         pc.ParameterizedTypes(),
         pc.Subtyping()],
        True,
        sy.InternalCompilerError(),
        rc.DesignIssue(),
        ct.TypeComparison(),
        6
    ),
    KotlinBug(
        "12.KT-6014",
        [pc.Overriding(), pc.Inheritance(), pc.Delegation()],
        True,
        sy.CompileTimeError(),
        rc.IncorrectComputation(),
        ct.Resolution(),
        7
    ),
    KotlinBug(
        "13.KT-12044",
        [pc.Conditionals(), pc.PropertyReference(), pc.ParameterizedTypes()],
        True,
        sy.CompileTimeError(),
        rc.WrongParams(),
        ct.Resolution(),
        8
    ),
    KotlinBug(
        "14.KT-4334",
        [pc.Lambdas(), pc.Loops(), pc.Collections()],
        False,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.OtherSemanticChecking(), # -- BREAK_OR_CONTINUE_JUMPS_ACROSS_FUNCTION_BOUNDARY
        7
    ),
    KotlinBug(
        "15.KT-32184",
        [pc.Lambdas(), pc.DataClasses(), pc.FunctionTypes(), pc.Nullables()],
        True,
        sy.InternalCompilerError(),
        rc.WrongParams(),
        ct.Resolution(),
        12
    ),
    KotlinBug(
        "16.KT-10197",
        [pc.Overriding(), pc.Inheritance(), pc.Delegation()],
        False,
        sy.Runtime(sy.AbstractMethodError()),
        rc.MissingCase(),
        ct.Declarations(), # -- During Override Resolution
        #16
        12
    ),
    KotlinBug(
        "17.KT-41693",
        [pc.Conditionals(), pc.Import(),
         pc.Nullables(),
         pc.JavaInterop()],
        True,
        sy.Runtime(sy.NullPointerException()),
        rc.MissingCase(),
        ct.Approximation(),
        16
    ),
    KotlinBug(
        "18.KT-44420",
        [pc.FlexibleTypes(),
         pc.Collections(),
         pc.VarTypeInference(),
         pc.JavaInterop()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Approximation(),
        9
    ),
    KotlinBug(
        "19.KT-35602",
        [pc.ParameterizedClasses(),
         pc.FBounded(),
         pc.Nullables(),
         pc.WildCardType(),
         pc.ParameterizedTypes(),
         pc.NullAssertion()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Approximation(),
        6
    ),
    KotlinBug(
        "20.KT-6992",
        [pc.Overloading(),
         pc.ParameterizedClasses(),
         pc.Delegation(),  # ConstructorDelegation
         pc.This()],
        False,
        sy.MisleadingReport(),
        rc.InsufficientAlgorithmImplementation(),
        ct.Resolution(),
        3
    ),
]


kotlin_iter2 = [
    KotlinBug(
        "1.KT-31102",
        # pc.ParamTypeInference(), pc.This()
        [pc.Lambdas(), pc.FunctionReferences(),
         pc.ParameterizedFunctions(), pc.FunctionTypes],
        True,
        sy.CompileTimeError(),
        rc.InsufficientAlgorithmImplementation(),
        ct.Inference(),  # constraint solving
        8
    ),
    KotlinBug(
        "2.KT-3112",
        # pc.ParameterizedTypes() ( C<String>.Inner or C.Inner)
        [pc.NestedClasses(),
         pc.ParameterizedClasses(),
         pc.TypeArgsInference()],
        False,
        sy.MisleadingReport(),
        rc.InsufficientAlgorithmImplementation(),
        ct.Inference(),
        4
    ),
    KotlinBug(
        "3.KT-11721",
        # pc.Property() (Property getter)
        [pc.Overriding()],
        False,
        sy.MisleadingReport(),
        rc.IncorrectSequence(),
        ct.Resolution(),
        3
    ),
    KotlinBug(
        "4.KT-39461",
        # pc.Cast() in Kotlin "foo as X: is the equivalent of "(X) foo" (null as T),pc.ParamTypeInference() (suspend () -> T)
        [pc.Coroutines(), pc.OperatorOverloading(),
         pc.Lambdas(),
         pc.ParameterizedFunctions(),
         pc.FunctionTypes()
         ],
        True,
        sy.CompileTimeError(),
        rc.IncorrectComputation(),
        ct.Resolution(),
        11
    ),
    KotlinBug(
        "5.KT-15226",
        [pc.JavaInterop(),
         pc.Overriding(),
         pc.Delegation()],
        True,
        sy.Runtime(sy.WrongResult()),
        rc.DesignIssue(),
        ct.Declarations(),
        15
    ),
    KotlinBug(
        "6.KT-6720",
        # pc.Inheritance() (MyTraitImpl: TraitJavaImpl() ), maybe not pc.Overriding()?
        [pc.Overriding(),
         pc.JavaInterop()],
        False,
        sy.Runtime(sy.AbstractMethodError()),
        rc.IncorrectComputation(),
        ct.Resolution(),
        8
    ),
    KotlinBug(
        "7.KT-37644",
        # maybe pc.ArithmeticExpressions() ( because of +( Arithmetic Operator))
        [pc.ElvisOperator(),
         pc.Collections(),
         pc.ParameterizedTypes()
         ],
        True,
        sy.InternalCompilerError(),
        rc.ExtraneousComputation(),
        ct.Inference(),  # contraint solving
        3
    ),
    KotlinBug(
        "8.KT-22517",
        [pc.Reflection(),
         pc.OperatorOverloading(),
         pc.Delegation(),
         pc.ParameterizedTypes(),
         pc.Nullables(),
         pc.FlowTyping()],
        False,
        sy.Runtime(sy.NullPointerException()),
        rc.DesignIssue(),
        ct.Environment(),  # XXX
        10
    ),
    KotlinBug(
        "9.KT-18522",
        # pc.Nulllables (persistable1: Persistable?), no pc.ParameterizedClasses()
        [pc.Conditionals(), pc.Import(),
         pc.ParameterizedClasses(),
         pc.ParameterizedTypes()
         ],
        False,
        sy.InternalCompilerError(),
        rc.IncorrectCondition(),  # Wrong loop iteration
        ct.TypeComparison(),
        9
    ),
    KotlinBug(
        "10.KT-8320",
        # pc.ParameterizedTypes
        [pc.ParameterizedFunctions(),
         pc.TryCatch()],
        False,
        sy.Runtime(sy.ClassCastException()),
        rc.MissingCase(),
        ct.Declarations(),
        11
    ),
    KotlinBug(
        "11.KT-32081",
        # pc.This(), pc.VarTypeInference() (Either.Left(this)), no pc.ParameterizedClasses(),
        [pc.ParameterizedClasses(),
         pc.ParameterizedFunctions(),
         pc.ParameterizedTypes(),
         pc.Nothing(),
         pc.Subtyping(),
         pc.ExtensionFunctions()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Inference(),  # constraint solving
        5
    ),
    KotlinBug(
        #  The fix of KT-11280 triggers the bug on  KT-2311 so  maybe consider these 2 for the paper
        "12.KT-11280",
        # pc.Nullables() Any? in all test cases it uses a nullable type, pc.Conditionals() if (x1 == x), Inheritance() class Derived1 : Base(), took the second example becasue it is more realistic
        [pc.Overriding(),
         pc.Subtyping(),
         pc.FlowTyping()],
        False,
        # sy.Runtime(sy.ClassCastException())
        sy.Runtime(sy.RuntimeSymptom()),
        rc.DesignIssue(),
        ct.Inference(),
        13
    ),
    KotlinBug(
        "13.KT-42825",
        #pc.ParameterizedTypes()
        [pc.Conditionals(),
         pc.ParameterizedClasses(),
         pc.UseVariance(),
         pc.FlexibleTypes(), pc.Nullables(),
         pc.JavaInterop(),
         pc.FlowTyping()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.TypeComparison(),
        15
    ),
    KotlinBug(
        # regression bug The regression appeared after  commit with url:
        # https://github.com/JetBrains/kotlin/commit/b5a8ffaddc64b9862d8cf1173183df5e538e4c8e
        "14.KT-17597",
        # pc.ParameterizedTypes(), pc.VarTypeInference()
        [pc.Collections(), pc.AccessModifiers(),
         pc.StaticMethod(),
         pc.JavaInterop(),
         pc.FunctionReferences()],
        True,
        sy.CompileTimeError(),
        # maybe rc.MisingCase() because doesnt only change the condition but introduces a new method. Also see the following commit message
        # The regression appeared after b5a8ffa
        # when we started trying both static and member methods until
        # first success and when there is no successful
        # we were just leaving the last one (e.g. private member)

        # But the actual problem is that we were commiting the trace
        # in case of single (but incorrect) result in resolution mode of
        # SHAPE_FUNCTION_ARGUMENTS when we couldn't yet choose the
        # correct static method

        # Also we shouldn't choose a shape for callable reference
        # using only the knowledge that result is single:
        # it may lead to the wrong inference result
        # (see test with Pattern::compile)
        rc.IncorrectCondition(),
        ct.Resolution(),
        9
    ),
    KotlinBug(
        "15.KT-13597",
        # pc.Property()
        [pc.AnonymousClass()],
        False,  # change final field
        sy.Runtime(sy.IllegalAccessError()),
        rc.InsufficientAlgorithmImplementation(),
        ct.OtherSemanticChecking(),
        15
    ),
    KotlinBug(
        "16.KT-12738",
        # pc.Lambdas(), pc.ParamTypeInference()
        [pc.ParameterizedFunctions(),
         pc.FunctionReferences()],
        True,
        sy.CompileTimeError(),
        # agreed its algorithmic, maybe consider rc.IncorrectComputation (wrong algorithm used, we simplify it, i think incorrect matches better to insufficient)
        # Simplify and fix createReflectionTypeForCallableDescriptor
        # Previously its call sites needed to determine if the receiver type should be
        # ignored (e.g. if the reference is to static member or nested class constructor,
        # or if it's a bound reference), and 3 of 4 callers did it incorrectly. Simplify
        # this by passing the DoubleColonLHS instance everywhere.
        rc.InsufficientAlgorithmImplementation(),
        ct.Resolution(),
        3
    ),
    KotlinBug(
        "17.KT-37627",
        # pc.ParamTypeInference(), pc.ParameterizedTypes(), pc.Nothing(), no pc.Subtyping()? "to" method creates a pair
        [pc.Collections(),
         pc.Conditionals(),
         pc.Nullables(),
         pc.Subtyping(),
         pc.Lambdas(),
         pc.VarTypeInference()],
        True,
        sy.CompileTimeError(),
        # could be also  rc.IncorrectCondition but its also a missing case because its an additional check. Maybe change description of IncorrectCondition to only incorrect and not missing,
        # because most of the time a missing condition is considered a missing case.
        rc.MissingCase(),
        ct.Inference(),  # constraint solving
        5
    ),
    KotlinBug(
        "18.KT-12286",
        # pc.FunctionTypes() val f: (T, T) -> T = ::maxOf
        [pc.ParameterizedFunctions(),
         pc.FBounded(),
         pc.Conditionals(),
         pc.FunctionReferences()],
        True,
        sy.CompileTimeError(),
        rc.InsufficientAlgorithmImplementation(),
        ct.Inference(),  # constraint solving
        2
    ),
    KotlinBug(
        "19.KT-9630",
        # pc.MultipleImplements() class Baz<T> : Foo<T>, Bar<T>,
        [pc.ParameterizedClasses(),
         pc.Inheritance(),
         pc.ParameterizedFunctions(),
         pc.ParameterizedTypes(),
         pc.FBounded(),
         pc.MultiBounds(),
         pc.IntersectionTypes(),
         pc.ExtensionFunctions()],
        True,
        sy.CompileTimeError(),
        #agreed, also consider rc.IncorrectComputation() Fix computation of erased receiver for intersection types, change computation of receiverTypeConstructor
        rc.MissingCase(),
        ct.Approximation(),
        8
    ),
    KotlinBug(
        "20.KT-25302",
        # pc.Streams(), no pc.UseVariance() (direct use of Variance)
        [pc.ParameterizedFunctions(),
         pc.ParameterizedClasses(),
         pc.UseVariance(),
         pc.ParameterizedTypes(),
         ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Inference(),  # constraint solving
        12
    )
]

kotlin_iter3 = [
    KotlinBug(
        "1.KT-31620",
        # pc.SAM()(Interface Inv), maybe pc.ExperimentalApi() (ExperimentalTypeInference) characteristic?
        [pc.ParameterizedClasses(),
         pc.ParameterizedFunctions(),
         pc.Lambdas(),
         pc.VarTypeInference(),
         pc.BuilderInference(),
         pc.TypeArgsInference(),
         pc.ExtensionFunctions(),
         pc.FunctionTypes()],
        True,
        sy.CompileTimeError(),
        rc.WrongParams(),
        ct.Inference(),
        11
    ),
    KotlinBug(
        "2.KT-2277",
        [pc.Overloading(), pc.NestedClasses()],
        False,
        sy.Runtime(sy.AmbiguousMethodError()),
        rc.MissingCase(),
        ct.Declarations(),
        5
    ),
    KotlinBug(
        "3.KT-9134",
        [pc.Nullables(), pc.Lambdas(), pc.FlowTyping()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.TypeExpression(),
        6
    ),
    KotlinBug(
        "4.KT-35172",
        # pc.Cast() (null as T equals to: null (T) in Kotlin)
        [pc.Nullables(), pc.ParameterizedFunctions(),
         pc.ExtensionFunctions(), pc.Lambdas(), pc.ElvisOperator(),
         pc.SafeNavigationOperator(), pc.TypeArgsInference()],
        True,
        sy.CompileTimeError(),
        rc.ExtraneousComputation(),
        ct.Inference(),
        5
    ),
    KotlinBug(
        "5.KT-41644",
        [
            pc.ParameterizedClasses(),
            pc.ParameterizedTypes(),
            pc.BoundedPolymorphism(),
            pc.FBounded(),
            pc.SealedClasses(),
            pc.NestedClasses(),
            pc.Cast()
        ],
        True,
        sy.CompilationPerformance(),
        # rc.AlgorithmImproperlyImplemented() The current implementation of the algorithm for constraints incorporation
        #  produces a potentially very large number constructs and causes a significant degradation performance.
        rc.IncorrectComputation(),
        ct.Inference(),
        41
    ),
    KotlinBug(
        "6.KT-30953",
        # pc.VarTypeInference()
        [
            pc.Conditionals(),
            pc.FunctionReferences(),
        ],
        False,
        sy.InternalCompilerError(),
        rc.WrongDataReference(),
        ct.ErrorReporting(),
        3
    ),
    KotlinBug(
        # regression bug (This issue appeared after recently added new overload for flatMapTo.)
        "7.KT-39470",
        [
            pc.Collections(),
            pc.ParameterizedTypes(),
            pc.FunctionReferences(),
            pc.Property(),
            pc.ExtensionFunctions(),
            pc.TypeArgsInference()
        ],
        True,
        sy.CompileTimeError(),
        rc.IncorrectCondition(),
        ct.Inference(),
        8
    ),
    KotlinBug(
        "8.KT-6999",
        # maybe introduce a characterstic for org.apache.hadoop.util.PlatformName class?
        [
            pc.SecondaryConstructor(), # TODO
            pc.TypeAnnotations() # TODO
        ],
        False,
        sy.Runtime(sy.VerifyError()), # ?
        rc.IncorrectCondition(),
        ct.Declarations(),
        8
    ),
    KotlinBug(
        "9.KT-13685",
        [
            pc.Collections(),
            pc.ParameterizedTypes(),
            pc.TypeArgsInference(),
            pc.Nullables(),
            pc.FunctionReferences()
        ],
        False,
        sy.InternalCompilerError(),
        rc.WrongDataReference(),
        ct.Resolution(),
        4
    ),
    KotlinBug(
        "10.KT-5511",
        [
           pc.ParameterizedClasses(),
           pc.NestedClasses(),
           pc.Inheritance(),
           pc.ParameterizedTypes(),
           pc.Enums()
        ],
        False,
        sy.MisleadingReport(),
        rc.WrongParams(),
        ct.ErrorReporting(),
        3
    ),
    KotlinBug(
        "11.KT-26816",
        # pc.ParamTypeInference() ( Found: List<() -> Int>)
        [
            pc.TypeArgsInference(),
            pc.Lambdas(),
            pc.Collections()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Inference(),
        9
    ),
    KotlinBug(
        # regression bug (Issue does not reproduce with Kotlin 1.3.31 or less)
        "12.KT-33125",
        [
            pc.ParameterizedClasses(),
            pc.ParameterizedFunctions(),
            pc.ParameterizedTypes(),
            pc.TypeArgsInference(),
            pc.OperatorOverloading(),
            pc.Inheritance(),
            pc.BuilderInference(),
            pc.Collections(),
            pc.FunctionTypes(),
            pc.Lambdas(),
            pc.ExtensionFunctions(),
            pc.UseVariance(),
            pc.AugmentedAssignmentOperator(),
        ],
        True,
        sy.InternalCompilerError(),
        rc.InsufficientAlgorithmImplementation(),
        ct.TypeExpression(),
        12
    ),
    KotlinBug(
        "13.KT-7383",
        [
            pc.FunctionAPI(),
            pc.WildCardType(), # TODO
            pc.ParameterizedTypes(),
            pc.Lambdas()
        ],
        False,
        sy.InternalCompilerError(),
        rc.ExtraneousComputation(),
        ct.ErrorReporting(),
        3
    ),
    KotlinBug(
        "14.KT-33542",
        # pc.Nullables (Bundle?),
        [
            pc.Coroutines(),
            pc.ParameterizedClasses(),
            pc.DeclVariance(),
            pc.BoundedPolymorphism(),
            pc.ParameterizedTypes(),
            pc.BuilderInference(),
            pc.Overriding(),
            pc.Inheritance(),
            pc.FunctionTypes(),
            pc.ExtensionFunctions(),
            pc.Lambdas()
        ],
        False,
        sy.InternalCompilerError(),
        rc.WrongParams(),
        ct.Environment(),
        22
    ),
    KotlinBug(
        "15.KT-15391",
        # pc.ParamTypeInference() (suspend () -> Unit), pc.Lambda(), pc.NamedArgs() (completion = object : Continuation<Unit>)
        [
            pc.Coroutines(),
            pc.Inheritance(),
            pc.FunctionTypes(),
            pc.AnonymousClass(),
            pc.ParameterizedTypes(),
            pc.Overriding()
        ],
        False,
        sy.Runtime(sy.AbstractMethodError()),
        rc.MissingCase(),
        ct.Declarations(),
        15
    ),
    KotlinBug(
        "16.KT-9320",
        # in pc.TypeAnnotations() description it says java only, maybe include Kotlin?
        [
            pc.TypeAnnotations(),
            pc.AnonymousClass()
        ],
        True,
        sy.Runtime(sy.WrongResult()),
        rc.MissingCase(),
        # ct.Resolution
        # annotations on object literals are resolved later inside LazyClassDescriptor
        ct.TypeExpression(),
        5
    ),
    KotlinBug(
        "17.KT-13926",
        # pc.Nullables()
        [
            pc.TypeAnnotations(),
        ],
        False,
        sy.MisleadingReport(),
        rc.MissingCase(),
        # agreed maybe ct.Environment() (change in private method of LazyImportScope() )
        ct.OtherSemanticChecking(),
        6
    ),
    KotlinBug(
        "18.KT-9816",
        [
            pc.ParameterizedClasses(),
            pc.Inheritance(),
            pc.TryCatch(),
            pc.ParameterizedTypes()
        ],
        False,
        sy.InternalCompilerError(),
        # rc.MissingCase()
        # missed to check and throw an error if a parameterized class is extending Throwable
        rc.DesignIssue(),
        # ct.Declaration()  semantic check of class declaration
        ct.OtherSemanticChecking(),
        10
    ),
    KotlinBug(
        "19.KT-4462",
        # pc.Property(), pc.Arrays()
        [
            pc.OperatorOverloading(),
        ],
        False,
        sy.InternalCompilerError(),
        rc.IncorrectComputation(),
        ct.Transformation(),
        14
    ),
    KotlinBug(
        "20.KT-11203",
        # pc.Arrays()
        [
            pc.OperatorOverloading(),
            pc.ExtensionFunctions()
        ],
        False,
        sy.Runtime(sy.VerifyError()),
        # rc.MissingCase() add a boolean variable to resolveArrayAccessSpecialMethod to check if the array access is implicit, also we add an extra condition and an extra method
        rc.IncorrectCondition(),
        ct.Resolution(),
        8
    )
]

kotlin_iter4 = [
    KotlinBug(
        "1.KT-2418",
        [
            pc.Enums()
        ],
        False,
        sy.Runtime(sy.WrongResult()),
        rc.MissingCase(),
        ct.Declarations(),
        3
    ),
    KotlinBug(
        "2.KT-12982",
        [
            pc.AccessModifiers(),
            pc.Reflection(),
            pc.FunctionReferences(),
            pc.VarTypeInference()
        ],
        True,
        sy.CompileTimeError(),
        rc.WrongParams(),
        ct.Inference(),
        12
    ),
    KotlinBug(
        "3.KT-41470",
        [
            pc.ParameterizedClasses(),
            pc.ParameterizedTypes(),
            pc.TypeArgsInference(),
            pc.DeclVariance(),
            pc.ExtensionFunctions(),
            pc.ParameterizedFunctions(),
            pc.Inheritance(),
            pc.Overriding(),
            pc.Lambdas(),
            pc.FunctionTypes(),
            pc.BuilderInference()
        ],
        False,
        sy.Runtime(sy.NullPointerException()),
        rc.MissingCase(),
        ct.Inference(),
        29
    ),
    KotlinBug(
        "4.KT-12477",
        [
            pc.StandardFeatures()
        ],
        False,
        sy.MisleadingReport(),
        rc.MissingCase(),
        ct.Declarations(),
        1
    ),
    KotlinBug(
        "5.KT-44153",
        [
            pc.StandardLibrary()
        ],
        False,
        sy.CompilationPerformance(),
        rc.IncorrectCondition(),
        ct.Transformation(),
        1
    ),
    KotlinBug(
        "6.KT-8484",
        [
            pc.Enums()
        ],
        True,
        sy.CompileTimeError(),
        rc.IncorrectCondition(),
        ct.Declarations(),
        4
    ),
    KotlinBug(
        "7.KT-16232",
        [
            pc.NestedClasses(),
            pc.Singleton()
        ],
        False,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.Declarations(),
        13
    ),
    KotlinBug(
        "8.KT-17611",
        [
            pc.NestedClasses(),
            pc.AnonymousClass()
        ],
        True,
        sy.MisleadingReport(),
        rc.DesignError(),
        ct.OtherSemanticChecking(),
        5
    ),
    KotlinBug(
        "9.KT-37554",
        [
            pc.ParameterizedClasses(),
            pc.DeclVariance(),
            pc.BoundedPolymorphism(),
            pc.Nullables(),
            pc.FBounded(),
            pc.Inheritance(),
            pc.ParameterizedFunctions(),
            pc.ParameterizedTypes(),
            pc.TypeArgsInference(),
            pc.ElvisOperator()
        ],
        True,
        sy.CompileTimeError(),
        rc.IncorrectComputation(),
        ct.Inference(),
        13
    ),
    KotlinBug(
        "10.KT-23854",
        [
            pc.ParameterizedClasses(),
            pc.ParameterizedFunctions(),
            pc.TypeArgsInference(),
            pc.UseVariance(),
            pc.ParameterizedTypes()
        ],
        True,
        sy.CompileTimeError(),
        rc.DesignIssue(),
        ct.Inference(),
        11
    ),
    KotlinBug(
        "11.KT-6399",
        [
            pc.JavaInterop(),
            pc.Conditionals(),
            pc.Enums()
        ],
        True,
        sy.Runtime(), # TODO MissingCase
        rc.DesignIssue(),
        ct.Declarations(),
        11
    ),
    KotlinBug(
        "12.KT-30826",
        [
            pc.MultipleImplements(),
            pc.Nullables(),
            pc.VarTypeInference(),
            pc.Cast(),
            pc.Lambdas(),
            pc.FlowTyping()
        ],
        False,
        sy.Runtime(sy.NullPointerException()),
        rc.MissingCase(),
        ct.OtherSemanticChecking(),
        18
    ),
    KotlinBug(
        "13.KT-11490",
        [
            pc.ParameterizedClasses(),
            pc.DeclVariance(),
            pc.Inheritance(),
            pc.ParameterizedTypes(),
            pc.ParameterizedFunctions(),
            pc.TypeArgsInference()
        ],
        False,
        sy.InternalCompilerError(),
        rc.IncorrectCondition(),
        ct.Declarations(),
        7
    ),
    KotlinBug(
        "14.KT-37579",
        [
            pc.ParameterizedClasses(),
            pc.ParameterizedTypes(),
            pc.OperatorOverloading(),
            pc.FunctionTypes(),
            pc.Nullables(),
            pc.SafeNavigationOperator(),
            pc.ExtensionFunctions()
        ],
        True,
        sy.CompileTimeError(),
        rc.IncorrectCondition(),
        ct.Resolution(),
        10
    ),
    KotlinBug(
        "15.KT-32462",
        [
            pc.Conditionals(),
            pc.FunctionReferences(),
            pc.Subtyping()
        ],
        True,
        sy.InternalCompilerError(),
        rc.IncorrectComputation(),
        ct.Resolution(),
        8
    ),
    KotlinBug(
        "16.KT-32235",
        [
            pc.ParameterizedClasses(),
            pc.Collections(),
            pc.ParameterizedTypes(),
            pc.WildCardType(),
            pc.Nullables(),
            pc.FlowTyping(),
            pc.Property(),
            pc.ParamTypeInference()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Approximation(),
        17
    ),
    KotlinBug(
        "17.KT-10896",
        [
            pc.ParameterizedClasses(),
            pc.ParameterizedFunctions(),
            pc.ParameterizedTypes(),
            pc.Subtyping(),
            pc.Inheritance(),
            pc.FunctionTypes(),
            pc.Overriding(),
            pc.Conditionals(),
            pc.Lambdas()
        ],
        False,
        sy.Runtime(sy.ClassCastException()),
        rc.MissingCase(),
        ct.Resolution(),
        35
    ),
    KotlinBug(
        "18.KT-31025",
        [
            pc.JavaInterop(),
            pc.ParameterizedClasses(),
            pc.ParameterizedFunctions(),
            pc.FunctionTypes(),
            pc.TypeArgsInference(),
            pc.UseVariance(),
            pc.FunctionReferences(),
            pc.SAM(),
            pc.FunctionAPI()
        ],
        True,
        sy.CompileTimeError(),
        rc.IncorrectCondition(),
        ct.Resolution(),
        12
    ),
    KotlinBug(
        "19.KT-42791",
        [
            pc.ParameterizedTypes(),
            pc.ParameterizedClasses(),
            pc.BoundedPolymorphism(),
            pc.ParameterizedFunctions(),
            pc.Inheritance(),
            pc.TypeArgsInference(),
            pc.NestedClasses()
        ],
        True,
        sy.CompilationPerformance(),
        rc.InsufficientAlgorithmImplementation(),
        ct.Inference(),
        14
    ),
    KotlinBug(
        "20.KT-42791",
        [
            pc.Import(),
            pc.Typedefs(),
            pc.Lambdas(),
            pc.FunctionTypes(),
            pc.DeclVariance(),
            pc.ParameterizedClasses(),
            pc.ParameterizedTypes(),
            pc.ExtensionFunctions(),
            pc.TypeArgsInference()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Resolution(),
        0
    ),
]
