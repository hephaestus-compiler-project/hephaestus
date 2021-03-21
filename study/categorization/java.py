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
    # Note: I see  Bounded Polymorphism characteristic is common in java bugs (18/60) approximately 30% frequency , maybe consider it for paper section about java bugs
    JavaBug(
        "1.JDK-8152832",  # regression
        # pc.FunctionReferences() strings::stream
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
        # nice bug with a good comment explanation, maybe consider it for paper
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
        # no pc.ParameterizedClasses() in test case, but if we consider the declaration of Comparable<T> part of test case its also pc.SAM() , pc.Inheritance(),
        [
            pc.Overriding(), pc.Overloading(),
            pc.ParameterizedClasses(),
            pc.ParameterizedTypes()
        ],
        False,
        sy.Runtime(sy.ClassCastException()),
        # rc.FunctionalSpecificationMismatch() becasue in the fix we see a new addition of checkClasses method in Check.java with the following comment:
        #    /** Check that all non-override equivalent methods accessible from 'site'  are mutually compatible (JLS 8.4.8/9.4.1).
        rc.MissingCase(),
        ct.Resolution(),
        13
    ),
    JavaBug(
        # regression bug (This is a regression, the code was providing the right error message in JDK 7.)
        "4.JDK-8029569",
        # pc.StaticMethod()
        [pc.Varargs(), pc.Overloading()],
        False,
        sy.InternalCompilerError(),
        rc.IncorrectDataType(),
        ct.Resolution(),
        8
    ),
    JavaBug(
        # regression bug 
        "5.JDK-8075793",
        # pc.Cast() ( return new HashSet<>(set);)
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
        # pc.ParamTypeInference()
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
        # False 
        # The below code should throw a compilation error as there is no result expression for the switch expression.
        # However, the compilation goes through successfully.
        True,
        # maybe a category for code which should be rejected by compiler but its accepted with no warnings or errors and can be executed
        sy.Runtime(),
        rc.MissingCase(),
        # ct.TypeExpression check of switch expression, if caseTypes.isEmpty())
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
        # rc.FunctionalSpecificationMismatch() see descritpion of bug:
        #  Here is the relevant text for JLS8 9.6.3 "Repeatable Annotation Types"
        # which is aware of the TYPE_USE construct from JSR 308:
        # T is applicable to at least the same kinds of program etc. etc.
        rc.DesignIssue(),
        ct.TypeComparison(),
        10
    ),
    JavaBug(
        # regression bug
        "10.JDK-7041730",
        # pc.PrimitiveTypes() cast from int to Byte, int is primitive, it is also shown in the fix or comments that the bug is related to primitive types
        [pc.Cast()],
        False,
        sy.Runtime(sy.ClassCastException()),
        rc.IncorrectComputation(),
        ct.TypeComparison(),
        3
    ),
    JavaBug(
        "11.JDK-8020804",
        # pc.SAM() (Supplier<D>), pc.Collections() (LinkedList)
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
        # pc.SAM() (A and B)
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
        # pc.ParamTypeInference(), pc.SAM() (callable)
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
        # same symptom with JDK-8226510
        sy.Runtime(),
        # agreed, also consider rc.IncorrectSequence()
        # Static-ness check should be applied after member reference resolution
        rc.MissingCase(),
        ct.OtherSemanticChecking(),
        17
    ),
    JavaBug(
        "16.JDK-8188144",  # regression
        [pc.ParameterizedTypes(), pc.FunctionReferences(), pc.FunctionalInterface()],
        True,
        sy.Runtime(sy.WrongResult()),
        # I agree with rc.IncorrectComputation() because:
        # The correct selection logic is already implemented in ReferenceChooser.result - but unfortunately the result of the 'choice' is too lossy,
        rc.IncorrectComputation(), # MissingCase
        ct.Resolution(),
        9
    ),
    JavaBug(
        # regression
        "17.JDK-8171993",
        # pc.BoundedPolymorphism() (<T extends String> works with <T> alone), no pc.ParameterizedTypes()
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
        # pc.SAM() (Func interface)
        [pc.ParameterizedFunctions(), pc.ParameterizedClasses(),
         pc.ParameterizedTypes()],
        True,
        sy.CompileTimeError(),
        rc.IncorrectComputation(),
        ct.Inference(),
        10
    ),
    JavaBug(
        # regression bug
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
            pc.Overloading(),
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
            pc.ParameterizedTypes(),
            pc.Inheritance(),
            pc.BoundedPolymorphism(),
            pc.FBounded()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.TypeComparison(),
        9
    ),
    JavaBug(
        "3.JDK-7142086",
        [
            pc.Overloading(),
            pc.Overriding()
        ],
        True,
        sy.CompilationPerformance(),
        rc.IncorrectComputation(),
        ct.Declarations(),
        84
    ),
    JavaBug(
        "4.JDK-8131915",
        [
            pc.TypeAnnotations(),
            pc.Import()
        ],
        False,
        sy.InternalCompilerError(),
        rc.WrongDataReference(),
        ct.Mechanics(),
        55
    ),
    JavaBug(
        "5.JDK-7148242",
        [
            pc.ParameterizedClasses(),
            pc.ParameterizedTypes(),
            pc.NestedDeclaration(),
            pc.BoundedPolymorphism()
        ],
        True,
        sy.CompileTimeError(),
        rc.ExtraneousComputation(),
        ct.Declarations(),
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
        ct.OtherSemanticChecking(),
        5
    ),
    JavaBug(
        "7.JDK-8209173",
        [
            pc.JavaInterop(),
            pc.ParameterizedTypes()
        ],
        False,
        sy.InternalCompilerError(),
        rc.WrongDataReference(),
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
        ct.OtherSemanticChecking(),
        16
    ),
    JavaBug(
        "9.JDK-8177933",
        [
            pc.StandardFeatures()
        ],
        True,
        sy.InternalCompilerError(),
        rc.ExtraneousComputation(),
        ct.TypeExpression(),
        46
    ),
    JavaBug(
        "10.JDK-8013394",
        [
            pc.Collections(),
            pc.ParameterizedClasses(),
            pc.Inheritance(),
            pc.ParameterizedTypes(),
            pc.Loops()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Mechanics(), # Desugaring
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
        sy.Runtime(sy.WrongResult()),
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
        rc.IncorrectCondition(),
        ct.TypeExpression(),
        7
    ),
    JavaBug(
        "13.JDK-8175790",
        [
            pc.ParameterizedFunctions(),
            pc.FunctionalInterface(),
            pc.Collections(),
            pc.Subtyping(),
            pc.UseVariance(),
            pc.TypeArgsInference(),
            pc.ParameterizedTypes(),
            pc.Lambdas()
        ],
        False,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.Mechanics(), # Error Reporting
        26
    ),
    JavaBug(
        "14.JDK-8069265",
        [
            pc.Collections(),
            pc.ParameterizedTypes(),
            pc.TypeArgsInference(),
            pc.WildcardType(), #TODO
            pc.Cast()
        ],
        True,
        sy.Runtime(sy.ClassCastException()),
        rc.DesignIssue(),
        ct.Approximation(),
        14
    ),
    JavaBug(
        "15.JDK-8009131",
        [
            pc.Lambdas(),
            pc.SAM(),
            pc.ParamTypeInference(),
            pc.Overloading()
        ],
        False,
        sy.Runtime(sy.WrongResult()),
        rc.InsufficientAlgorithmImplementation(),
        ct.Resolution(), # TypeExpression
        11
    ),
    JavaBug(
        "16.JDK-8211102",
        [
            pc.Collections(),
            pc.TypeArgsInference(),
            pc.Overriding(),
            pc.ParameterizedTypes(),
            pc.AnonymousClass(),
            pc.Conditionals()
        ],
        True,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.OtherSemanticChecking(),
        7
    ),
    JavaBug(
        "17.JDK-8161383",
        [
            pc.NestedDeclaration(),
            pc.AugmentedAssignment(), #TODO
            pc.Inheritance(),
            pc.AccessModifiers()
        ],
        True,
        sy.InternalCompilerError(),
        rc.IncorrectComputation(),
        ct.Resolution(),
        11
    ),
    JavaBug(
        "18.JDK-7020657",
        [
            pc.Collections(),
            pc.ParameterizedTypes(),
            pc.MultipleImplements(),
            pc.Overriding()
        ],
        True,
        sy.CompileTimeError(),
        rc.FunctionalSpecificationMismatch(),
        ct.Declarations(),
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
        True,
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
            pc.AccessModifiers(),
            pc.Inheritance(),
            pc.FunctionReferences(),
            pc.NestedDeclaration()
        ],
        False,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.Resolution(),
        23
    ),
]
