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
        ct.ErrorReporting(),
        #  10
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
        ct.Resolution(),
        7
    ),
    ScalaBug(
        "4.Dotty-8802",
        [
         pc.DependentTypes(),
         pc.ParameterizedTypes(),
         pc.ParameterizedClasses(),
         pc.ParameterizedFunctions(),
         pc.TypeArgsInference(),
         pc.Implicits(),
         pc.Typedefs(),
        ],
        True,
        sy.CompileTimeError(),
        rc.DesignIssue(),
        ct.Inference(),
        11
    ),
    ScalaBug(
        "5.Dotty-4509",
        [
         pc.Implicits(),
         pc.FunctionTypes(),
         pc.ErasedParameters(),
         pc.Lambdas()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Transformation(),
        4
    ),
    ScalaBug(
        "6.Scala2-5878",
        [
         pc.ValueClasses(),
         pc.Inheritance()
        ],
        False,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.Declarations(),
        2
    ),
    ScalaBug(
        "7.Scala2-5886",
        [
            pc.ParameterizedFunctions(),
            pc.TypeArgsInference(),
            pc.Reflection(),
            pc.CallByName(),
            pc.FunctionTypes()
        ],
        True,
        sy.CompileTimeError(),
        rc.ExtraneousComputation(),
        ct.TypeExpression(),
        8
    ),
    ScalaBug(
        "8.Scala2-7928",
        [
            pc.Inheritance(), pc.NestedClasses(),
            pc.Collections(), pc.ParameterizedTypes(),
            pc.Overriding(), pc.DependentTypes(), pc.Typedefs(),
            pc.Subtyping()
        ],
        False,
        sy.InternalCompilerError(),
        rc.IncorrectCondition(),
        ct.Transformation(),
        13
    ),
    ScalaBug(
        "9.Dotty-1757",
        [
            pc.ParameterizedClasses(),
            pc.ParameterizedTypes(),
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
            pc.WildCardType(),
            pc.Inheritance(),
            pc.SealedClasses(),
            pc.Implicits()
        ],
        True,
        sy.CompileTimeError(),
        rc.IncorrectSequence(),
        ct.TypeComparison(),
        9
    ),
    ScalaBug(
        "11.Scala2-9542",
        [pc.Inheritance(), pc.NestedClasses(),
         pc.ParameterizedClasses(), pc.ParameterizedTypes()],
        True,
        sy.InternalCompilerError(),
        rc.WrongParams(),
        ct.Transformation(),
        24
    ),
    ScalaBug(
        "12.Dotty-2234",
        [
            pc.ParameterizedClasses(),
            pc.ParameterizedTypes(),
            pc.Overloading(),
            pc.Typedefs()
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
            pc.Nothing(),
            pc.Typedefs(),
            pc.TypeArgsInference()
        ],
        False,
        sy.InternalCompilerError(),
        rc.IncorrectCondition(),
        ct.ErrorReporting(),
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
            pc.TypeArgsInference(),
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
            pc.Subtyping(), pc.Implicits(), pc.PatMat()
        ],
        False,
        sy.MisleadingReport(),
        rc.DesignIssue(),
        ct.Inference(),
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
        ct.Transformation(),
        6
    ),
    ScalaBug(
        "18.Dotty-8752",
        [
            pc.TypeLambdas(), pc.ParameterizedClasses(),
            pc.FBounded(), pc.ParameterizedTypes(),
            pc.Collections()
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
            pc.AlgebraicDataTypes(), pc.PatMat(),
        ],
        True,
        sy.CompileTimeError(),
        rc.IncorrectComputation(),
        ct.TypeComparison(),
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
        ct.OtherSemanticChecking(),
        4
    )

]


