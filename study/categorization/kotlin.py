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
         pc.TypeArgsInference(),
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
         pc.TypeArgsInference(),
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
         pc.TypeArgsInference(),
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
        [pc.Collections(),
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
#rc.AlgorithmImproperlyImplemented
        "1.KT-31102",
        [pc.Lambdas(), pc.FunctionReferences(),
         pc.ParameterizedFunctions(), pc.FunctionTypes(),
         pc.TypeArgsInference(),
         pc.TypeArgsInference(), pc.This()],
        True,
        sy.CompileTimeError(),
        rc.InsufficientAlgorithmImplementation(),
        ct.Inference(),  # constraint solving
        8
    ),
    KotlinBug(
#rc.AlgorithmImproperlyImplemented
        "2.KT-3112",
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
        [pc.Overriding(), pc.Property()],
        False,
        sy.MisleadingReport(),
        rc.IncorrectSequence(),
        ct.Resolution(),
        3
    ),
    KotlinBug(
        "4.KT-39461",
        [pc.Coroutines(), pc.OperatorOverloading(),
         pc.Lambdas(),
         pc.TypeArgsInference(),
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
        [pc.ParameterizedClasses(),
         pc.ParameterizedFunctions(),
         pc.TypeArgsInference(),
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
        "12.KT-11280",
        [pc.Overriding(),
         pc.Subtyping(),
         pc.FlowTyping()],
        False,
        sy.Runtime(sy.ClassCastException()),
        rc.DesignIssue(),
        ct.Inference(),
        13
    ),
    KotlinBug(
        "13.KT-42825",
        [pc.Conditionals(),
         pc.ParameterizedClasses(),
         pc.ParameterizedTypes(),
         pc.UseVariance(),
         pc.Nullables(),
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
        [pc.Collections(), pc.AccessModifiers(),
         pc.StaticMethod(),
         pc.JavaInterop(),
         pc.FunctionReferences()],
        True,
        sy.CompileTimeError(),
        rc.IncorrectCondition(),
        ct.Resolution(),
        9
    ),
    KotlinBug(
        "15.KT-13597",
        [pc.AnonymousClass(), pc.Property()],
        False,  # change final field
        sy.Runtime(sy.IllegalAccessError()),
        rc.InsufficientAlgorithmImplementation(),
        ct.OtherSemanticChecking(),
        15
    ),
    KotlinBug(
        "16.KT-12738",
        [pc.ParameterizedFunctions(),
         pc.FunctionReferences()],
        True,
        sy.CompileTimeError(),
        rc.InsufficientAlgorithmImplementation(),
        ct.Resolution(),
        3
    ),
    KotlinBug(
        "17.KT-37627",
        [pc.Collections(),
         pc.Conditionals(),
         pc.ParamTypeInference(),
         pc.Nullables(),
         pc.Subtyping(),
         pc.Lambdas(),
         pc.VarTypeInference()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Inference(),  # constraint solving
        5
    ),
    KotlinBug(
        "18.KT-12286",
        [pc.ParameterizedFunctions(),
         pc.TypeArgsInference(),
         pc.FunctionTypes(),
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
        [pc.ParameterizedClasses(),
         pc.Inheritance(),
         pc.MultipleImplements(),
         pc.ParameterizedFunctions(),
         pc.TypeArgsInference(),
         pc.ParameterizedTypes(),
         pc.FBounded(),
         pc.MultiBounds(),
         pc.IntersectionTypes(),
         pc.ExtensionFunctions()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Approximation(),
        8
    ),
    KotlinBug(
        "20.KT-25302",
        [pc.ParameterizedFunctions(),
         pc.TypeArgsInference(),
         pc.ParameterizedClasses(),
         pc.WildCardType(),
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
				#rc.AlgorithmImproperlyImplemented
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
        # pc.ParameterizedTypes() (KMutableProperty1<Foo, Int>)
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
        # pc.Couroutines() FlowCollector interface is part of of Couroutines library, pc.SAM() Flow and FlowCollector intefaces
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
        # True it says: Should print null but instead, it fails with NPE:
        # Also if we see original report it also says code should pass
        False,
        sy.Runtime(sy.NullPointerException()),
        rc.MissingCase(),
        ct.Inference(),
        29
    ),
    KotlinBug(
        "4.KT-12477",
        # pc.Constants() new category or make pc.StaticMethod -> pc.Static in general and consider this bug  pc.Static because:
        # "Declaring a variable const is much like using the static keyword in Java."
        [
            pc.StandardFeatures()
        ],
        False,
        sy.MisleadingReport(),
        rc.MissingCase(),
        # I think it fits more pc.ErrorReporting() because althought we have a declaration check implementation (canBeConst),
        # the fix is strongly related to diagnostics which relates more to Error Reporting, and a strong indication is also the bug symptom
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
        # maybe introduce a new characteristic pc.Shadowing() or pc.VariableShadowing()
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
        # ct.TypeExpression, the fix is related more to a type check of an expression with when
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
        # pc.SAM()(I2)
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
        #type related, ct.Approximation() fix related to intersection types, expected types
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
        # pc.Conditionals()
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
        # pc.FlowTyping() when (result) is SuccessBinding -> {...., pc.VarTypeInference() (FailedBinding(errors))
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
        # pc.ParameterizedTypes() (Inv<String>)
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
        # agreed, but I think ct.Environment() fits more. We add a check at SamAdapterFunctionsScope also removed
        # context.call.createLookupLocation() and added ktExpression?.createLookupLocation()
        # and if it is null then call context.call.createLookupLocation(). Also change arguments of ASTScopeTower
        ct.Resolution(),
        12
    ),
    KotlinBug(
        "19.KT-42791",
        # regression bug
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
        # maybe rc.DesignIssue() Rethink constraints incorporation
        # Namely, remove incorporation “otherInsideMyConstraint” to eliminate
        # constraint system redundancy and produce a potentially very large number
        #  of constructs.
        # Instead, introduce not so “spreadable” incorporation during variable fixation
        # from the commit message, it seems like the bug is associated with an issue in the design rather than the implementation
        rc.InsufficientAlgorithmImplementation(),
        ct.Inference(),
        14
    ),
    KotlinBug(
        # I think you should change the name of the bug to KT-13181
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
