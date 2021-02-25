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
        rc.FunctionalSpecificationMismatch(),  # incorrect computation
        ct.SubtypingRelated()
    ),
    JavaBug(
        "2.JDK-8254557",
        [pc.Streams(), pc.FunctionalInterface(),
         pc.ParameterizedFunctions(), pc.AnonymousClass(),
         pc.Lambdas(), pc.Conditionals(), pc.Reflection()
         ],
        False,
        sy.InternalCompilerError(),
        rc.MissingMethod(),  # XXX Missing case
        ct.TypeExpression()
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
        ct.Mechanics()  # transformation
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
        ct.Inference()
    ),
    JavaBug(
        "5.JDK-8231461",
        [pc.FunctionReferences(),
         pc.StaticMethod(), pc.Overloading(),
         ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Resolution()
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
        ct.Inference()  # constraint solving
    ),
    JavaBug(
        "7.JDK-8006749",
        [pc.SAM(),
         pc.Lambdas(), pc.ParamTypeInference()
         ],
        False,
        sy.MisleadingReport(),
        rc.MissingCase(),
        ct.TypeExpression()
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
        ct.SubtypingRelated()
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
        ct.Inference()  # type variable substitution
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
        ct.Environment()
    ),
    JavaBug(
        "11.JDK-8129214",
        [pc.Import(),
         pc.ParameterizedFunctions(), pc.BoundedPolymorphism()
         ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Approximation()
    ),
    JavaBug(
        "12.JDK-8203277",
        [pc.Collections(), pc.FunctionalInterface(),
         pc.Overriding(), pc.Lambdas()
         ],
        True,
        sy.InternalCompilerError(),
        rc.MissingMethod(),  # missing case
        ct.Mechanics()  # transformation
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
        ct.Resolution()
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
    ),
    JavaBug(
        "15.JDK-8144832",
        [
            pc.ParameterizedClasses(), pc.Cast(), pc.PrimitiveTypes()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Approximation()
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
        ct.SubtypingRelated()
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
        ct.Environment()
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
        ct.Inference()  # type variable substitution
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
        ct.Approximation()
    )
]
