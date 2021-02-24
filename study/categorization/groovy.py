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
        ct.Resolution()
    ),
    GroovyBug(
        "3.GROOVY-5217",
        [pc.Lambdas(), pc.FunctionTypes(), pc.Property()],
        True,
        sy.CompileTimeError(),
        rc.IncorrectSequence(),
        ct.Resolution()
    ),
    GroovyBug(
        "4.GROOVY-7211",
        [pc.ParameterizedClasses(),
         pc.ParameterizedTypes(),
         pc.NamedArgs()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Inference()  # type variable substitution
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
    ),
    GroovyBug(
        "6.GROOVY-5232",
        [pc.Property(), pc.VarTypeInference()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Resolution()
    ),
    GroovyBug(
        "7.GROOVY-8330",
        [pc.Subtyping(), pc.Inheritance(), pc.Cast()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.OtherSemanticChecking(),
    ),
    GroovyBug(
        "8.GROOVY-7721",
        [pc.Arrays(), pc.Subtyping(), pc.Overriding()],
        True,
        sy.CompileTimeError(),
        rc.FunctionalSpecificationMismatch(),
        ct.Resolution(),
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
        ct.Misc()
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
    ),
    GroovyBug(
        "12.GROOVY-7987",
        [pc.StaticMethod()],
        False,
        sy.Runtime(sy.ClassCastException()),
        rc.MissingCase(),
        ct.OtherSemanticChecking()
    ),
    GroovyBug(
        "13.GROOVY-8445",
        [pc.Lambdas(), pc.Collections(), pc.ParamTypeInference()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Approximation()
    ),
    GroovyBug(
        "14.GROOVY-7316",
        [pc.ParameterizedFunctions(),
         pc.Collections()],
        True,
        sy.CompileTimeError(),
        rc.FunctionalSpecificationMismatch(),
        ct.TypeExpression()
    ),
    GroovyBug(
        "15.GROOVY-7420",
        [pc.PrimitiveTypes(), pc.Overloading()],
        True,
        sy.CompileTimeError(),
        rc.FunctionalSpecificationMismatch(),
        ct.Resolution()
    ),
    GroovyBug(
        "16.GROOVY-7315",
        [pc.NamedArgs(), pc.NestedDeclaration()],
        True,
        sy.CompileTimeError(),
        rc.InsufficientFunctionality(),
        ct.OtherSemanticChecking(),
    ),
    GroovyBug(
        "17.GROOVY-6030",
        [pc.Collections(), pc.Overriding(), pc.Overloading(),
         pc.Subtyping(), pc.Lambdas()],
        True,
        sy.CompileTimeError(),
        rc.IncorrectSequence(),
        ct.Resolution()
    ),
    GroovyBug(
        "18.GROOVY-7711",
        [pc.Overriding(), pc.Varargs(), pc.Subtyping()],
        True,
        sy.CompileTimeError(),
        rc.IncorrectComputation(),
        ct.Resolution()
    ),
    GroovyBug(
        "19.GROOVY-6119",
        [pc.Collections(), pc.NamedArgs()],
        True,
        sy.CompileTimeError(),
        rc.InsufficientFunctionality(),
        ct.Mechanics()
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
        ct.TypeExpression()
    )
]
