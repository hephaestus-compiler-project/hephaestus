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
        ct.Mechanics()  # error reporting
    ),
    ScalaBug(
        "2.Scala2-11843",
        [pc.Cast()],
        False,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.Environment()
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
        ct.Approximation()
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
        ct.Mechanics()  # transformation /desugaring
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
        pc.Declaration()
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
        ct.Resolution()
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
        ct.Mechanics()  # transformation
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
        rc.DesignIssue(),
        ct.Inference()  # type variable substitution
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
        rc.MissingCase(),
        ct.SubtypingRelated(),
    ),
    ScalaBug(
        "11.Scala2-9542",
        [pc.Inheritance(), pc.NestedDeclaration(),
         pc.ParameterizedClasses(), pc.ParameterizedTypes()],
        True,
        sy.InternalCompilerError(),
        rc.WrongParams(),
        ct.Mechanics()  # transformation
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
        ct.Approximation()
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
        ct.Mechanics()  # error reporting
    ),
    ScalaBug(
        "14.Scala2-4098",
        [
            pc.This()
        ],
        False,
        sy.Runtime(sy.VerifyError()),
        rc.MissingCase(),
        ct.OtherSemanticChecking()
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
        ct.TypeExpression()
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
        ct.Approximation()
    ),
    ScalaBug(
        "17.Dotty-4470",
        [
            pc.Enums()
        ],
        False,
        sy.InternalCompilerError(),
        rc.ExtremeConditionNeglected(),
        ct.Mechanics()  # transformation / desugaring
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
        ct.OtherSemanticChecking()
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
        ct.SubtypingRelated()
    ),
    ScalaBug(
        "20.Dotty-5188",
        [
            pc.Inline(), pc.Varargs()
        ],
        True,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.TypeExpression()
    )

]
