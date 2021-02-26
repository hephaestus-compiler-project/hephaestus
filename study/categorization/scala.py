from bug import ScalaBug
import categories as ct
import characteristics as pc
import symptoms as sy
import root_causes as rc


scala_iter1 = [
    ScalaBug(
        "1.Scala2-8675",
        [pc.Arrays(), pc.Loops()],
        False,
        sy.InternalCompilerError(),
        rc.IncorrectCondition(),
        ct.Mechanics(), # error reporting
        9
    ),
    ScalaBug(
        "2.Scala2-11843",
        [pc.Cast()],
        False,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.Environment(),
        1
    ),
    ScalaBug(
        "3.Dotty-5636",
        [pc.ParameterizedClasses(),
         pc.ParameterizedTypes(),
         pc.DependentTypes(),
         pc.Inheritance()
         ],
        True,
        sy.CompileTimeError(),
        rc.IncorrectCondition(),
        ct.TypeExpression(),
        7
    ),
    ScalaBug(
        "4.Dotty-8802",
        [
         pc.DependentTypes(),
         pc.ParameterizedTypes(),
         pc.ParameterizedClasses(),
         pc.ParameterizedFunctions(),
         pc.ImplicitParameters(),
         pc.ImplicitDefs(),
         pc.Typedefs(),
        ],
        True,
        sy.CompileTimeError(),
        rc.DesignIssue(), 
        ct.Approximation(),
        11
    ),
    ScalaBug(
        "5.Dotty-4509",
        [
         pc.ImplicitParameters(),
         pc.FunctionTypes(),
         pc.ErasedParameters(),
         pc.Lambdas()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Mechanics(),  # transformation /desugaring
        4
    ),
    ScalaBug(
        "6.Scala2-5878",
        [
         pc.DataClasses(),
         pc.Inheritance()
        ],
        False,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        pc.Declaration(),
        2
    ),
    ScalaBug(
        "7.Scala2-5886",
        [
            pc.ParameterizedFunctions(),
            pc.Lambdas(),
            pc.CallByName(),
        ],
        True,
        sy.CompileTimeError(),
        rc.ExtraneousComputation(),
        ct.Resolution(),
        8
    ),
    ScalaBug(
        "8.Scala2-7928",
        [
            pc.Inheritance(), pc.NestedDeclaration(),
            pc.Collections(), pc.ParameterizedTypes(),
            pc.Overriding(), pc.DependentTypes(), pc.Typedefs(),
            pc.Subtyping()
        ],
        False,
        sy.InternalCompilerError(),
        rc.IncorrectCondition(),
        ct.Mechanics(),  # transformation
        13
    ),
    ScalaBug(
        "9.Dotty-1757",
        [
            pc.ParameterizedClasses(),
            pc.ParameterizedTypes(),
            pc.DataClasses(),
            pc.DefaultInitializer()
        ],
        False,
        sy.InternalCompilerError(),
        rc.IncorrectComputation(), 
        ct.Inference(),  # type variable substitution
        4
    ),
    ScalaBug(
        "10.Dotty-6146",
        [
            pc.ParameterizedClasses(),
            pc.ParameterizedTypes(),
            pc.FBounded(),
            pc.ExistentialTypes(),
            pc.Inheritance(),
            pc.SealedClasses(), pc.ImplicitParameters(), pc.ImplicitDefs()
        ],
        True,
        sy.CompileTimeError(),
        rc.IncorrectSequence(), 
        ct.SubtypingRelated(),
        9
    ),
    ScalaBug(
        "11.Scala2-9542",
        [pc.Inheritance(), pc.NestedDeclaration(),
         pc.ParameterizedClasses(), pc.ParameterizedTypes()],
        True,
        sy.InternalCompilerError(),
        rc.WrongParams(),
        ct.Mechanics(),  # transformation
        24
    ),
    ScalaBug(
        "12.Dotty-2234",
        [
            pc.ParameterizedClasses(),
            pc.ParameterizedTypes(),
            pc.Overloading()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(), 
        ct.Approximation(),
        3
    ),
    ScalaBug(
        "13.Scala-9361",
        [
            pc.HigherKindedTypes(),
            pc.Overriding(),
            pc.Subtyping(),
            pc.Nothing()
        ],
        False,
        sy.InternalCompilerError(),
        rc.IncorrectCondition(),
        ct.Mechanics(),  # error reporting
        5
    ),
    ScalaBug(
        "14.Scala2-4098",
        [
            pc.This()
        ],
        False,
        sy.Runtime(sy.VerifyError()),
        rc.MissingCase(),
        ct.OtherSemanticChecking(),
        6
    ),
    ScalaBug(
        "15.Dotty-10325",
        [
            pc.ParameterizedFunctions(),
            pc.Collections(),
            pc.Overloading(),
            pc.FunctionReferences(),
            pc.ParameterizedTypes()
        ],
        True,
        sy.CompileTimeError(),
        rc.ExtraneousComputation(),
        ct.TypeExpression(), 
        7
    ),
    ScalaBug(
        "16.Dotty-9044",
        [
            pc.ParameterizedClasses(), pc.ParameterizedFunctions(),
            pc.ParameterizedTypes(), pc.HigherKindedTypes(),
            pc.DeclVariance(), pc.AlgebraicDataTypes(),
            pc.Subtyping(), pc.ImplicitParameters(), pc.PatMat()
        ],
        False,
        sy.MisleadingReport(),
        rc.DesignIssue(),
        ct.Approximation(),
        9
    ),
    ScalaBug(
        "17.Dotty-4470",
        [
            pc.Enums()
        ],
        False,
        sy.InternalCompilerError(),
        rc.MissingCase(), 
        ct.Mechanics(),  # transformation / desugaring
        6
    ),
    ScalaBug(
        "18.Dotty-8752",
        [
            pc.TypeLambdas(), pc.ParameterizedClasses(),
            pc.FBounded(), pc.ParameterizedTypes()
        ],
        False,
        sy.MisleadingReport(),
        rc.MissingCase(), 
        ct.OtherSemanticChecking(),
        2
    ),
    ScalaBug(
        "19.Scala2-10185",
        [
            pc.ParameterizedTypes(), pc.ParameterizedClasses(),
            pc.BoundedPolymorphism(), pc.HigherKindedTypes(),
            pc.AlgebraicDataTypes(), pc.PatMat()
        ],
        True,
        sy.CompileTimeError(),
        rc.IncorrectComputation(),
        ct.SubtypingRelated(),
        8
    ),
    ScalaBug(
        "20.Dotty-5188",
        [
            pc.Inline(), pc.Varargs()
        ],
        True,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.Declarations(), 
        4
    )

]


scala_iter2 = [
    ScalaBug(
        "1.Scala2-8763",
        [
            pc.Collections(), pc.PatMat(),
            pc.Arrays()
        ],
        False,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.Mechanics()  # error reporting
    ),
    ScalaBug(
        "2.Scala2-5231",
        [
            pc.AccessModifiers(), pc.ImplicitDefs()
        ],
        False,
        sy.InternalCompilerError(),
        rc.IncorrectCondition(),
        ct.TypeExpression()
    ),
    ScalaBug(
        "3.Scala2-11239",
        [
            pc.ParameterizedClasses(), pc.Typedefs(),
            pc.HigherKindedTypes(), pc.DataClasses(),
            pc.BoundedPolymorphism(), pc.ParameterizedTypes(),
            pc.TypeProjections()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.SubtypingRelated()
    ),
    ScalaBug(
        "4.Dotty-9735",
        [
            pc.Typedefs(), pc.TypeLambdas(),
            pc.ParameterizedTypes()
        ],
        False,
        sy.MisleadingReport(),
        rc.IncorrectCondition(),
        ct.OtherSemanticChecking()
    ),
    ScalaBug(
        "5.Scala2-10886",
        [
            pc.Import(),
        ],
        True,
        sy.CompileTimeError(),
        rc.WrongParams(),
        ct.TypeExpression(),  # wrong information from context
    ),
    ScalaBug(
        "6.Dotty-9803",
        [
            pc.Overloading(), pc.Import()
        ],
        False,
        sy.MisleadingReport(),
        rc.WrongParams(),
        ct.Resolution()
    ),
    ScalaBug(
        "7.Dotty-5140",
        [
            pc.JavaInterop(), pc.Arrays(),
            pc.Import(), pc.Varargs()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Approximation()
    ),
    ScalaBug(
        "8.Dotty-4487",
        [
            pc.Inheritance(), pc.FunctionTypes()
        ],
        False,
        sy.InternalCompilerError(),
        rc.DesignIssue(),
        ct.TypeExpression()
    ),
    ScalaBug(
        "9.Dotty-3585",
        [
            pc.ParameterizedClasses(),
            pc.ParameterizedTypes(),
            pc.CallByName(),
            pc.ImplicitDefs(),
            pc.ImplicitParameters()
        ],
        True,
        sy.InternalCompilerError(),
        rc.WrongParams(),
        ct.Resolution()
    ),
    ScalaBug(
        "10.Dotty-9631",
        [
            pc.ParameterizedTypes(),
            pc.ParameterizedFunctions(),
            pc.FBounded(),
            pc.NestedDeclaration(),
            pc.Inheritance(),
            pc.ParameterizedFunctions(),
            pc.ImplicitParameters(),
            pc.ExistentialTypes(),
            pc.PatMat()
        ],
        True,
        sy.CompileTimeError(),
        rc.IncorrectComputation(),
        ct.SubtypingRelated()
    ),
    ScalaBug(
        "11.Dotty-10217",
        [
            pc.UnionTypes(), pc.ParameterizedClasses(),
            pc.ParameterizedTypes()
        ],
        True,
        sy.CompilationPerformance(),
        rc.AlgorithmImproperlyImplemented(),
        ct.SubtypingRelated()
    ),
    ScalaBug(
        "12.Scala2-7482",
        [
            pc.JavaInterop(), pc.Collections(),
            pc.ParameterizedTypes()
        ],
        True,
        sy.CompileTimeError(),
        rc.IncorrectCondition(),
        ct.Approximation()
    ),
    ScalaBug(
        "13.Scala2-5454",
        [
            pc.ImplicitDefs(), pc.ImplicitParameters(),
            pc.Inheritance(), pc.ParameterizedClasses()
        ],
        True,
        sy.CompileTimeError(),
        rc.DesignIssue(),
        ct.Environment()
    ),
    ScalaBug(
        "14.Scala2-6714",
        [
            pc.Overriding(), pc.ImplicitDefs(),
            pc.ImplicitParameters(), pc.ArithmeticExpressions()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Mechanics()  # transformation
    ),
    ScalaBug(
        "15.Dotty-3917",
        [
            pc.Inheritance()
        ],
        True,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.Mechanics()  # transformation
    ),
    ScalaBug(
        "16.Dotty-2723",
        [
            pc.Inline(), pc.ImplicitParameters(), pc.FunctionTypes()
        ],
        True,
        sy.InternalCompilerError(),
        rc.IncorrectDataType(),
        ct.Mechanics()  # Transformation
    ),
    ScalaBug(
        "17.Dotty-4030",
        [
            pc.Inheritance(), pc.AlgebraicDataTypes(),
            pc.ParameterizedClasses(), pc.ParameterizedTypes(),
            pc.BoundedPolymorphism(), pc.FunctionTypes(),
            pc.UnionTypes(), pc.ExistentialTypes()
        ],
        True,
        sy.CompileTimeError(),
        rc.IncorrectCondition(),
        ct.TypeExpression()
    ),
    ScalaBug(
        "18.Scala2-10536",
        [
            pc.ParameterizedClasses(), pc.ImplicitParameters(),
            pc.FBounded(), pc.BoundedPolymorphism(),
            pc.AlgebraicDataTypes(), pc.Overloading(),
            pc.ParameterizedTypes()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Approximation()
    ),
    ScalaBug(
        "19.Dotty-9749",
        [
            pc.Varargs()
        ],
        False,
        sy.Runtime(sy.WrongMethodCalled()),
        rc.MissingCase(),
        ct.Declarations()
    ),
    ScalaBug(
        "20.Dotty-3422",
        [
            pc.HigherKindedTypes(), pc.NestedDeclaration(),
            pc.ParameterizedClasses(),
            pc.DependentTypes(), pc.ParameterizedTypes()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.SubtypingRelated()
    )
]
