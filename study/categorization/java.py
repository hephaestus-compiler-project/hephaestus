from bug import JavaBug
import categories as ct
import characteristics as pc
import symptoms as sy
import root_causes as rc
# Rename pc.FunctionApi() to pc.FunctionApi() because An informative annotation type used to indicate that an interface type declaration is intended to be a functional interface as defined by the Java Language Specification. Conceptually, a functional interface has exactly one abstract method

java_iter1 = [
    JavaBug(
        "1.JDK-8258972",
        [pc.ParameterizedClasses(),
         pc.ParameterizedTypes(),
         pc.SealedClasses(),
         pc.NestedDeclaration(),
         pc.Subtyping()
         ],
         True,
        sy.CompileTimeError(),
        rc.FunctionalSpecificationMismatch(),
        ct.TypeComparison(),
        # 12
        9
    ),
    JavaBug(
        "2.JDK-8254557",
        [pc.Streams(), pc.FunctionalInterface(),
         pc.ParameterizedFunctions(), pc.AnonymousClass(),
         pc.Lambdas(), pc.Conditionals(), pc.Reflection(),
         pc.TypeArgsInference(),
         pc.Overriding()
         ],
        False,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.TypeExpression(),
        # 58
        34
    ),
     JavaBug(
        "3.JDK-8244559",
        [pc.Collections(), pc.Streams(),
         pc.Inline(), pc.NestedDeclaration(),
         pc.ParameterizedClasses(), pc.ParameterizedTypes(),
         pc.ReferenceTypes(), pc.Lambdas()
         ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Mechanics(),
        # 21
        17
    ),
        JavaBug(
        "4.JDK-8191802",
        [pc.ParameterizedClasses(), pc.BoundedPolymorphism(),
         pc.ParameterizedTypes(), pc.UseVariance(),
         pc.Subtyping(), pc.VarTypeInference()
         ],
         True,
        sy.CompileTimeError(),
        rc.FunctionalSpecificationMismatch(),
        ct.Inference(),
        # 9
        8
    ),
    JavaBug(
        "5.JDK-8231461",
        [pc.FunctionReferences(),
         pc.StaticMethod(), pc.Overloading(),
         ],
         True,
         sy.CompileTimeError(),
         rc.MissingCase(),
        ct.Resolution(),
        # 10
        8
    ),
    JavaBug(
        "6.JDK-8012238",
        [pc.Overriding(),
         pc.Reflection(),
         pc.ParameterizedFunctions(),
         pc.BoundedPolymorphism(),
         pc.ParameterizedTypes()
         ],
         True,
         sy.CompileTimeError(),
        rc.InsufficientAlgorithmImplementation(),
        ct.Inference(),
        18
    ),
    JavaBug(
        "7.JDK-8006749",
        [pc.SAM(),
         pc.Lambdas(), pc.ParamTypeInference()
         ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.TypeExpression(),
        # 7
        6
    ),
   JavaBug(
        "8.JDK-6995200",
        [
            pc.ParameterizedFunctions(),
            pc.PrimitiveTypes(), pc.ParameterizedTypes()
         ],
        True,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.TypeComparison(),
        # 9
        8
    ),
    JavaBug(
        "9.JDK-7040883",
        [
            pc.ParameterizedFunctions(), pc.Arrays(),
            pc.Reflection(), pc.ParameterizedTypes()
         ],
         True,
        sy.CompileTimeError(),
        rc.WrongParams(),
        ct.Inference(),
        # 16
        6
    ),
    JavaBug(
        "10.JDK-8029721",
        [
            pc.TypeAnnotations(),
            pc.SAM(),
            pc.Lambdas()
        ],
        True,
        sy.InternalCompilerError(),
        rc.IncorrectComputation(),
        ct.Environment(),
        # 10
        9
    ),
    JavaBug(
        "11.JDK-8129214",
        [pc.Import(),
         pc.ParameterizedFunctions(), pc.BoundedPolymorphism()
         ],
        True,
         sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Approximation(),
        # 13
        10
    ),
    JavaBug(
        "12.JDK-8203277",
        [pc.Collections(), pc.FunctionalInterface(),
         pc.Overriding(), pc.Lambdas(), pc.TypeArgsInference()
         ],
        True,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.TypeExpression(),
        # 12
        9
    ),
    JavaBug(
        "13.JDK-8195598",
        [
            pc.ParameterizedFunctions(), pc.Overloading(),
            pc.Lambdas(), pc.FunctionalInterface()
        ],
        True,
        sy.CompileTimeError(),
        rc.IncorrectCondition(),
        ct.Resolution(),
        14,
    ),
    JavaBug(
        "14.JDK-8202597",
        [pc.Cast(),
         pc.Subtyping(),
         pc.FunctionReferences(), pc.IntersectionTypes()
         ],
        True,
        sy.CompileTimeError(),
        rc.FunctionalSpecificationMismatch(),
        ct.Approximation(),
        # 10
        9
    ),
    JavaBug(
        "15.JDK-8144832",
        [
            pc.ParameterizedClasses(), pc.Cast(), pc.PrimitiveTypes()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Approximation(),
        5
    ),
    JavaBug(
        "16.JDK-8169091",
        [
            pc.IntersectionTypes(),
            pc.ParameterizedFunctions(), pc.UseVariance(),
            pc.ParameterizedTypes(), pc.BoundedPolymorphism(),
            pc.TypeArgsInference(),
            pc.Collections(),
            pc.Cast(), pc.StaticMethod(), pc.FunctionReferences()
        ],
        True,
        sy.CompileTimeError(),
        rc.WrongParams(),
        ct.TypeComparison(),
        # 17
        7
    ),
  JavaBug(
        "17.JDK-6996914",
        [
            pc.NestedDeclaration(), pc.Subtyping(), pc.ParameterizedClasses(),
            pc.TypeArgsInference(), pc.AccessModifiers()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Environment(),
        # 19
        8
    ),
 JavaBug(
        "18.JDK-8154180",
        [
            pc.FunctionalInterface(),
            pc.ParameterizedTypes(),
            pc.Lambdas(),
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Resolution(),
        # 15,17
        16
    ),
    JavaBug(
        "19.JDK-7041019",
        [pc.Arrays(), pc.ParameterizedClasses(),
        pc.BoundedPolymorphism(), pc.ParameterizedTypes(),
        pc.Overriding(), pc.Subtyping()
        ],
        False,
        sy.Runtime(sy.ClassCastException())
        rc.WrongParams()
        ct.Inference(),
        # 24
        8
    ),
    JavaBug(
        "20.JDK-8148354",
        [
            pc.FunctionalInterface(),
            pc.FunctionReferences(),
            pc.ParameterizedFunctions(), pc.BoundedPolymorphism(),
            pc.ParameterizedTypes(),
            pc.IntersectionTypes()
        ],
        True,
        sy.CompileTimeError(),
        rc.IncorrectComputation(),
        ct.Approximation(),
        # 17
        8
    ),
]


java_iter2 = [
    JavaBug(
        "1.JDK-8152832",  # regression
        [
            pc.Streams(), pc.Collections(), pc.Lambdas(),
            pc.FunctionalInterface(), pc.BoundedPolymorphism(),
            pc.UseVariance(), pc.ParameterizedTypes(),
            pc.ParameterizedClasses(), pc.ParameterizedFunctions(),
            pc.Subtyping()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Inference(),  # Contraint solving
        19
    ),
    JavaBug(
        "2.JDK-7042566",
        [
            pc.Overloading(), pc.Varargs()
        ],
        True,
        sy.CompileTimeError(),
        rc.AlgorithmImproperlyImplemented(),
        ct.Resolution(),
        8
    ),
    JavaBug(
        "3.JDK-6476118",
        [
            pc.Overriding(), pc.Overloading(),
            pc.ParameterizedClasses(),
            pc.ParameterizedTypes()
        ],
        False,
        sy.Runtime(sy.ClassCastException()),
        rc.MissingCase(),
        ct.Resolution(),
        13
    ),
    JavaBug(
        "4.JDK-8029569",
        [pc.Varargs(), pc.Overloading()],
        False,
        sy.InternalCompilerError(),
        rc.IncorrectDataType(),
        ct.Resolution(),
        8
    ),
    JavaBug(
        "5.JDK-8075793",
        [
            pc.Collections(), pc.ParameterizedFunctions(),
            pc.UseVariance(), pc.ParameterizedTypes(),
            pc.TypeArgsInference()
        ],
        True,
        sy.CompileTimeError(),
        rc.DesignIssue(),
        ct.Inference(),  # constraint solving
        6
    ),
    JavaBug(
        "6.JDK-8016081",
        [pc.TypeAnnotations(), pc.Lambdas(), pc.Conditionals(), pc.SAM()],
        True,
        sy.CompileTimeError(),
        rc.IncorrectCondition(),
        ct.Environment(),
        5
    ),
    JavaBug(
        "7.JDK-8226510",
        [pc.Conditionals(), pc.TryCatch()],
        True,
        sy.Runtime(),
        rc.MissingCase(),
        ct.OtherSemanticChecking(),
        10
    ),
    JavaBug(
        "8.JDK-8039214",
        [
            pc.ParameterizedClasses(), pc.ParameterizedFunctions(),
            pc.ParameterizedTypes(), pc.UseVariance(),
            pc.Inheritance(), pc.Subtyping()
        ],
        True,
        sy.CompileTimeError(),
        rc.DesignIssue(),
        ct.TypeComparison(),
        7
    ),
    JavaBug(
        "9.JDK-8029017",
        [pc.TypeAnnotations()],
        True,
        sy.CompileTimeError(),
        rc.DesignIssue(),
        ct.TypeComparison(),
        10
    ),
    JavaBug(
        "10.JDK-7041730",
        [pc.Cast()],
        False,
        sy.Runtime(sy.ClassCastException()),
        rc.IncorrectComputation(),
        ct.TypeComparison(),
        3
    ),
    JavaBug(
        "11.JDK-8020804",
        [
            pc.FunctionalInterface(),
            pc.ParameterizedClasses(), pc.ParameterizedFunctions(),
            pc.Arrays(), pc.BoundedPolymorphism(),
            pc.ParameterizedTypes(), pc.Overloading(),
            pc.FunctionReferences()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Approximation(),
        12
    ),
    JavaBug(
        "12.JDK-7062745",  # regression
        [
            pc.Overloading(), pc.Collections(),
            pc.Inheritance(), pc.ParameterizedTypes(),
            pc.Subtyping()
        ],
        True,
        sy.CompileTimeError(),
        rc.DesignIssue(),
        ct.Resolution(),
        9
    ),
    JavaBug(
        "13.JDK-8189838",
        [
            pc.FBounded(),
            pc.BoundedPolymorphism(), pc.ParameterizedClasses(),
            pc.Collections(), pc.ParameterizedTypes(),
            pc.TypeArgsInference(), pc.IntersectionTypes()
        ],
        True,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.Approximation(),
        5
    ),
    JavaBug(
        "14.JDK-8011376",
        [
            pc.Lambdas(), pc.TryCatch(), pc.ParameterizedFunctions(),
            pc.ParameterizedTypes(), pc.Subtyping()
        ],
        True,
        sy.CompileTimeError(),
        rc.WrongParams(),
        ct.OtherSemanticChecking(),
        6
    ),
    JavaBug(
        "15.JDK-8008537",
        # Subtyping
        [pc.FunctionReferences(), pc.Overloading(), pc.Subtyping()],
        False,
        sy.Runtime(),
        rc.MissingCase(),
        ct.OtherSemanticChecking(),
        17
    ),
    JavaBug(
        "16.JDK-8188144",  # regression
        [pc.ParameterizedTypes(), pc.FunctionReferences(), pc.FunctionalInterface()],
        True,
        sy.Runtime(sy.WrongResult()),
        rc.IncorrectComputation(), # MissingCase
        ct.Resolution(),
        9
    ),
    JavaBug(
        "17.JDK-8171993",
        # pc.ParameterizedTypes()?
        [
            pc.Varargs(), pc.TypeArgsInference(), pc.ParameterizedClasses(),
            pc.FunctionReferences(), pc.FunctionalInterface()
        ],
        True,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.Mechanics(),
        9
    ),
    JavaBug(
        "18.JDK-8010303",
        [pc.ParameterizedFunctions(), pc.ParameterizedClasses(),
         pc.ParameterizedTypes()],
        True,
        sy.CompileTimeError(),
        rc.IncorrectComputation(),
        ct.Inference(),
        10
    ),
    JavaBug(
        "19.JDK-6835428",
        [
            pc.FBounded(),
            pc.UseVariance(), pc.Subtyping(),
            pc.ParameterizedFunctions(), pc.Collections(),
            pc.BoundedPolymorphism()
        ],
        True,
        sy.CompileTimeError(),
        rc.ExtraneousComputation(),
        ct.Inference(),  # constraint solving
        7
    ),
    JavaBug(
        "20.JDK-8029002",
        [
            pc.ParameterizedClasses(), pc.ParameterizedFunctions(),
            pc.BoundedPolymorphism(), pc.UseVariance(),
            pc.Subtyping(), pc.Inheritance(),
            pc.ParameterizedTypes()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Inference(),  # constraint solving
        11
    )
]

java_iter3 = [
    JavaBug(
        "1.JDK-8031967",
        [
            pc.Collections(),
            pc.Lambdas(),
            pc.Cast(),
            pc.Conditionals(),
            pc.ParameterizedTypes(),
            pc.Reflection() # Dynamic Invocation
            # + File API?
        ],
        True,
        sy.CompilationPerformance(),
        rc.AlgorithmImproperlyImplemented(),
        ct.Resolution(),
        105
    ),
    JavaBug(
        "2.JDK-6880344",
        [
            pc.ParameterizedClasses(),
            pc.Inheritance(),
            pc.BoundedPolymorphism(),
            pc.FBounded()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Inference(),
        9
    ),
    JavaBug(
        "3.JDK-7142086",
        [
            pc.Collections(),
            pc.UseVariance(),
            pc.ParameterizedTypes()
            # + File API?
        ],
        True,
        sy.CompilationPerformance(),
        rc.MissingCase(),
        ct.Resolution(),
        84
    ),
    JavaBug(
        "4.JDK-8131915",
        [
            # Files API?
            pc.Collections(),
            pc.ParameterizedTypes()
        ],
        False,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.Mechanics(),
        55
    ),
    JavaBug(
        "5.JDK-7148242",
        [
            pc.ParameterizedClasses(),
            pc.NestedDeclaration(),
            pc.BoundedPolymorphism()
        ],
        True,
        sy.CompileTimeError(),
        rc.ExtraneousComputation(),
        ct.Inference(),
        7
    ),
    JavaBug(
        "6.JDK-7020043",
        [
            pc.TypeArgsInference()
        ],
        False,
        sy.Runtime(),
        rc.MissingCase(),
        ct.Mechanics(), # But maybe it's more close to Environment
        5
    ),
    JavaBug(
        "7.JDK-8209173",
        [
            # File API?
            # Maybe we should include the code in Strings?
            # pc.ParameterizedTypes(),
            # pc.Collections(),
            # pc.ParameterizedClasses()
        ],
        False,
        sy.InternalCompilerError(),
        rc.IncorrectCondition(),
        ct.Mechanics(),
        62
    ),
    JavaBug(
        "8.JDK-7181578",
        [
            pc.TryCatch(),
            pc.Conditionals(),
        ],
        True,
        sy.CompileTimeError(),
        rc.IncorrectSequence(),
        ct.Environment(),
        16
    ),
    JavaBug(
        "9.JDK-8177933",
        [
            pc.FunctionReferences(),
            pc.ParameterizedTypes(),
            pc.UseVariance(),
            pc.Overriding()
        ],
        True,
        sy.InternalCompilerError(),
        rc.ExtraneousComputation(),
        ct.Mechanics(),
        46
    ),
    JavaBug(
        "10.JDK-8013394",
        [
            pc.ParameterizedClasses(),
            pc.BoundedPolymorphism(),
            pc.Import(),
            pc.Overriding(),
            pc.ParameterizedTypes(),
            pc.Loops()
        ],
        True,
        sy.CompileTimeError(),
        rc.WrongParams(),
        ct.Environment(), # During Environment building
        27
    ),
    JavaBug(
        "11.JDK-8027253",
        [
            pc.ParameterizedClasses(),
            pc.BoundedPolymorphism(),
            pc.Arrays()
        ],
        False,
        sy.WrongResult(), #?
        rc.FunctionalSpecificationMismatch(),
        ct.Declarations(),
        1
    ),
    JavaBug(
        "12.JDK-8236546",
        [
            pc.Conditionals(),
            pc.Subtyping()
        ],
        False,
        sy.InternalCompilerError(),
        rc.WrongDataReference(),
        ct.OtherSemanticChecking(), # Analyze an expression..
        7
    ),
    JavaBug(
        "13.JDK-8175790",
        [
            pc.ParameterizedFunctions(),
            pc.FunctionalInterface(),
            pc.Collections(),
            pc.UseVariance(),
            pc.TypeArgsInference(),
            pc.ParameterizedTypes(),
            pc.Lambdas()
        ],
        False,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.Mechanics(),
        26
    ),
    JavaBug(
        "14.JDK-8069265",
        [
            pc.Collections(),
            pc.ParameterizedTypes(),
            pc.TypeArgsInference(),
            pc.Cast()
        ],
        True,
        sy.Runtime(sy.ClassCastException()),
        rc.IncorrectCondition(),
        ct.Mechanics(),
        14
    ),
    JavaBug(
        "15.JDK-8009131",
        [
            pc.Lambdas()
        ],
        False,
        sy.Runtime(), # Ambiguous?
        rc.InsufficientAlgorithmImplementation(),
        ct.Resolution(),
        11
    ),
    JavaBug(
        "16.JDK-8211102",
        [
            pc.Collections(),
            pc.TypeArgsInference(),
            pc.ParameterizedTypes(),
            pc.AnonymousClass(),
            pc.Conditionals()
        ],
        True,
        sy.InternalCompilerError(),
        rc.IncorrectSequence(), # ExtraneousComputation?
        ct.OtherSemanticChecking(),
        7
    ),
    JavaBug(
        "17.JDK-8161383",
        [
            pc.NestedDeclaration(),
            pc.Inheritance()
        ],
        True,
        sy.InternalCompilerError(),
        rc.IncorrectSequence(),
        ct.Environment(),
        11
    ),
    JavaBug(
        "18.JDK-7020657",
        [
            pc.Collections(),
            pc.ParameterizedTypes(),
            pc.Overriding()
        ],
        True,
        sy.CompileTimeError(),
        rc.IncorrectCondition(),
        ct.Resolution(),
        13
    ),
    JavaBug(
        "19.JDK-8034048",
        [
            pc.FunctionReferences(),
            pc.Varargs(),
            pc.ParameterizedFunctions(),
            pc.FunctionalInterface()
        ],
        False,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.Approximation(),
        5
    ),
    JavaBug(
        "20.JDK-8173456",
        [
            pc.FunctionalInterface(),
            pc.ParameterizedTypes(),
            pc.Inheritance(),
            pc.FunctionReferences(),
            pc.NestedDeclaration()
        ],
        False,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.Declarations(),
        23
    ),
]