scala_iter2 = [
    ScalaBug(
        "1.Scala2-8763",
        [
            pc.Collections(), pc.PatMat(),
            pc.Arrays(),
            pc.VarTypeInference(),
            pc.AugmentedAssignmentOperator()
        ],
        False,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.ErrorReporting(),
        4
    ),
    ScalaBug(
        "2.Scala2-5231",
        [
            pc.AccessModifiers(), pc.Implicits()
        ],
        False,
        sy.InternalCompilerError(),
        rc.IncorrectCondition(),
        ct.TypeExpression(),
        6
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
        ct.TypeComparison(),
        4
    ),
    ScalaBug(
        "4.Dotty-9735",
        [
            pc.Typedefs(), pc.TypeLambdas(),
            pc.ParameterizedClasses(),
            pc.OpaqueType(),
            pc.ParameterizedTypes()
        ],
        False,
        sy.MisleadingReport(),
        rc.IncorrectCondition(),
        ct.OtherSemanticChecking(),
        3
    ),
    ScalaBug(
        "5.Scala2-10886",
        [
            pc.Import(),
        ],
        True,
        sy.CompileTimeError(),
        rc.WrongParams(),
        ct.TypeExpression(),
        9
    ),
    ScalaBug(
        "6.Dotty-9803",
        [
            pc.Overloading(), pc.Import()
        ],
        False,
        sy.MisleadingReport(),
        rc.WrongParams(),
        ct.Resolution(),
        11
    ),
    ScalaBug(
        "7.Dotty-5140",
        # pc.Inheritance(), pc.Subtyping()
        [
            pc.JavaInterop(), pc.Arrays(),
            pc.Varargs(),
            pc.Inheritance(), pc.Subtyping()
        ],
        True,
        sy.InternalCompilerError(),
        rc.DesignIssue(),
        ct.Approximation(),
        10
    ),
    ScalaBug(
        "8.Dotty-4487",
        [
            pc.Inheritance(), pc.FunctionTypes(),
            pc.CallByName()
        ],
        False,
        sy.InternalCompilerError(),
        rc.DesignIssue(),
        ct.TypeExpression(),
        1
    ),
    ScalaBug(
        "9.Dotty-3585",
        [
            pc.ParameterizedClasses(),
            pc.ParameterizedTypes(),
            pc.CallByName(),
            pc.Implicits(),
        ],
        True,
        sy.InternalCompilerError(),
        rc.WrongParams(),
        ct.Resolution(),
        13
    ),
    ScalaBug(
        "10.Dotty-9631",
        [
            pc.ParameterizedTypes(),
            pc.ParameterizedFunctions(),
            pc.FBounded(),
            pc.NestedClasses(),
            pc.Inheritance(),
            pc.Implicits(),
            pc.WildCardType(),
            pc.PatMat()
        ],
        True,
        sy.InternalCompilerError(),
        rc.IncorrectComputation(),
        ct.TypeComparison(),
        15
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
        ct.TypeComparison(),
        27
    ),
    ScalaBug(
        # regression bug
        "12.Scala2-7482",
        [
            pc.JavaInterop(), pc.Collections(),
            pc.ParameterizedTypes()
        ],
        True,
        sy.CompileTimeError(),
        rc.IncorrectCondition(),
        ct.Approximation(),
        2
    ),
    ScalaBug(
        "13.Scala2-5454",
        [
            pc.Implicits(),
            pc.Inheritance(), pc.ParameterizedClasses()
        ],
        True,
        sy.CompileTimeError(),
        rc.DesignIssue(),
        ct.Environment(),
        7
    ),
    ScalaBug(
        "14.Scala2-6714",
        [
            pc.Overriding(), pc.Implicits(),
            pc.ArithmeticExpressions(),
            pc.AugmentedAssignmentOperator()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Transformation(),
        10
    ),
    ScalaBug(
        "15.Dotty-3917",
        [
            pc.Inheritance()
        ],
        True,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.Transformation(),
        8
    ),
    ScalaBug(
        "16.Dotty-2723",
        [
            pc.Inline(), pc.Implicits(), pc.FunctionTypes()
        ],
        True,
        sy.InternalCompilerError(),
        rc.IncorrectDataType(),
        ct.Transformation(),
        3
    ),
    ScalaBug(
        "17.Dotty-4030",
        [
            pc.Inheritance(), pc.AlgebraicDataTypes(),
            pc.ParameterizedClasses(), pc.ParameterizedTypes(),
            pc.BoundedPolymorphism(), pc.FunctionTypes(),
            pc.UnionTypes(), pc.WildCardType()
        ],
        True,
        sy.CompileTimeError(),
        rc.IncorrectCondition(),
        ct.TypeExpression(),
        11
    ),
    ScalaBug(
        "18.Scala2-10536",
        [
            pc.OperatorOverloading(),
            pc.ParameterizedClasses(), pc.Implicits(),
            pc.FBounded(), pc.BoundedPolymorphism(),
            pc.AlgebraicDataTypes(), pc.Overloading(),
            pc.ParameterizedTypes()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Approximation(),
        6
    ),
    ScalaBug(
        "19.Dotty-9749",
        [
            pc.Varargs()
        ],
        False,
        sy.Runtime(sy.WrongResult()),
        rc.MissingCase(),
        ct.Declarations(),
        6
    ),
    ScalaBug(
        "20.Dotty-3422",
        [
            pc.HigherKindedTypes(), pc.NestedClasses(),
            pc.ParameterizedClasses(),
            pc.DependentTypes(), pc.ParameterizedTypes()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.TypeComparison(),
        7
    )
]

scala_iter3 = [
    ScalaBug(
        "1.Dotty-10123",
        # pc.TypeArgsInference() new C(new Foo()).await.status
        [
            pc.ParameterizedClasses(),
            pc.DeclVariance(),
            pc.Implicits(),
            pc.ParameterizedTypes(),
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Inference(),
        19
    ),
    ScalaBug(
        # regression bug
        "2.Scala2-5399",
        # pc.NestedClasses()
        [
            pc.ParameterizedClasses(),
            pc.ParameterizedTypes(),
            pc.Inheritance(),
            pc.AlgebraicDataTypes(),
            pc.WildCardType(), # TODO
            pc.PatMat()
        ],
        True,
        sy.CompileTimeError(),
        #WrongDataReference()
        #should refer to Skolem normal form of an existential type
        rc.MissingCase(), #WrongDataReference(),
        ct.Approximation(),
        19
    ),
    ScalaBug(
        "3.Dotty-7597",
        [
            pc.ParameterizedFunctions(),
            pc.BoundedPolymorphism(),
            pc.TypeArgsInference(),
            pc.Overloading(),
            pc.FunctionAPI(),
            pc.AnonymousClass()
        ],
        False,
        sy.Runtime(sy.AbstractMethodError()),
        # rc.InsufficientAlgorithmImplementation()
        # "The check for a concrete class used to be simply that its `abstractTermMembers`
        # are empty. However, i7597.scala shows that this is not enough.It will not include a member
        # as long as there is a concrete member with the same signature."
        # so the root cause was an insufficient implementation of the algorithm
        rc.IncorrectComputation(),
        ct.Declarations(),
        2
    ),
    ScalaBug(
        "4.Scala2-5958",
        [
            pc.This(),
            pc.DependentTypes(),
            pc.NestedClasses()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.TypeExpression(), # Attribution
        12
    ),
    ScalaBug(
        "5.Scala2-7872",
        # pc.TypeLambdas() (type Stringer[-A] = A => String) Can also verify it form the issue title
        [
            pc.TypeProjections(),
            pc.HigherKindedTypes(),
            pc.Collections(),
            pc.Typedefs(),
            pc.FunctionTypes(),
            pc.Subtyping(),
            pc.DeclVariance(),
            pc.ParameterizedFunctions(),
            pc.TypeArgsInference(),
            pc.ParameterizedTypes()
        ],
        False,
        sy.Runtime(sy.ClassCastException()),
        rc.MissingCase(),
        ct.Declarations(),
        13
    ),
    ScalaBug(
        "6.Scala2-2038",
        # pc.Cast() (call cast method), no pc.FunctionAPI()
        [
            pc.Collections(),
            pc.WildCardType(), #TODO
            pc.Reflection(),
            pc.PatMat(),
            pc.TypeArgsInference(),
            pc.FunctionAPI(),
            pc.ParameterizedTypes()
        ],
        False,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.Approximation(),
        5
    ),
    ScalaBug(
        "7.Scala2-5378",
        #pc.Collections() (Nil object, List, Traversable), maybe introduce pc.StructuralTypes()(Scala only or Duck Typing in general)
        # https://alvinalexander.com/scala/how-to-use-duck-typing-in-scala-structural-types/
        [
            pc.ParameterizedClasses(),
            pc.FunctionAPI(),
            pc.DeclVariance(),
            pc.AnonymousClass(),
            pc.Overriding(),
            pc.VarTypeInference(),
            pc.ParameterizedFunctions(),
            pc.TypeArgsInference(),
            pc.BoundedPolymorphism(),
            pc.ParameterizedTypes()
        ],
        False,
        sy.Runtime(sy.MissingMethodException()),
        # agreed, maybe also consider rc.InsufficientAlgorithmImplementation()
        # Not enough to look for abstract types; have to recursively check
        # the bounds of each abstract type for more abstract types. It also makes 2 bug fixes.
        rc.IncorrectComputation(),
        # ct.TypeExpression() it is too type related to be considered a OtherSemanticChecking bug I think.
        ct.TypeExpression(), # OtherSemanticChecking
        12
    ),
    ScalaBug(
        "8.Scala2-5687",
        # pc.AccessModifiers() (private val t: T), pc.DependentTypes()
        [
            pc.ParameterizedClasses(),
            pc.BoundedPolymorphism(),
            pc.Typedefs(),
            pc.Cast(),
            pc.This(),
            pc.ParameterizedTypes(),
            pc.Inheritance(),
            pc.Overriding()
        ],
        False,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.ErrorReporting(),
        18
    ),
    ScalaBug(
        "9.Scala2-11252",
        # pc.ParameterizedTypes() (Option[Int] )
        [
            pc.PatMat(),
            pc.FunctionAPI(),
            pc.Overriding(),
            pc.Conditionals(),
            pc.AlgebraicDataTypes()
        ],
        True,
        sy.CompileTimeError(),
        rc.IncorrectCondition(),
        ct.Resolution(),
        13
    ),
    ScalaBug(
        "10.Scala2-8344",
        [
            pc.Overloading(),
            pc.Varargs()
        ],
        False,
        sy.Runtime(sy.WrongResult()),
        rc.DesignIssue(),
        ct.Resolution(),
        5
    ),
    ScalaBug(
        "11.Scala2-2509",
        # pc.DependentTypes()  implicit def f[T, U](t: T)(implicit x: X[T, U]): U = x.u
        [
            pc.ParameterizedClasses(),
            pc.ParameterizedTypes(),
            pc.ParameterizedFunctions(),
            pc.TypeArgsInference(),
            pc.DeclVariance(),
            pc.Inheritance(),
            pc.Overriding(),
            pc.Subtyping(),
            pc.Implicits(),
        ],
        True,
        sy.Runtime(sy.WrongResult()),
        rc.DesignIssue(),
        ct.Resolution(),
        28
    ),
    ScalaBug(
        "12.Scala2-4775",
        [
            pc.Overloading(),
            pc.ParameterizedFunctions(),
            pc.TypeArgsInference(),
            pc.Varargs(),
        ],
        True,
        sy.CompileTimeError(),
        rc.DesignIssue(),
        ct.Resolution(),
        29
    ),
    ScalaBug(
        "13.Scala2-8862",
        [
            pc.Implicits(),
            pc.Import(),
            pc.ParameterizedTypes(),
            pc.Inheritance(),
            pc.Overriding(),
            pc.ParameterizedClasses()
        ],
        True,
        sy.CompileTimeError(),
        rc.InsufficientAlgorithmImplementation(),
        # both fit, but I think Environment fits better (change in context.implicits)
        ct.Environment(), # Resolution
        25
    ),
    ScalaBug(
        "14.Scala2-9231",
        [
            pc.ParameterizedClasses(),
            pc.Implicits(),
            pc.ParameterizedTypes(),
            pc.ParameterizedFunctions(),
        ],
        False,
        sy.MisleadingReport(),
        # maybe root cause rc.WrongMethod()?
        rc.IncorrectCondition(),
        ct.Resolution(),
        9
    ),
    ScalaBug(
        "15.Dotty-7041",
        # pc.Conditionals(), pc.ArithmeticExpressions()
        [
            pc.Inline(),
            pc.CallByName(),
            pc.BoundedPolymorphism(),
            pc.ParameterizedFunctions(),
            pc.WildCardType(), # TODO
            pc.TypeArgsInference(),
            pc.TryCatch(),
            pc.FunctionAPI(),
            pc.Lambdas(),
            pc.ParameterizedTypes()
        ],
        True,
        sy.InternalCompilerError(),
        rc.IncorrectComputation(),
        ct.Approximation(),
        13
    ),
    ScalaBug(
        "16.Dotty-4754",
        [
            pc.Import(),
            pc.AccessModifiers(),
            pc.Singleton(), #TODO
            pc.Inline()
        ],
        True,
        sy.InternalCompilerError(),
        # maybe rc.MissingCase() because in previous examples with a missing codition it was considered a missing case
        rc.IncorrectCondition(),
        ct.Transformation(),
        13
    ),
    ScalaBug(
        "17.Scala2-4691",
        # pc.SealedClasses() (sealed trait Node), no FunctionApi() maybe pc.StandardLibrary() (for Some) or create some type characteristic like pc.Some() or pc.Option() in general
        # function api from java doesnt include Some, it is part of Scala standard Library
        [
            pc.Inheritance(),
            pc.PatMat(),
            pc.AlgebraicDataTypes(),
            pc.Overriding(),
            pc.FunctionAPI(),
            pc.ParameterizedTypes(),
        ],
        False,
        sy.Runtime(sy.CaseNotFound()), #TODO
        rc.DesignIssue(),
        ct.OtherSemanticChecking(),
        18
    ),
    ScalaBug(
        "18.Dotty-6451",
        [
            pc.TypeLambdas(),
            pc.Typedefs(),
            pc.HigherKindedTypes(),
            pc.Collections(),
            pc.ParameterizedTypes()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.TypeComparison(),
        2
    ),
    ScalaBug(
        "19.Scala2-9760",
        # pc.SealedClasses() (sealed trait Foo[F[_]])
        [
            pc.HigherKindedTypes(),
            pc.AlgebraicDataTypes(),
            pc.ParameterizedTypes(),
            pc.ParameterizedClasses(),
            pc.ParameterizedFunctions(),
            pc.TypeArgsInference(),
            pc.Inheritance(),
            pc.PatMat(),
            pc.Collections()
        ],
        True,
        sy.CompileTimeError(),
        rc.ExtraneousComputation(),
        ct.Inference(),
        18
    ),
    ScalaBug(
        "20.Scala2-10186",
        [
            pc.HigherKindedTypes(),
            pc.BoundedPolymorphism(),
            pc.ParameterizedTypes(),
            pc.ParameterizedFunctions(),
            pc.Typedefs()
        ],
        True,
        sy.CompileTimeError(),
        # pc.MissingCase() missed the case that prefix normalizes type aliases and kind-checking should not do this, so this fix is due to a missing case
        rc.IncorrectCondition(),
        ct.TypeComparison(),
        12
    )
]

scala_iter4 = [
    ScalaBug(
        "1.Dotty-5876",
        # pc.MultiBounds()
        [
            pc.Inheritance(),
            pc.Typedefs(),
            pc.ParameterizedTypes(),
            pc.BoundedPolymorphism(),
            pc.Overriding()
        ],
        True,
        sy.InternalCompilerError(),
        rc.IncorrectCondition(),
        ct.TypeComparison(),
        9
    ),
    ScalaBug(
        "2.Scala2-2742",
        # pc.VarTypeInference() val f = new A
        [
            pc.Implicits(),
            pc.Inheritance(),
            pc.Overriding(),
            pc.Subtyping()
        ],
        True,
        sy.CompileTimeError(),
        rc.DesignIssue(),
        ct.OtherSemanticChecking(),
        12
    ),
    ScalaBug(
        "3.Dotty-2192",
        [
            pc.ParameterizedTypes(),
            pc.PatMat(),
            pc.Subtyping()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Approximation(),
        5
    ),
    ScalaBug(
        "4.Scala2-9630",
        # pc.NestedDeclarations() ( nested case classes to the sealed trait)
        [
            pc.AlgebraicDataTypes(),
            pc.PatMat(),
        ],
        True,
        sy.CompileTimeError(),
        rc.InsufficientAlgorithmImplementation(),
        ct.TypeExpression(),
        12
    ),
    ScalaBug(
        "5.Dotty-6745",
        # pc.CallByName() prog: (h: self.type) => h.M
        [
            pc.DependentTypes(),
            pc.Typedefs(),
            pc.This(),
            pc.FunctionTypes(),
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.TypeExpression(),
        4
    ),
    ScalaBug(
        "6.Dotty-2219",
        [
            pc.ParameterizedClasses(),
            pc.ParameterizedTypes(),
            pc.BoundedPolymorphism(),
            pc.HigherKindedTypes(),
            pc.TypeLambdas(),
            pc.WildCardType(),
            pc.Typedefs()
        ],
        True,
        sy.CompileTimeError(),
        # rc.IncorrectDataType()
        # Previously we just returned the unapplied WildcardType
        #  which isincorrect if the WildcardType is bounded.
        rc.MissingCase(),
        #agreed, but consider also ct.TypeComparison()
        # do the type application on the bounds of the WildcardType
        # and wrap the result in a WildcardType.
        ct.Approximation(),
        0
    ),
    ScalaBug(
        "7.Scala2-6754",
        [
            pc.ParameterizedFunctions(),
            pc.BoundedPolymorphism(),
            pc.Reflection(),
            pc.PatMat()
        ],
        True,
        sy.InternalCompilerError(),
        # agreed, we add atPos(uncheckedPattern.pos)
        # consider also rc.WrongParams() because app is passed as argument to doTypedUnapply
        rc.MissingCase(),
        ct.TypeExpression(),
        0
    ),
    ScalaBug(
        "8.Scala2-7232",
        # maybe pc.Shadowing() characteristic?
        [
            pc.JavaInterop(),
        ],
        True,
        sy.Runtime(sy.ClassCastException()),
        rc.FunctionalSpecificationMismatch(),
        ct.Resolution(),
        0
    ),
    ScalaBug(
        # pc.regression bug
        "9.Scala2-7688",
        # pc.Singleton() object A
        [
            pc.ParameterizedClasses(),
            pc.BoundedPolymorphism(),
            pc.TypeProjections(),
            pc.Mixins(), # TODO
            pc.Reflection(),
            pc.ParameterizedTypes(),
            pc.DependentTypes()
        ],
        True,
        sy.CompileTimeError(),
        rc.IncorrectComputation(),
        ct.Approximation(),
        0
    ),
    ScalaBug(
        # regression bug
        "10.Scala2-9086",
        # pc.Singleton() object X
        [
            pc.ParameterizedClasses(),
            pc.ParameterizedTypes(),
            pc.Inheritance(),
            pc.TypeArgsInference(),
            pc.Implicits()
        ],
        True,
        sy.CompileTimeError(),
        rc.WrongParams(),
        # agreed with Resolution, maybe ct.Environment() fits better?
        # change at context.outer.owner.newLocalDummy() by passing argument context.owner.pos
        ct.Resolution(),
        0
    ),
    ScalaBug(
        "11.Dotty-8647",
        [
            pc.ParameterizedClasses(),
            pc.WildCardType(),
            pc.Typedefs(),
            pc.MatchTypes(), # TODO
            pc.PatMat(),
            pc.ParameterizedTypes()
        ],
        True,
        sy.CompileTimeError(),
        # rc.ExtraneousComputation()
        # the type of the bug is an extraneous condition
        # ( as stated on ExtraneousComputation documentation)
        rc.IncorrectCondition(),
        ct.TypeComparison(),
        0
    ),
    ScalaBug(
        # regression bug
        "12.Scala2-8531",
        [
            pc.Enums(),
            pc.PatMat(),
            pc.JavaInterop()
        ],
        True,
        sy.CompilationPerformance(),
        rc.InsufficientAlgorithmImplementation(),
        ct.OtherSemanticChecking(),
        0
    ),
    ScalaBug(
        "13.Scala2-6912",
        [
            pc.ParameterizedFunctions(),
            pc.Overloading(),
            pc.Nothing(),
            pc.ParameterizedTypes()
        ],
        False,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.ErrorReporting(),
        0
    ),
    ScalaBug(
        "14.Dotty-2104",
        # pc.Singleton() object Cons, pc.TypeArgsInference(), no pc.ParameterizedTypes()
        [
            pc.AlgebraicDataTypes(),
            pc.ParameterizedClasses(),
            pc.FunctionAPI(),
            pc.ParameterizedFunctions(),
            pc.ParameterizedTypes(),
            pc.DeclVariance(),
            pc.Overriding(),
            pc.PatMat()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Inference(),
        0
    ),
    ScalaBug(
        "15.Dotty-5640",
        # maybe pc.ParamTypeInference()
        [
            pc.Lambdas(),
            pc.VarTypeInference()
        ],
        False,
        sy.InternalCompilerError(),
        rc.IncorrectSequence(),
        ct.Transformation(),
        0
    ),
    ScalaBug(
        "16.Dotty-3067",
        # pc.Singleton() object Bar extends Foo
        [
            pc.ParameterizedClasses(),
            pc.ParamTypeInference(),
            pc.Lambdas(),
            pc.ETAExpansion(), #TODO
            pc.Collections(),
            pc.ParameterizedTypes(),
            pc.FunctionTypes(),
            pc.Implicits(),
            pc.Inheritance()
        ],
        True,
        sy.CompileTimeError(),
        rc.InsufficientAlgorithmImplementation(),
        ct.Resolution(),
        0
    ),
    ScalaBug(
        # regression bug
        "17.Scala2-7636",
        [
            pc.ParameterizedClasses(),
            pc.WildCardType(),
            pc.ParameterizedTypes(),
            pc.Inheritance(),
            pc.Collections()
        ],
        False,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.ErrorReporting(),
        0
    ),
    ScalaBug(
        "18.Scala2-9110",
        # pc.Singleton() object DomainC extends Domain
        [
            pc.NestedClasses(),
            pc.AlgebraicDataTypes(),
            pc.PatMat()
        ],
        True,
        sy.Runtime(sy.WrongResult()),
        rc.MissingCase(),
        ct.TypeExpression(),
        0
    ),
    ScalaBug(
        "19.Scala2-10545",
        [
            pc.HigherKindedTypes(),
            pc.ParameterizedClasses(),
            pc.ParameterizedTypes(),
            pc.ParameterizedFunctions(),
            pc.FunctionAPI(),
            pc.Implicits()
        ],
        True,
        sy.CompileTimeError(),
        # maybe rc.FunctionalSpecificationMismatch because it says:
        # The spec and intuitions suggest that c1 is more specific than the quantified c0
        # and that the former should be selected over the latter
        rc.MissingCase(),
        ct.TypeComparison(),
        0
    ),
    ScalaBug(
        "20.Scala2-9398",
        # pc.SealedClasses() sealed abstract class TB, pc.Singleton() case object B extends TB
        [
            pc.AlgebraicDataTypes(),
            pc.PatMat()
        ],
        False,
        sy.Runtime(sy.CaseNotFound()),
        rc.InsufficientAlgorithmImplementation(),
        ct.OtherSemanticChecking(),
        0
    ),
]
