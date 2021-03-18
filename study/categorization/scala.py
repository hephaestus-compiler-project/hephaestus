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
                # Dataclasses are kotlin only maybe introduce value classes because that is a value class only bug, we see in comments if we remove extend anyval it works, maybe create new category
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
    # pc.Reflection(), pc.This(), no Lamda , also pc.ParameterizedTypes(), maybe pc.ExistentialTypes() becasue this.getClass is resolved as an existential type 
        [
            pc.ParameterizedFunctions(),
            pc.Lambdas(),
            pc.CallByName(),
        ],
        True,
        sy.CompileTimeError(),
        rc.ExtraneousComputation(),
        # maybe ct.TypeExpression remove a check, also has to do with  an expression f1(this.getClass)
        ct.Resolution(),
        # 9
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
        # 16
        13
    ),
    ScalaBug(
        "9.Dotty-1757",
        # pc.VarTypeInference()
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
           # it is bound related but Is the fix really related to type comparsion? maybe consider inference
        ct.TypeComparison(),
        9
    ),
    ScalaBug(
        "11.Scala2-9542",
        # pc.DependentTypes(), because I think type Mutation[C] is dependent, pc.Typedefs()
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
        # pc.Typefefs()
        [
            pc.ParameterizedClasses(),
            pc.ParameterizedTypes(),
            pc.Overloading()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Approximation(),
        #4
        3
    ),
    ScalaBug(
        "13.Scala-9361",
        #  pc.Typedefs(), pc.TypeArgsInference() It appears that in the absence of a type parameter to the new Foo instantiation,
#       #the type inferencer looks to the expected type of foo to try to infer it.
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
      # agree with Expression, maybe consider ct.Approximation because `pretypeArgs` allows arguments of overloaded methods to be typed with a
# more precise expected type 
        ct.TypeExpression(),
        # 10
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
        # maybe rc.Approximation() of gadt type 
        # ApproximateGadtAccumulator   /** Approximates a type to get rid of as many GADT-constrained abstract types as possible. */
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
        ct.Mechanics(),  # transformation / desugaring
        #7
        6
    ),
    ScalaBug(
        "18.Dotty-8752",
        # pc.Collection()
        [
            pc.TypeLambdas(), pc.ParameterizedClasses(),
            pc.FBounded(), pc.ParameterizedTypes()
        ],
        False,
        sy.MisleadingReport(),
        rc.MissingCase(),
        ct.OtherSemanticChecking(),
        # 3
        2
    ),
    ScalaBug(
        "19.Scala2-10185",
        #  pc.TypeArgsInference() HK Types require an instantiation of a type contructor, and we pass no arguments
        [
            pc.ParameterizedTypes(), pc.ParameterizedClasses(),
            pc.BoundedPolymorphism(), pc.HigherKindedTypes(),
            pc.AlgebraicDataTypes(), pc.PatMat()
        ],
        True,
        sy.CompileTimeError(),
        # rc.AlgorithmImproperlyImplemented() fix many issues  change the algorithm implementation first message of TomasMikula at https://github.com/scala/scala/pull/6069 
        rc.IncorrectComputation(),
        ct.TypeComparison(),
        # 10
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
        # CT.OtherSemanticChecking() i dont think we have a declaration check, we semantic check the args at def call
        # the problem is that the varargs 1, 2, 3 are known values, but their translation SeqLiteral(1, 2, 3) is not.
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
        ct.Mechanics(),  # error reporting
        4
    ),
    ScalaBug(
        "2.Scala2-5231",
        [
            pc.AccessModifiers(), pc.ImplicitDefs()
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
            pc.ParameterizedTypes()
        ],
        False,
        sy.MisleadingReport(),
        rc.DesignIssue(),
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
        [
            pc.JavaInterop(), pc.Arrays(),
            pc.Varargs()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Approximation(),
        10
    ),
    ScalaBug(
        "8.Dotty-4487",
        [
            pc.Inheritance(), pc.FunctionTypes()
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
            pc.ImplicitDefs(),
            pc.ImplicitParameters()
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
            pc.NestedDeclaration(),
            pc.Inheritance(),
            pc.ImplicitParameters(),
            pc.ExistentialTypes(),
            pc.PatMat()
        ],
        True,
        sy.CompileTimeError(),
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
            pc.ImplicitDefs(), pc.ImplicitParameters(),
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
            pc.Overriding(), pc.ImplicitDefs(),
            pc.ImplicitParameters(), pc.ArithmeticExpressions()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Mechanics(),  # transformation
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
        ct.Mechanics(),  # transformation
        8
    ),
    ScalaBug(
        "16.Dotty-2723",
        [
            pc.Inline(), pc.ImplicitParameters(), pc.FunctionTypes()
        ],
        True,
        sy.InternalCompilerError(),
        rc.IncorrectDataType(),
        ct.Mechanics(),  # Transformation
        3
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
        ct.TypeExpression(),
        11
    ),
    ScalaBug(
        "18.Scala2-10536",
        [
            pc.OperatorOverloading(),
            pc.ParameterizedClasses(), pc.ImplicitParameters(),
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
            pc.HigherKindedTypes(), pc.NestedDeclaration(),
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
        [
            pc.ParameterizedClasses(),
            pc.DeclVariance(),
            pc.ImplicitDefs(),
            pc.ParameterizedTypes(),
            pc.ImplicitParameters()
        ],
        True,
        sy.CompileTimeError(),
        rc.InsufficientAlgorithmImplementation(),
        ct.Inference(),
        19
    ),
    ScalaBug(
        "2.Scala2-5399",
        [
            pc.ExistentialTypes(),
            pc.ParameterizedClasses(),
            pc.ParameterizedTypes(),
            pc.Inheritance(),
            pc.PatMat()
        ],
        True,
        sy.CompileTimeError(),
        rc.WrongDataReference(),
        ct.TypeExpression(),
        19
    ),
    ScalaBug(
        "3.Dotty-7597",
        [
            pc.ParameterizedFunctions(),
            pc.BoundedPolymorphism(),
            pc.TypeArgsInference(),
            pc.AnonymousClass()
        ],
        False,
        sy.Runtime(),
        rc.IncorrectComputation(),
        ct.Resolution(),
        2
    ),
    ScalaBug(
        "4.Scala2-5958",
        [
            pc.DependentTypes(),
            pc.NestedDeclaration()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Mechanics(),  # Environment (build)
        12
    ),
    ScalaBug(
        "5.Scala2-7872",
        [
            pc.TypeLambdas(),
            pc.DeclVariance(),
            pc.ParameterizedFunctions(),
            pc.TypeArgsInference(),
            pc.ParameterizedTypes()
        ],
        False,
        sy.Runtime(sy.AmbiguousMethodError()),
        rc.MissingCase(),
        ct.Approximation(),
        13
    ),
    ScalaBug(
        "6.Scala2-2038",
        [
            pc.Collections(),
            pc.Reflection(),
            pc.PatMat(),
            pc.Cast(),
            pc.DependentTypes(),
            pc.TypeArgsInference(),
            pc.ParameterizedTypes()
            # Some?
        ],
        False,
        sy.InternalCompilerError(),
        rc.WrongParams(),
        ct.Approximation(),
        5
    ),
    ScalaBug(
        "7.Scala2-5378",
        [
            pc.ParameterizedClasses(),
            pc.DeclVariance(),
            pc.AnonymousClass(),
            pc.VarTypeInference(),
            pc.ParameterizedFunctions(),
            pc.TypeArgsInference(),
            pc.BoundedPolymorphism(),
            pc.ParameterizedTypes()
        ],
        False,
        sy.InternalCompilerError(),
        rc.IncorrectComputation(),
        ct.Approximation(),
        12
    ),
    ScalaBug(
        "8.Scala2-5687",
        [
            pc.ParameterizedClasses(),
            pc.BoundedPolymorphism(),
            pc.Typedefs(),
            pc.ParameterizedTypes(),
            pc.Inheritance()
        ],
        False,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.Mechanics(),
        18
    ),
    ScalaBug(
        "9.Scala2-11252",
        [
            pc.PatMat(),
            pc.Overriding(),
            pc.Conditionals(),
            pc.AlgebraicDataTypes()
            # Option?
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
        sy,
        rc.DesignIssue(),
        ct.Resolution(),
        5
    ),
    ScalaBug(
        "11.Scala2-2509",
        [
            pc.ParameterizedClasses(),
            pc.DeclVariance(),
            pc.Inheritance(),
            pc.AnonymousClass(),
            pc.ImplicitDefs(),
            pc.ImplicitParameters()
        ],
        True,
        sy.WrongResult(),
        rc.DesignIssue(),
        ct.Inference(),
        28
    ),
    ScalaBug(
        "12.Scala2-4775",
        [
            pc.JavaInterop(),
            pc.StaticMethod(),
            pc.Overloading(),
            pc.ParameterizedFunctions(),
            pc.TypeArgsInference(),
            pc.Varargs(),
            pc.UseVariance()
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
            pc.ImplicitDefs(),
            pc.ParameterizedTypes(),
            pc.Inheritance(),
            pc.Overriding(),
            pc.ParameterizedClasses()
        ],
        True,
        sy.CompileTimeError(),
        rc.InsufficientAlgorithmImplementation(),
        ct.Environment(),
        25
    ),
    ScalaBug(
        "14.Scala2-9231",
        [
            pc.ParameterizedClasses(),
            pc.ImplicitDefs(),
            pc.ParameterizedTypes(),
            pc.ParameterizedFunctions(),
            pc.TypeArgsInference(),
            pc.ImplicitParameters()
        ],
        False,
        sy.MisleadingReport(),
        rc.IncorrectCondition(),
        ct.Declarations(),
        9
    ),
    ScalaBug(
        "15.Dotty-7041",
        [
            pc.Inline(),
            pc.TryCatch(),
            pc.PatMat(),
            pc.ParameterizedTypes()
        ],
        True,
        sy.InternalCompilerError(),
        rc.WrongDataReference(),
        ct.Mechanics(),
        13
    ),
    ScalaBug(
        "16.Dotty-4754",
        [
            pc.Import(),
            pc.Inline()
        ],
        True,
        sy.InternalCompilerError(),
        rc.IncorrectCondition(),
        ct.Mechanics(),
        13
    ),
    ScalaBug(
        "17.Scala2-4691",
        [
            pc.Inheritance(),
            pc.PatMat(),
            pc.ParameterizedTypes(),
            pc.SealedClasses()
        ],
        False,
        sy.Runtime(sy.AmbiguousMethodError()),
        rc.IncorrectComputation(),
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
            pc.TypeArgsInference(),
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
        [
            pc.SealedClasses(),
            pc.HigherKindedTypes(),
            pc.AlgebraicDataTypes(),
            pc.ParameterizedTypes(),
            pc.ParameterizedClasses(),
            pc.ParameterizedFunctions(),
            pc.Inheritance(),
            pc.PatMat(),
            pc.Collections()
        ],
        True,
        sy.CompileTimeError(),
        rc.IncorrectCondition(),
        ct.Approximation(),
        18
    ),
    ScalaBug(
        "20.Scala2-10186",
        [
            pc.HigherKindedTypes(),
            pc.BoundedPolymorphism(),
            pc.ParameterizedTypes(),
            pc.ParameterizedFunctions(),
            pc.TypeArgsInference()
        ],
        True,
        sy.CompileTimeError(),
        rc.WrongParams(),
        ct.Mechanics(),
        12
    )
]
