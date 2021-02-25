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
        ct.Inference(),  # type variable substitution
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
        ct.Inference(),  # type variable substitution
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
        rc.IncorrectDataType(),  # Or maybe programming error
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
        ct.SubtypingRelated(), 
        7
    ),
    GroovyBug(
        "8.GROOVY-7721",
        [pc.Arrays(), pc.Subtyping(), pc.Overriding()],
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
        ct.Mechanics(), # Code Generation
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
        rc.WrongDataReference(),  # Programming error
        ct.Inference(),  # type variable substitution
        9
    ),
    GroovyBug(
        "11.GROOVY-7333",
        [pc.FlowTyping(), 
         pc.PrimitiveTypes(),
         pc.Arrays()],
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
        ct.OtherSemanticChecking(), # Resolution
        7
    ),
    GroovyBug(
        "13.GROOVY-8445",
        [pc.Lambdas(), pc.Collections(), pc.ParamTypeInference()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Approximation(),
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
        [pc.NamedArgs(), pc.NestedDeclaration()],
        True,
        sy.CompileTimeError(),
        rc.InsufficientFunctionality(),
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
        [pc.Overriding(), pc.Varargs(), pc.Subtyping()],
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
        rc.InsufficientFunctionality(),
        ct.Mechanics(),
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
        10
    )
]


groovy_iter2 = [
    GroovyBug(
        "1.GROOVY-6489",
        [pc.JavaInterop(),
         pc.WithMultipleAssignment()
         ],
        True,
        sy.InternalCompilerError(),
        rc.WrongParams(),
        ct.TypeExpression(),
    ),
    GroovyBug(
        "2.Groovy-8686",
        [pc.FlowTyping()],
        False,
        sy.Runtime(sy.AbstractMethodError()),
        rc.MissingMethod(),
        ct.Environment(),
    ),
    GroovyBug(
        "3.Groovy-6415",
        [pc.ParameterizedFunctions()],
        True,
        sy.CompileTimeError(),
        rc.IncorrectComputation(),
        ct.Environment()  # XXX
    ),
    GroovyBug(
        "4.Groovy-8590",
        [pc.Cast(), pc.Subtyping()],
        True,
        sy.CompileTimeError(),
        rc.IncorrectCondition(),
        ct.TypeExpression()
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
        ct.Resolution()
    ),
    GroovyBug(
        "6.Groovy-6034",
        [pc.PrimitiveTypes()],
        False,  # At the time was false
        sy.Runtime(sy.VerifyError()),
        rc.DesignIssue(),
        ct.TypeExpression(),
    ),
    GroovyBug(
        "7.Groovy-6195",
        [pc.Collections(), pc.VarTypeInference()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Resolution()
    ),
    GroovyBug(
        "8.Groovy-5873",
        [pc.Inheritance(), pc.ParameterizedClasses(),
         pc.ParameterizedTypes(), pc.Property()
         ],
        True,
        sy.CompileTimeError(),
        rc.InsufficientFunctionality(),
        ct.Inference()
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
        ct.SubtypingRelated()  # XXX
    ),
    GroovyBug(
        "10.Groovy-9328",
        [pc.AccessModifiers(), pc.AnonymousClass(),
         pc.Overriding()],
        True,
        sy.CompileTimeError(),
        rc.IncorrectCondition(),
        ct.Environment()
    ),
    GroovyBug(
        "11.Groovy-5175",
        [pc.Arrays(),
         pc.Subtyping()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.SubtypingRelated()
    ),
    GroovyBug(
        "12.Groovy-7922",
        [pc.Overloading(), pc.Inheritance()],
        False,
        sy.Runtime(sy.AmbiguousMethodError()),
        rc.IncorrectComputation(),
        ct.Resolution()
    ),
    GroovyBug(
        "13.Groovy-6129",
        [pc.Collections(),
         pc.ParameterizedTypes(),
         pc.TypeArgsInference()],
        True,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.Inference()
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
        ct.Inference()
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
        ct.Inference()
    ),
    GroovyBug(
        "16.Groovy-7307",
        [pc.Subtyping(),
         pc.ParameterizedFunctions(), pc.BoundedPolymorphism()
         ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.SubtypingRelated()
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
        ct.Approximation()
    ),
    GroovyBug(
        "18.Groovy-5580",
        [pc.Inheritance(), pc.Property()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Resolution()
    ),
    GroovyBug(
        "19.Groovy-7061",
        [pc.Collections(), pc.ParamTypeInference(),
         pc.Lambdas()],
        True,
        sy.CompileTimeError(),
        rc.IncorrectComputation(),
        ct.Inference()
    ),
    GroovyBug(
        "20.Groovy-5240",
        [pc.Reflection()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.TypeExpression()
    )
]
