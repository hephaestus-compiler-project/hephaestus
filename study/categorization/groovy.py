from bug import GroovyBug
import categories as ct
import characteristics as pc
import symptoms as sy
import root_causes as rc



groovy_iter1 = [
    GroovyBug(
        "1.GROOVY-8609",
        [pc.ParameterizedClasses(),
         pc.ParameterizedTypes(),
         pc.BoundedPolymorphism(),
         pc.Collections()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Inference(),
        5
    ),
    GroovyBug(
        "2.GROOVY-7364",
        [pc.ParameterizedClasses(),
         pc.VarTypeInference(),
         pc.NamedArgs()
         ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Resolution(),
        9
        ),
    GroovyBug(
        "3.GROOVY-5217",
        [pc.Lambdas(), pc.FunctionTypes(), pc.Property()],
        True,
        sy.CompileTimeError(),
        rc.IncorrectSequence(),
        ct.Resolution(),
        7
    ),
    GroovyBug(
        "4.GROOVY-7211",
        [pc.ParameterizedClasses(),
         pc.ParameterizedTypes(),
         pc.NamedArgs()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Inference(),
        13
    ),
    GroovyBug(
        "5.GROOVY-9420",
        [pc.Collections(),
         pc.ParameterizedTypes(),
         pc.VarTypeInference(),
         pc.Subtyping()],
        True,
        sy.CompileTimeError(),
        rc.IncorrectDataType(),
        ct.TypeExpression(),
        14
    ),
    GroovyBug(
        "6.GROOVY-5232",
        [pc.Property(), pc.VarTypeInference()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Resolution(),
        9
    ),
    GroovyBug(
        "7.GROOVY-8330",
        [pc.Subtyping(), pc.Inheritance(), pc.Cast()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.TypeComparison(),
        7
    ),
    GroovyBug(
        "8.GROOVY-7721",
        [pc.Arrays(), pc.Subtyping(), pc.Overriding(), pc.JavaInterop()],
        True,
        sy.CompileTimeError(),
        rc.FunctionalSpecificationMismatch(),
        ct.Resolution(),
        13
    ),
    GroovyBug(
        "9.GROOVY-6021",
        [pc.Lambdas(),
         pc.Collections(),
         pc.DelegationAPI(),
         pc.VarTypeInference()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Transformation(), # TODO backend
        12
    ),
    GroovyBug(
        "10.GROOVY-8247",
        [pc.Lambdas(),
         pc.ParamTypeInference(),
         pc.FunctionTypes(),
         pc.SAM()],
        True,
        sy.InternalCompilerError(),
        rc.WrongDataReference(),
        ct.Inference(),
        9
    ),
    GroovyBug(
        "11.GROOVY-7333",
        [pc.FlowTyping(),
         pc.PrimitiveTypes(),
         pc.Arrays(), pc.Subtyping()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Approximation(),
        7

    ),
    GroovyBug(
        "12.GROOVY-7987",
        [pc.StaticMethod()],
        False,
        sy.Runtime(sy.ClassCastException()),
        rc.MissingCase(),
        ct.OtherSemanticChecking(),
        7
    ),
     GroovyBug(
        "13.GROOVY-8445",
        [pc.Lambdas(), pc.ParamTypeInference(), pc.Streams()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Approximation(),
        11
    ),
    GroovyBug(
        "14.GROOVY-7316",
        [pc.ParameterizedFunctions(),
         pc.TypeArgsInference(),
         pc.Collections()],
        True,
        sy.CompileTimeError(),
        rc.FunctionalSpecificationMismatch(),
        ct.TypeExpression(),
        2
    ),
    GroovyBug(
        "15.GROOVY-7420",
        [pc.PrimitiveTypes(), pc.Overloading()],
        True,
        sy.CompileTimeError(),
        rc.FunctionalSpecificationMismatch(),
        ct.Resolution(),
        10
    ),
 GroovyBug(
        "16.GROOVY-7315",
        [pc.NamedArgs(), pc.NestedClasses(), pc.PrimitiveTypes()],
        True,
        sy.CompileTimeError(),
        rc.InsufficientAlgorithmImplementation(),
        ct.OtherSemanticChecking(),
        9
    ),
    GroovyBug(
        "17.GROOVY-6030",
        [pc.Collections(), pc.Overriding(), pc.Overloading(),
         pc.Subtyping(), pc.Lambdas()],
        True,
        sy.CompileTimeError(),
        rc.IncorrectSequence(),
        ct.Resolution(),
        4
    ),
    GroovyBug(
        "18.GROOVY-7711",
        [pc.Overriding(), pc.Varargs(), pc.Subtyping(), pc.Inheritance()],
        True,
        sy.CompileTimeError(),
        rc.IncorrectComputation(),
        ct.Resolution(),
        13
    ),
    GroovyBug(
        "19.GROOVY-6119",
        [pc.Collections(), pc.NamedArgs()],
        True,
        sy.CompileTimeError(),
        rc.InsufficientAlgorithmImplementation(),
        ct.Transformation(),
        8
    ),
    GroovyBug(
        "20.GROOVY-8310",
        [pc.ParameterizedTypes(),
         pc.ParameterizedFunctions(),
         pc.TypeArgsInference(),
         pc.Collections(),
         pc.Lambdas(),
         pc.Subtyping()],
        False,
        sy.Runtime(),
        rc.IncorrectCondition(),
        ct.TypeExpression(),
        10
    )
]




groovy_iter2 = [
    GroovyBug(
        "1.GROOVY-6489",
        [pc.ParameterizedTypes, pc.JavaInterop(),
         pc.WithMultipleAssignment()
         pc.Property(), pc.AccessModifiers()
        ],
        True,
        sy.InternalCompilerError(),
        rc.WrongParams(),
        ct.TypeExpression(),
        17
    ),
    GroovyBug(
        "2.GROOVY-8686",
        [pc.FlowTyping(), pc.VarTypeInference()],
        False,
        sy.Runtime(sy.AbstractMethodError()),
        rc.MissingCase(),
        ct.Environment(),
        4
    ),
    GroovyBug(
        "3.GROOVY-6415",
        [pc.ParameterizedFunctions(), pc.TypeArgsInference()],
        True,
        sy.CompileTimeError(),
        rc.IncorrectComputation(),
        ct.Environment(),  # TypeExpression
        12
    ),
    GroovyBug(
        "4.GROOVY-8590",
        [pc.PrimitiveTypes(), pc.Cast(), pc.Subtyping()],
        True,
        sy.CompileTimeError(),
        rc.IncorrectCondition(),
        ct.TypeExpression(),
        7
    ),
    GroovyBug(
        "5.GROOVY-6761",
        [pc.ParameterizedFunctions(),
         pc.TypeArgsInference(),
         pc.ParameterizedTypes(),
         pc.UseVariance()
         ],
        True,
        sy.CompileTimeError(),
        rc.IncorrectComputation(),
        ct.Resolution(),
        8
    ),
    GroovyBug(
        "6.GROOVY-6034",
        [pc.PrimitiveTypes()],
        False,  # At the time was false
        sy.Runtime(sy.VerifyError()),
        rc.DesignIssue(),
        ct.TypeExpression(),
        5
    ),
    GroovyBug(
        "7.GROOVY-6195",
        [pc.Collections(), pc.VarTypeInference()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Resolution(),
        7
    ),
    GroovyBug(
        "8.GROOVY-5873",
        [pc.Inheritance(), pc.ParameterizedClasses(),
         pc.ParameterizedTypes(), pc.Property()
         ],
        True,
        sy.CompileTimeError(),
        rc.InsufficientAlgorithmImplementation(),
        ct.Inference(),
        10
    ),
    GroovyBug(
        "9.GROOVY-5415",
        # pc.This()
        [pc.JavaInterop(),
         pc.ParameterizedClasses(),
         pc.ParameterizedTypes(),
         pc.ParameterizedFunctions(),
         pc.TypeArgsInference(),
         pc.Reflection()
         ],
        True,
        sy.CompileTimeError(),
        rc.ExtraneousComputation(),
        ct.TypeComparison(),
        11
    ),
    GroovyBug(
        "10.GROOVY-9328",
        [pc.AccessModifiers(), pc.AnonymousClass(),
         pc.Overriding()],
        True,
        sy.CompileTimeError(),
        rc.IncorrectCondition(),
        ct.Environment(),
        14
    ),
    GroovyBug(
        "11.GROOVY-5175",
        [pc.Arrays(),
         pc.Subtyping()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Approximation(),
        7
    ),
    GroovyBug(
        # regression bug
        "12.GROOVY-7922",
        [pc.Overloading(), pc.MultipleImplements()],
        False,
        sy.Runtime(sy.AmbiguousMethodError()),
        rc.IncorrectComputation(),
        ct.Resolution(),
        9
    ),
    GroovyBug(
        "13.GROOVY-6129",
        [pc.Collections(),
         pc.ParameterizedTypes(),
         pc.TypeArgsInference()],
        True,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.Inference(),
        2
    ),
    GroovyBug(
        "14.GROOVY-8090",
        [pc.Collections(),
         pc.ParameterizedTypes(),
         pc.ParameterizedFunctions()
         pc.TypeArgsInference(),
         ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Inference(),
        7
    ),
    GroovyBug(
        "15.GROOVY-5742",
        [pc.Import(), pc.ParameterizedClasses(),
         pc.FBounded(), pc.ParameterizedFunctions(),
         pc.TypeArgsInference(),
         pc.ParameterizedTypes(), pc.Inheritance()
         ],
        True,
        sy.InternalCompilerError(),
        rc.IncorrectComputation(),
        ct.Inference(),
        12
    ),
    GroovyBug(
        "16.GROOVY-7307",
        [pc.Subtyping(),
         pc.ParameterizedFunctions(), pc.BoundedPolymorphism(),
         pc.TypeArgsInference()
         ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.TypeComparison(),
        11
    ),
    GroovyBug(
        "17.GROOVY-7618",
        [
         pc.Lambdas(),
         pc.ParamTypeInference(),
         pc.SAM()],
        True,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.Approximation(),
        10
    ),
    GroovyBug(
        "18.GROOVY-5580",
        [pc.Inheritance(), pc.Property()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Resolution(),
        14
    ),
    GroovyBug(
        "19.GROOVY-7061",
        [pc.Collections(), pc.ParamTypeInference(),
         pc.Lambdas()],
        True,
        sy.CompileTimeError(),
        rc.IncorrectComputation(),
        ct.Inference(),
        5
    ),
    GroovyBug(
        "20.GROOVY-5240",
        [pc.Reflection()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.TypeExpression(),
        7
    )
]

groovy_iter3 = [
    GroovyBug(
        "1.GROOVY-5411",
        # pc.StaticMethod() (static context)
        [
            #  pc.StandardFeatures()
        ],
        False,
        sy.Runtime(sy.MissingMethodException()),
        rc.MissingCase(),
        ct.OtherSemanticChecking(),
        8
    ),
    GroovyBug(
        "2.GROOVY-8961",
        [pc.Collections(), pc.ParameterizedTypes(), pc.Property()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Inference(),
        6
    ),
    GroovyBug(
        "3.GROOVY-6787",
        [pc.ParameterizedFunctions(),
         pc.TypeArgsInference(),
         pc.BoundedPolymorphism(),
         pc.ParameterizedTypes(),
         pc.Collections()],
        True,
        sy.Runtime(sy.ClassCastException()),
        rc.IncorrectComputation(),
        ct.Inference(),
        11
    ),
    GroovyBug(
        "4.GROOVY-7327",
        # no pc.ParameterizedTypes(), pc.Varargs() (Arrays.asList(sequence)[0..1])
        [pc.JavaInterop(),
         pc.ParameterizedFunctions(),
         pc.Collections(),
         pc.TypeArgsInference(),
         pc.ParameterizedTypes(),
         pc.Arrays(),
         pc.Enums()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.TypeComparison(),
        6
    ),
    GroovyBug(
        "5.GROOVY-5332",
        [pc.Collections(), pc.ParameterizedTypes()],
        True,
        sy.CompileTimeError(),
        # pc.IncorrectComputation() fix body of parameterizeArguments method, could be missing case, but I consider it more algorithmic than logic fix.
        rc.MissingCase(), # IncorrectComputation
        ct.Inference(),
        2
    ),
    GroovyBug(
        "6.GROOVY-9327",
        [
            pc.AnonymousClass(),
            pc.Overriding()
        ],
        False,
        sy.Runtime(sy.MissingMethodException()),
        rc.MissingCase(),
        ct.Environment(),
        9
    ),
    GroovyBug(
        "7.GROOVY-6742",
        [
            pc.ParameterizedFunctions(),
            pc.AnonymousClass(),
            pc.ParameterizedTypes(),
            pc.FunctionAPI(),
            pc.TypeArgsInference(),
            pc.Overriding()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        # ct.Resolution Groovy is unable to resolve this Generics use case, change in ResolveVisitor, we find the enclosing method
        # if (innerClassNode.isAnonymous()) {
        # MethodNode enclosingMethod = innerClassNode.getEnclosingMethod();
        # if (null != enclosingMethod) {
        #     resolveGenericsHeader(enclosingMethod.getGenericsTypes());
        ct.Environment(),
        8
    ),
    GroovyBug(
        "8.GROOVY-6504",
        [
            pc.Lambdas(),
            pc.PrimitiveTypes(),
            pc.Collections(),
            pc.TypeArgsInference(),
        ],
        True,
        sy.CompileTimeError(),
        # pc.InsufficientAlgorithmImplementation()
        # algorithmic error not a simple missing case, we can see many methods like fullyResolve or typeCheckMethodArgumentWithGenerics or typeCheckMethodsWithGenerics removed and re-implemented
        #  The fix above refines the implementation of the algorithm related to selecting the correct "inject" method so I think it is pc.InsufficientAlgorithmImplementation()
        rc.MissingCase(),
        # found it difficult, both fit I would say TypeExpression because mostly the fix is related more with the type check of expression than with the process of inferring a type variable.
        #
        ct.Inference(), # TypeExpression
        1
    ),
    GroovyBug(
        "9.GROOVY-9518",
        # pc.pc.TypeArgsInference()  {foo, bar -> println(bar.size())}) for argument Consumer<String, ? super List<Integer>> bar

        [
            pc.JavaInterop(),
            pc.FunctionAPI(),
            pc.ParameterizedTypes(),
            pc.ParamTypeInference(),
            pc.Collections(),
            pc.Lambdas(),
            pc.UseVariance()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.TypeExpression(),
        28
    ),
    GroovyBug(
        "10.GROOVY-5172",
        # pc.ParamTypeInference() { ->printHtmlPart(2) }
        [
            pc.JavaInterop(),
            pc.Inheritance(),
            pc.PrimitiveTypes(),
            pc.ParameterizedTypes(),
            pc.Lambdas(),
            pc.TypeArgsInference(),
            pc.WildCardType() # TODO
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Approximation(),
        11
    ),
    GroovyBug(
        "11.GROOVY-5141",
        #pc.ParamTypeInference()(same as GROOVY-5141 ) maybe create a characterisitc it (implicit variable that is provided in closures.)
        [
            pc.Collections(),
            pc.Lambdas(),
            pc.TypeArgsInference()
        ],
        True,
        sy.CompileTimeError(),
        rc.IncorrectComputation(),
        ct.Resolution(),
        1
    ),
    GroovyBug(
        "12.GROOVY-5601",
        # pc.SAM()(Mapper<F, T>), no pc.Overriding()
        [
            pc.AnonymousClass(),
            pc.ParameterizedClasses(),
            pc.ParameterizedTypes(),
            pc.TypeArgsInference(),
            pc.Overriding()
        ],
        False,
        sy.InternalCompilerError(),
        # rc.MissingCase() we add a check to report an error message
        rc.DesignIssue(),
        # I think it fits in 2 categories.
        # ct.Declaration() because we have a Semantic check of a class declaration, if it is using generics, is inner and is anonymous create an error message.
        # maybe it could also be ct.ErrorReporting()? we add a check to add an errormessage
        # ct.Declaration() fits better
        ct.OtherSemanticChecking(),
        18
    ),
    GroovyBug(
        "13.GROOVY-6757",
        [
            pc.Collections(),
            pc.ParameterizedTypes()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Inference(),
        6
    ),
    GroovyBug(
        "14.GROOVY-8629",
        # no pc.ParameterizedClasses(), pc.This(), pc.Property() (in fix we see pushEnclosingPropertyExpression),
        [
            pc.Collections(),
            pc.ParameterizedTypes(),
            pc.NestedClasses(),
            pc.ParameterizedClasses(),
            pc.Subtyping(),
            pc.Overriding()
        ],
        True,
        sy.CompileTimeError(),
        rc.IncorrectComputation(),
        ct.Environment(),
        54
    ),
    GroovyBug(
        "15.GROOVY-5456",
        # pc.PrimitiveTypes(), pc.ParamTypeInference() (only it/2 statement without closure parameters) ({ [closureParameters -> ] statements })
        [
            pc.ArithmeticExpressions(),
            pc.Lambdas(),
        ],
        False,
        sy.InternalCompilerError(),
        rc.IncorrectCondition(),
        ct.TypeExpression(),
        5
    ),
    GroovyBug(
        "16.GROOVY-8157",
        [
            pc.Inheritance(),
            pc.Subtyping(),
            pc.FlowTyping()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        # the fix fits also ct.TypeComparsion()  if (accessedVariable instanceof Parameter) (((Parameter) accessedVariable) casting)
        # it also fits Environment because putNodeMetaData changes context
        ct.Environment(),
        13
    ),
    GroovyBug(
        "17.GROOVY-5145",
        [
            pc.Collections(),
            pc.TypeArgsInference(),
            pc.ParamTypeInference(),
            pc.Lambdas()
        ],
        True,
        sy.CompileTimeError(),
        rc.IncorrectComputation(),
        ct.Inference(),
        1
    ),
    GroovyBug(
        "18.GROOVY-6671",
        [
            pc.ParameterizedClasses(),
            pc.ParameterizedTypes(),
            pc.ParamTypeInference(),
            pc.ParameterizedFunctions(),
            pc.UseVariance(),
            pc.TypeArgsInference(),
            pc.Lambdas(),
            pc.SAM()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Inference(),
        25
    ),
    GroovyBug(
        "19.GROOVY-8319",
        [
            pc.Arrays(),
            pc.VarTypeInference()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Environment(),
        4
    ),
    GroovyBug(
        "20.GROOVY-7880",
        # pc.This()
        [
            pc.ParameterizedClasses(),
            pc.ParameterizedTypes(),
            pc.TypeArgsInference()
        ],
        True,
        sy.InternalCompilerError(),
        rc.WrongDataReference(),
        ct.Inference(),
        27
    )
]

groovy_iter4 = [
    GroovyBug(
        "1.GROOVY-5705",
        [
            pc.ParamTypeInference(),
            pc.Lambdas()
        ],
        True,
        sy.InternalCompilerError(),
        rc.WrongDataReference(),
        ct.TypeExpression(),
        9
    ),
    GroovyBug(
        "2.GROOVY-6760",
        [
            pc.Collections(),
            pc.ParameterizedFunctions(),
            pc.ParamTypeInference(),
            pc.TypeArgsInference(),
            pc.ParameterizedTypes(),
            pc.Lambdas()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Inference(),
        12
    ),
    GroovyBug(
        "3.GROOVY-5559",
        [
            pc.Collections(),
            pc.ParameterizedTypes(),
            pc.GString() # TODO
        ],
        False,
        sy.MisleadingReport(),
        rc.MissingCase(),
        ct.TypeComparison(),
        4
    ),
    GroovyBug(
        "4.GROOVY-6350",
        [
            pc.Arrays(),
            pc.ArithmeticExpressions()
        ],
        True,
        sy.InternalCompilerError(),
        rc.WrongDataReference(),
        ct.Inference(),
        1
    ),
    GroovyBug(
        "5.GROOVY-5237",
        [
            pc.ParameterizedClasses(),
            pc.AccessModifiers()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.TypeComparison(),
        5
    ),
    GroovyBug(
        "6.GROOVY-5640",
        [
            pc.Loops(),
            pc.Overriding(),
            pc.Collections(),
            pc.ParameterizedTypes()
        ],
        True,
        sy.CompileTimeError(),
        rc.InsufficientAlgorithmImplementation(),
        ct.Inference(),
        24
    ),
    GroovyBug(
        "7.GROOVY-6590",
        [
            pc.PrimitiveTypes(),
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Approximation(),
        1
    ),
    GroovyBug(
        "8.GROOVY-5650",
        [
            pc.ParameterizedTypes(),
            pc.ParameterizedClasses(),
            pc.JavaInterop(),
            pc.Inheritance(),
            pc.ParameterizedFunctions(),
            pc.Collections(),
            pc.UseVariance(),
            pc.Subtyping(),
            pc.TypeArgsInference(),
            pc.StaticMethod()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Inference(),
        33
    ),
    GroovyBug(
        "9.GROOVY-8523",
        [
            pc.FlowTyping(),
            pc.SAM(),
            pc.Subtyping()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.TypeExpression(),
        10
    ),
    GroovyBug(
        "10.GROOVY-9881",
        [
            pc.ParameterizedTypes(),
            pc.Lambdas(),
            pc.FunctionalInterface(),
            pc.ParameterizedClasses(),
            pc.ParamTypeInference(),
            pc.TypeArgsInference(),
            pc.SAM(),
            pc.ParameterizedFunctions(),
            pc.UseVariance(),
            pc.Overloading()
        ],
        True,
        sy.CompileTimeError(),
        rc.IncorrectComputation(),
        ct.Resolution(),
        26
    ),
    GroovyBug(
        "11.GROOVY-9903",
        [
            pc.DelegationAPI(),
            pc.Lambdas()
        ],
        False,
        sy.MisleadingReport(),
        rc.WrongParams(),
        ct.ErrorReporting(),
        7
    ),
    GroovyBug(
        "12.GROOVY-6961",
        [
            pc.TypeArgsInference(),
            pc.ParamTypeInference(),
            pc.Collections(),
            pc.Lambdas(),
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Inference(),
        12
    ),
    GroovyBug(
        "13.GROOVY-5229",
        [
            pc.StandardLibrary(),
            pc.PropertyReference()
        ],
        True,
        sy.CompileTimeError(),
        rc.IncorrectComputation(),
        ct.Resolution(),
        3
    ),
    GroovyBug(
        "14.GROOVY-5735",
        [
            pc.Reflection(),
            pc.ParameterizedFunctions(),
            pc.TypeArgsInference(),
            pc.Collections(),
            pc.ParameterizedTypes()
        ],
        True,
        sy.CompileTimeError(),
        rc.IncorrectComputation(),
        ct.Inference(),
        8
    ),
    GroovyBug(
        "15.GROOVY-9885",
        [
            pc.ElvisOperator(),
            pc.GString(), # TODO
            pc.Property()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.TypeExpression(),
        11
    ),
    GroovyBug(
        "16.GROOVY-5530",
        [
            pc.Lambdas(),
            pc.Collections(),
            pc.ParameterizedTypes(),
            pc.TypeArgsInference(),
            pc.GString()
            pc.NamedArgs()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.TypeComparison(),
        23
    ),
    GroovyBug(
        "17.GROOVY-5702",
        [
            pc.VarTypeInference(),
            pc.Overriding()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Resolution(),
        18
    ),
    GroovyBug(
        "18.GROOVY-7813",
        [
            pc.NestedDeclaration()
        ],
        False,
        sy.Runtime(sy.VerifyError()),
        rc.IncorrectComputation(),
        ct.Resolution(),
        10
    ),
    GroovyBug(
        "19.GROOVY-5148",
        [
            pc.PrimitiveTypes()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.TypeComparison(),
        1
    ),
    GroovyBug(
        "20.GROOVY-7888",
        [
            pc.ParameterizedTypes(),
            pc.Collections(),
            pc.Property(),
            pc.AugmentedAssignmentOperator(),
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.TypeExpression(),
        1
    ),
]
