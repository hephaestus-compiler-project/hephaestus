from bug import KotlinBug
import categories as ct
import characteristics as pc
import symptoms as sy
import root_causes as rc


kotlin_iter1 = [
    KotlinBug(
        "1.KT-1934",
        # pc.Overriding() maybe becasue we erroneously create a trait inheriting 2 overriding functions  and should yield an error because of that
        [pc.Inheritance()],
        False,
        sy.Runtime(sy.WrongResult()),
        rc.MissingCase(),
        ct.Declarations(), # -- During Override Resolution
        4
    ),
    KotlinBug(
        "2.KT-4814",
         # pc.AugmentedAssignmentOperator()
        [pc.ArithmeticExpressions()],
        False,
        sy.Runtime(sy.VerifyError()),
        rc.MissingCase(),
        ct.TypeExpression(),
        4
    ),
    KotlinBug(
        "3.KT-42175",
         # pc.AugmentedAssignmentOperator()
        [
            pc.Lambdas(),
            pc.Collections(),
            pc.This()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        # could also be resolution both fit, inference fits more to the general problem, the fix fits better to resolution
        # Resolve leaves incorrect information about this: it is resolved to an unrelated descriptor with type MutableList<NonFixed: TypeVariable(E)>.
        ct.Inference(),  # "type variable substitution"
        #10
        8
    ),
    KotlinBug(
        "4.KT-10244",
        [pc.FlowTyping(),
         pc.Conditionals()],
        False,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        # could also be ct.Declaration because the bug is not on the type check of the expression but mostly on the validity of the function declaration (return type) to support this in fix we see major change in DeclarationsChecker.kt
        #  for instance in the fix we add if (!function.hasDeclaredReturnType()) { do some semantic checks
        ct.TypeExpression(), # -- TypeChecking
        # 5
        4
    ),
    KotlinBug(
        "5.KT-10472",
        # no pc.ParameteriedClasses()
        [pc.Overloading(), pc.Varargs(),
         pc.ParameterizedClasses(),
         pc.ParameterizedFunctions(),
         pc.ParameterizedTypes()],
        True,
        # sy.Runtime(sy.WrongResult())
        sy.Runtime(sy.NullPointerException()),
        rc.IncorrectSequence(),
        ct.Resolution(),
        # 10
        8
    ),
    KotlinBug(
        "6.KT-7485",
        [pc.Where(),
         pc.BoundedPolymorphism(),
         pc.ParameterizedFunctions(),
         pc.ParameterizedClasses(),
         pc.Nullables(),
         pc.Subtyping()],
        False,
        sy.Runtime(sy.NullPointerException()),
        rc.IncorrectComputation(), # IncorrectCondition
        ct.TypeComparison(), # Declarations
        # 12
        11
    ),
    KotlinBug(
        "7.KT-23748",
        # pc.Collections()
        [pc.ParameterizedFunctions(),
         pc.Subtyping(),
         pc.Nullables(),
         pc.ElvisOperator()],
        True,
        sy.CompileTimeError(),
        rc.IncorrectComputation(),
        ct.Inference(),  # constraint solving
        # 11
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
         # maybe consider ct.Environment?(change in DeserializedMemberScope class)
        ct.Mechanics(), # -- serialization
        #16
        11
    ),
    KotlinBug(
        "9.KT-10711",
        # pc.ParameterizedClass()
        [pc.ParameterizedFunctions(),
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
        #13
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
         # found it difficult, change the way we calculate the common supertype of 2 classes, no declaration because typecomparsion is more specific to this fix and declaration more broaden.
#        # Also the fix is not in the semantic check of a declaration, and more it is about a computation of a type.
        ct.TypeComparison(), # Why not Decleration?
        6
    ),
    KotlinBug(
        "12.KT-6014",
        [pc.Overriding(), pc.Inheritance(), pc.Delegation()],
        True,
        sy.CompileTimeError(),
        rc.IncorrectComputation(),
        # agreed with resolution, maybe consider ct.Declaration because we do a semantic check of a class declaration (class B : C by A()) because it says
        # Members declared in interface or overriding members declared in super-interfaces
        # can be implemented by delegation even if they override members declared in super-class
        ct.Resolution(),
        #9
        7
    ),
    KotlinBug(
        "13.KT-12044",
        # do we consider it pc.FlowTyping()?
        [pc.Conditionals(), pc.PropertyReference(), pc.ParameterizedTypes()],
        True,
        sy.CompileTimeError(),
        rc.WrongParams(),
        ct.Resolution(),
        8
    ),
    KotlinBug(
        "14.KT-4334",
        # pc.Collections()
        [pc.Lambdas(), pc.Loops()],
        False,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.OtherSemanticChecking(), # -- BREAK_OR_CONTINUE_JUMPS_ACROSS_FUNCTION_BOUNDARY
        7
    ),
    KotlinBug(
        "15.KT-32184",
        # pc.Properties() pc.Nullables(), pc.VarTypeInference()
        [pc.Lambdas(), pc.DataClasses(), pc.FunctionTypes()],
        True,
        sy.InternalCompilerError(),
        rc.WrongParams(),
        ct.Resolution(),
        #24
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
#        #pc.Nullables()
        [pc.Conditionals(), pc.Import(),
         pc.FlexibleTypes(), # Java Types are loaded as flexible types
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
        #pc.Nullables() why pc.UseVariance()?
        [pc.ParameterizedClasses(),
         pc.FBounded(),
         pc.ParameterizedTypes(),
         pc.UseVariance(),
         pc.NullAssertion()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Approximation(),
        #10
        6
    ),
    KotlinBug(
        "20.KT-6992",
        [pc.Overloading(),
         pc.ParameterizedClasses(),
         pc.Delegation(), # ConstructorDelegation
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
        [pc.NestedDeclaration(),
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
        [pc.Overriding()],
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
        sy.Runtime(sy.RuntimeSymptom()),
        rc.DesignIssue(),
        ct.Inference(),
        13
    ),
    KotlinBug(
        "13.KT-42825",
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
        [pc.AnonymousClass()],
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
         pc.ParameterizedFunctions(),
         pc.ParameterizedTypes(),
         pc.FBounded(),
         pc.Where(),
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
        [pc.Overloading(), pc.NestedDeclaration()],
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
            pc.NestedDeclaration(),
            pc.Cast()
        ],
        True,
        sy.CompilationPerformance(),
        rc.IncorrectComputation(),
        ct.Inference(),
        41
    ),
    KotlinBug(
        "6.KT-30953",
        [
            pc.Conditionals(),
            pc.FunctionReferences(),
        ],
        False,
        sy.InternalCompilerError(),
        rc.WrongDataReference(), # Error Reporting
        ct.Mechanics(),
        3
    ),
    KotlinBug(
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
        [
            pc.SecondaryConstructor(), # TODO
            pc.Annotation() # TODO
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
           pc.NestedDeclaration(),
           pc.Inheritance(),
           pc.ParameterizedTypes(),
           pc.Enums()
        ],
        False,
        sy.MisleadingReport(),
        rc.WrongParams(),
        ct.Mechanics(), # Error Reporting
        3
    ),
    KotlinBug(
        "11.KT-26816",
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
            pc.FunctionalInterface(),
            pc.WildCardType(), # TODO
            pc.ParameterizedTypes(),
            pc.Lambdas()
        ],
        False,
        sy.InternalCompilerError(),
        rc.ExtraneousComputation(),
        ct.Mechanics(), # Error Reporting
        3
    ),
    KotlinBug(
        "14.KT-33542",
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
        ct.Environment()
        22
    ),
    KotlinBug(
        "15.KT-15391",
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
        [
            pc.TypeAnnotations(),
            pc.AnonymousClass()
        ],
        True,
        sy.Runtime(sy.WrongResult()),
        rc.MissingCase(),
        ct.TypeExpression(),
        5
    ),
    KotlinBug(
        "17.KT-13926",
        [
            pc.TypeAnnotations(),
        ],
        False,
        sy.MisleadingReport(),
        rc.MissingCase(),
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
        rc.DesignIssue(),
        ct.OtherSemanticChecking(),
        10
    ),
    KotlinBug(
        "19.KT-4462",
        [
            pc.OperatorOverloading(),
        ],
        False,
        sy.InternalCompilerError(),
        rc.IncorrectComputation(),
        ct.Mechanics(), # Desugaring
        14
    ),
    KotlinBug(
        "20.KT-11203",
        [
            pc.OperatorOverloading(),
            pc.ExtensionFunctions()
        ],
        False,
        sy.Runtime(sy.VerifyError()),
        rc.IncorrectCondition(),
        ct.Resolution(),
        8
    )
]
