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
        # maybe also ct.TypeComparsion() because we are comparing the length of parameterized type and redirectGenericsTypes and also is bound-related
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
        # 11
        9
        ),
    GroovyBug(
        "3.GROOVY-5217",
        [pc.Lambdas(), pc.FunctionTypes(), pc.Property()],
        True,
        sy.CompileTimeError(),
        rc.IncorrectSequence(),
        ct.Resolution(),
        # 8
        7
    ),
    GroovyBug(
        "4.GROOVY-7211",
        #pc.Property()
        [pc.ParameterizedClasses(),
         pc.ParameterizedTypes(),
         pc.NamedArgs()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Inference(),
        # 20
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
        # ct.Inference() because We want to find inferred type of type variable Map(K,V) and we need to take into consideration the type of key given may be supertype (Object)
        ct.TypeExpression(),
        # 26
        14
    ),
    GroovyBug(
        "6.GROOVY-5232",
        [pc.Property(), pc.VarTypeInference()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Resolution(),
        # 15
        9
    ),
    GroovyBug(
        "7.GROOVY-8330",
        [pc.Subtyping(), pc.Inheritance(), pc.Cast()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.TypeComparison(),
        # 12
        7
    ),
    GroovyBug(
        "8.GROOVY-7721",
        # pc.JavaInterop()
        [pc.Arrays(), pc.Subtyping(), pc.Overriding()],
        True,
        sy.CompileTimeError(),
        rc.FunctionalSpecificationMismatch(),
        ct.Resolution(),
        # 18
        13
    ),
    GroovyBug(
        "9.GROOVY-6021",
        # pc.Arrays, pc.WithMultipleAssignment(),
        [pc.Lambdas(),
         pc.Collections(),
         pc.DelegationAPI(),
         pc.VarTypeInference()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Transformation(),
        # 16
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
        # 10
        9
    ),
    GroovyBug(
        "11.GROOVY-7333",
        #pc.Subtyping()
        [pc.FlowTyping(),
         pc.PrimitiveTypes(),
         pc.Arrays()],
        True,
        sy.CompileTimeError(),
        # agreed also consider rc.IncorrectComputation()  Incorrect union type computed in case one of the types is Object
        rc.MissingCase(),
        ct.Approximation(),
        # 10
        7

    ),
    GroovyBug(
        "12.GROOVY-7987",
        # why static?
        [pc.StaticMethod()],
        False,
        sy.Runtime(sy.ClassCastException()),
        rc.MissingCase(),
        ct.OtherSemanticChecking(),
        # 10
        7
    ),
     GroovyBug(
        "13.GROOVY-8445",
        # no pc.ParamTypeInference(), pc.Streams()
        [pc.Lambdas(), pc.Collections(), pc.ParamTypeInference()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Approximation(),
        # 14
        11
    ),
    GroovyBug(
        "14.GROOVY-7316",
        [pc.ParameterizedFunctions(),
         pc.Collections()],
        True,
        sy.CompileTimeError(),
        rc.FunctionalSpecificationMismatch(),
        ct.TypeExpression(),
        # 4
        2
    ),
    GroovyBug(
        "15.GROOVY-7420",
        [pc.PrimitiveTypes(), pc.Overloading()],
        True,
        sy.CompileTimeError(),
        rc.FunctionalSpecificationMismatch(),
        ct.Resolution(),
        # 12
        10
    ),
 GroovyBug(
        "16.GROOVY-7315",
        # pc.PrimitiveTypes()
        [pc.NamedArgs(), pc.NestedDeclaration()],
        True,
        sy.CompileTimeError(),
        rc.InsufficientAlgorithmImplementation(),
        ct.OtherSemanticChecking(),
        # 12
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
        # 6
        4
    ),
    GroovyBug(
        "18.GROOVY-7711",
        # pc.Inheritance()
        [pc.Overriding(), pc.Varargs(), pc.Subtyping()],
        True,
        sy.CompileTimeError(),
        rc.IncorrectComputation(),
        ct.Resolution(),
        13
    ),
    GroovyBug(
        "19.GROOVY-6119",
        # pc.PrimitiveTypes(), pc.Property()
        [pc.Collections(), pc.NamedArgs()],
        True,
        sy.CompileTimeError(),
        rc.InsufficientAlgorithmImplementation(),
        # agreed, also consider ct.Declaration because we are checking if constructor with map type argument is semantically correct
        #   If a class defines a constructor which takes a map as argument, then the type checker doesn't recognize it and will think that constructor calls with maps are the default groovy map-style constructor.
        ct.Transformation(),
        8
    ),
    GroovyBug(
        "20.GROOVY-8310",
        [pc.ParameterizedTypes(),
         pc.ParameterizedFunctions(),
         pc.Collections(),
         pc.Lambdas(),
         pc.Subtyping()],
        False,
        sy.Runtime(),
        rc.IncorrectCondition(),
        ct.TypeExpression(),
        # 12
        10
    )
]




groovy_iter2 = [
    GroovyBug(
        "1.GROOVY-6489",
        [pc.ParameterizedTypes, pc.JavaInterop(),
         pc.WithMultipleAssignment()
         ],
        True,
        sy.InternalCompilerError(),
        rc.WrongParams(),
        ct.TypeExpression(),
        17
    ),
    GroovyBug(
        "2.Groovy-8686",
        [pc.FlowTyping()],
        False,
        sy.Runtime(sy.AbstractMethodError()),
        rc.MissingCase(),
        ct.Environment(),
        4
    ),
    GroovyBug(
        "3.Groovy-6415",
        [pc.ParameterizedFunctions()],
        True,
        sy.CompileTimeError(),
        rc.IncorrectComputation(),
        ct.Environment(),  # TypeExpression
        12
    ),
    GroovyBug(
        "4.Groovy-8590",
        [pc.PrimitiveTypes(), pc.Cast(), pc.Subtyping()],
        True,
        sy.CompileTimeError(),
        rc.IncorrectCondition(),
        ct.TypeExpression(),
        7
    ),
    GroovyBug(
        "5.Groovy-6761",
        [pc.ParameterizedFunctions(),
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
        "6.Groovy-6034",
        [pc.PrimitiveTypes()],
        False,  # At the time was false
        sy.Runtime(sy.VerifyError()),
        rc.DesignIssue(),
        ct.TypeExpression(),
        5
    ),
    GroovyBug(
        "7.Groovy-6195",
        [pc.Collections(), pc.VarTypeInference()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Resolution(),
        7
    ),
    GroovyBug(
        "8.Groovy-5873",
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
        "9.Groovy-5415",
        [pc.JavaInterop(),
         pc.ParameterizedClasses(),
         pc.ParameterizedTypes(),
         pc.ParameterizedFunctions(),
         pc.Reflection()
         ],
        True,
        sy.CompileTimeError(),
        rc.ExtraneousComputation(),
        ct.TypeComparison(),
        11
    ),
    GroovyBug(
        "10.Groovy-9328",
        [pc.AccessModifiers(), pc.AnonymousClass(),
         pc.Overriding()],
        True,
        sy.CompileTimeError(),
        rc.IncorrectCondition(),
        ct.Environment(),
        14
    ),
    GroovyBug(
        "11.Groovy-5175",
        [pc.Arrays(),
         pc.Subtyping()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.TypeComparison(),
        7
    ),
    GroovyBug(
        "12.Groovy-7922",
        [pc.Overloading(), pc.Inheritance()],
        False,
        sy.Runtime(sy.AmbiguousMethodError()),
        rc.IncorrectComputation(),
        ct.Resolution(),
        9
    ),
    GroovyBug(
        "13.Groovy-6129",
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
        "14.Groovy-8090",
        [pc.Collections(),
         pc.ParameterizedTypes(),
         pc.ParameterizedFunctions()
         ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Inference(),
        7
    ),
    GroovyBug(
        "15.Groovy-5742",
        [pc.Import(), pc.ParameterizedClasses(),
         pc.FBounded(), pc.ParameterizedFunctions(),
         pc.ParameterizedTypes(), pc.Inheritance()
         ],
        True,
        sy.InternalCompilerError(),
        rc.IncorrectComputation(),
        ct.Inference(),
        12
    ),
    GroovyBug(
        "16.Groovy-7307",
        [pc.Subtyping(),
         pc.ParameterizedFunctions(), pc.BoundedPolymorphism()
         ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.TypeComparison(),
        11
    ),
    GroovyBug(
        "17.Groovy-7618",
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
        "18.Groovy-5580",
        [pc.Inheritance(), pc.Property()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Resolution(),
        14
    ),
    GroovyBug(
        "19.Groovy-7061",
        [pc.Collections(), pc.ParamTypeInference(),
         pc.Lambdas()],
        True,
        sy.CompileTimeError(),
        rc.IncorrectComputation(),
        ct.Inference(),
        5
    ),
    GroovyBug(
        "20.Groovy-5240",
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
            pc.FunctionalInterface(),
            pc.TypeArgsInference(),
            pc.Overriding()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
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
        rc.MissingCase(),
        ct.Inference(), # TypeExpression
        1
    ),
    GroovyBug(
        "9.GROOVY-9518",
        [
            pc.JavaInterop(),
            pc.FunctionalInterface(),
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
        [
            pc.AnonymousClass(),
            pc.ParameterizedClasses(),
            pc.ParameterizedTypes(),
            pc.TypeArgsInference(),
            pc.Overriding()
        ],
        False,
        sy.InternalCompilerError(),
        rc.DesignIssue(),
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
        [
            pc.Collections(),
            pc.ParameterizedTypes(),
            pc.NestedDeclaration(),
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
