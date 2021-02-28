from bug import JavaBug
import categories as ct
import characteristics as pc
import symptoms as sy
import root_causes as rc


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
        ct.SubtypingRelated(),
        9
    ),
    JavaBug(
        "2.JDK-8254557",
        [pc.Streams(), pc.FunctionalInterface(),
         pc.ParameterizedFunctions(), pc.AnonymousClass(),
         pc.Lambdas(), pc.Conditionals(), pc.Reflection(),
         pc.TypeArgsInference()
         ],
        False,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.TypeExpression(),
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
        ct.Mechanics(),  # transformation
        17
    ),
    JavaBug(
        "4.JDK-8191802",
        [pc.ParameterizedClasses(), pc.BoundedPolymorphism(),
         pc.ParameterizedTypes(),
         pc.Subtyping(), pc.VarTypeInference()
         ],
        True,
        sy.CompileTimeError(),
        rc.FunctionalSpecificationMismatch(),
        ct.Inference(),
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
        rc.InsufficientFunctionality(),
        ct.Inference(),  # constraint solving
        16
    ),
    JavaBug(
        "7.JDK-8006749",
        [pc.SAM(),
         pc.Lambdas(), pc.ParamTypeInference()
         ],
        False,
        sy.MisleadingReport(),
        rc.MissingCase(),
        ct.TypeExpression(),
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
        ct.SubtypingRelated(),
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
        ct.Inference(),  # type variable substitution
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
        ct.Environment(), # TypeExpression
        9
    ),
    JavaBug(
        "11.JDK-8129214",
        [pc.Import(),
         pc.ParameterizedFunctions(), pc.BoundedPolymorphism()
         ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),  # missing step
        ct.Approximation(),
        10
    ),
    JavaBug(
        "12.JDK-8203277",
        [pc.Collections(), pc.FunctionalInterface(),
         pc.Overriding(), pc.Lambdas()
         ],
        True,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.Mechanics(),  # transformation
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
        14
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
            pc.Cast(), pc.StaticMethod(), pc.FunctionReferences()
        ],
        True,
        sy.CompileTimeError(),
        rc.WrongParams(),
        ct.SubtypingRelated(),
        7
    ),
    JavaBug(
        "17.JDK-6996914",
        [
            pc.NestedDeclaration(), pc.Subtyping(), pc.ParameterizedClasses(),
            pc.TypeArgsInference()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Environment(),
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
        16
    ),
    JavaBug(
        "19.JDK-7034511",
        [pc.Arrays(), pc.ParameterizedClasses(),
         pc.BoundedPolymorphism(), pc.ParameterizedTypes(),
         pc.Overriding(), pc.Subtyping()
         ],
        False,
        sy.Runtime(sy.ClassCastException()),
        rc.WrongParams(),
        ct.Inference(),  # type variable substitution
        8
    ),
    JavaBug(
        "20.JDK-8148354",
        [
            pc.FunctionalInterface(),
            pc.FunctionReferences(),
            pc.ParameterizedFunctions(), pc.BoundedPolymorphism(),
            pc.ParameterizedTypes(),
        ],
        True,
        sy.CompileTimeError(),
        rc.IncorrectComputation(),
        ct.Approximation(),
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
    ),
    JavaBug(
        "2.JDK-7042566",
        [
            pc.Overloading(), pc.Varargs()
        ],
        True,
        sy.CompileTimeError(),
        rc.WrongParams(),
        rc.AlgorithmImproperlyImplemented(),
        ct.Resolution()
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
        ct.Declarations()
    ),
    JavaBug(
        "4.JDK-8029569",
        [pc.Cast(), pc.Varargs(), pc.Overloading()],
        False,
        sy.InternalCompilerError(),
        rc.IncorrectDataType(),
        ct.Resolution()
    ),
    JavaBug(
        "5.JDK-JDK-8075793",
        [
            pc.Collections(), pc.ParameterizedFunctions(),
            pc.UseVariance(), pc.ParameterizedTypes()
        ],
        True,
        sy.CompileTimeError(),
        rc.DesignIssue(),
        ct.Inference(),  # constraint solving
    ),
    JavaBug(
        "6.JDK-8016081",
        [pc.TypeAnnotations(), pc.Lambdas(), pc.Conditionals(), pc.SAM()],
        True,
        sy.CompileTimeError(),
        rc.IncorrectCondition(),
        ct.Environment()
    ),
    JavaBug(
        "7.JDK-8226510",
        [pc.Conditionals(), pc.TryCatch()],
        True,
        sy.Runtime(),
        rc.MissingCase(),
        ct.OtherSemanticChecking()
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
        ct.SubtypingRelated()
    ),
    JavaBug(
        "9.JDK-8029017",
        [pc.TypeAnnotations()],
        True,
        sy.CompileTimeError(),
        rc.DesignIssue(),
        ct.SubtypingRelated()
    ),
    JavaBug(
        "10.JDK-7041730",
        [pc.Cast()],
        False,
        sy.Runtime(sy.ClassCastException()),
        rc.IncorrectComputation(),
        ct.SubtypingRelated()
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
        rc.IncorrectCondition(),
        ct.Approximation()
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
        ct.Resolution()
    ),
    JavaBug(
        "13.JDK-8189838",
        [
            pc.BoundedPolymorphism(), pc.ParameterizedClasses(),
            pc.Collections(), pc.ParameterizedTypes(),
            pc.TypeArgsInference(), pc.IntersectionTypes()
        ],
        True,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.Approximation()
    ),
    JavaBug(
        "14.JDK-8011376",
        [
            pc.Lambdas(), pc.TryCatch(), pc.ParameterizedFunctions(),
            pc.ParameterizedTypes()
        ],
        True,
        sy.CompileTimeError(),
        rc.WrongParams(),
        ct.TypeExpression()
    ),
    JavaBug(
        "15.JDK-8008537",
        [pc.FunctionReferences(), pc.Overloading()],
        False,
        sy.Runtime(),
        rc.MissingCase(),
        ct.OtherSemanticChecking()
    ),
    JavaBug(
        "16.JDK-8188144",  # regression
        [pc.FunctionReferences(), pc.FunctionalInterface()],
        True,
        sy.Runtime(sy.WrongResult()),
        rc.IncorrectComputation(),
        ct.Resolution()
    ),
    JavaBug(
        "17.JDK-8171993",
        [
            pc.Varargs(), pc.TypeArgsInference(), pc.ParameterizedClasses(),
            pc.FunctionReferences(), pc.FunctionalInterface()
        ],
        True,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.Mechanics()
    ),
    JavaBug(
        "18.JDK-8010303",
        [pc.ParameterizedFunctions(), pc.ParameterizedClasses(),
         pc.ParameterizedTypes()],
        True,
        sy.CompileTimeError(),
        rc.IncorrectComputation(),
        ct.Inference()
    ),
    JavaBug(
        "19.JDK-6835428",
        [
            pc.UseVariance(), pc.Subtyping(),
            pc.ParameterizedFunctions(), pc.Collections(),
            pc.BoundedPolymorphism()
        ],
        True,
        sy.CompileTimeError(),
        rc.ExtraneousComputation(),
        ct.Inference(),  # constraint solving
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
        ct.Inference()  # constraint solving
    )
]
