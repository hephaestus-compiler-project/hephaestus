from bug import KotlinBug
import categories as ct
import characteristics as pc
import symptoms as sy
import root_causes as rc


kotlin_iter1 = [
    KotlinBug(
        "1.KT-1934",
        [pc.Inheritance()],
        False,
        sy.Runtime(sy.WrongMethodCalled()),
        rc.MissingCase(),
        ct.Declarations()
    ),
    KotlinBug(
        "2.KT-4814",
        [pc.ArithmeticExpressions()],
        False,
        sy.Runtime(sy.VerifyError()),
        rc.MissingCase(),
        ct.TypeExpression()
    ),
    KotlinBug(
        "3.KT-42175",
        [
            pc.Lambdas(),
            pc.Collections(),
            pc.This()
        ],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Inference()  # "type variable substitution"
    ),
    KotlinBug(
        "4.KT-10244",
        [pc.FlowTyping(),
         pc.IntersectionTypes(),
         pc.Conditionals()],
        False,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.Declarations()
    ),
    KotlinBug(
        "5.KT-10472",
        [pc.Overloading(), pc.Varargs(),
         pc.ParameterizedClasses(),
         pc.ParameterizedFunctions(),
         pc.ParameterizedTypes()],
        True,
        sy.Runtime(sy.NullPointerException()),
        rc.MissingCase(),
        ct.Resolution()
    ),
    KotlinBug(
        "6.KT-7485",
        [pc.Where(),
         pc.BoundedPolymorphism(),
         pc.ParameterizedFunctions(),
         pc.ParameterizedClasses(),
         pc.Nullables(),
         pc.Subtyping()],
        False,
        sy.Runtime(sy.NullPointerException()),
        rc.IncorrectComputation(),
        ct.SubtypingRelated()
    ),
    KotlinBug(
        "7.KT-23748",
        [pc.ParameterizedFunctions(),
         pc.Subtyping(),
         pc.Nullables(),
         pc.ElvisOperator()],
        True,
        sy.CompileTimeError(),
        rc.DesignIssue(),
        ct.Inference()  # constraint solving
    ),
    KotlinBug(
        "8.KT-22728",
        [pc.Lambdas(),
         pc.ExtensionFunctions(),
         pc.Typedefs(),
         pc.Import(),
         pc.FunctionTypes()],
        True,
        sy.CompileTimeError(),
        rc.WrongParams(),
        ct.Misc()  # mechanics
    ),
    KotlinBug(
        "9.KT-10711",
        [pc.ParameterizedFunctions(),
         pc.Collections(),
         pc.FunctionReferences()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Inference(),  # constraint solving
    ),
    KotlinBug(
        "10.KT-37249",
        [pc.Conditionals(), pc.TryCatch(), pc.Lambdas()],
        True,
        sy.CompileTimeError(),
        rc.InsufficientFunctionality(),
        ct.Inference()  # constraint solving
    ),
    KotlinBug(
        "11.KT-11468",
        [pc.ParameterizedClasses(), pc.DeclVariance(),
         pc.ParameterizedTypes(),
         pc.Subtyping()],
        True,
        sy.InternalCompilerError(),
        rc.DesignIssue(),
        ct.SubtypingRelated()
    ),
    KotlinBug(
        "12.KT-6014",
        [pc.Overriding(), pc.Inheritance(), pc.Delegation()],
        True,
        sy.CompileTimeError(),
        rc.IncorrectComputation(),
        ct.Resolution()
    ),
    KotlinBug(
        "13.KT-12044",
        [pc.Conditionals(), pc.PropertyReference()],
        True,
        sy.CompileTimeError(),
        rc.WrongParams(),
        ct.Resolution()
    ),
    KotlinBug(
        "14.KT-4334",
        [pc.Lambdas(), pc.Loops()],
        False,
        sy.InternalCompilerError(),
        rc.MissingCase(),
        ct.Misc()
    ),
    KotlinBug(
        "15.KT-32184",
        [pc.Lambdas(), pc.DataClasses()],
        True,
        sy.InternalCompilerError(),
        rc.WrongParams(),
        ct.Resolution()
    ),
    KotlinBug(
        "16.KT-10197",
        [pc.Overriding(), pc.Inheritance(), pc.Delegation()],
        False,
        sy.Runtime(sy.AbstractMethodError()),
        rc.MissingCase(),
        ct.Declarations(),
    ),
    KotlinBug(
        "17.KT-41693",
        [pc.Conditionals(), pc.Import(),
         pc.FlexibleTypes(),
         pc.JavaInterop()],
        True,
        sy.Runtime(sy.NullPointerException()),
        rc.MissingCase(),
        ct.Approximation()
    ),
    KotlinBug(
        "18.KT-44420",
        [pc.FlexibleTypes(),
         pc.Collections(),
         pc.VarTypeInference(),
         pc.JavaInterop()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Approximation(),
    ),
    KotlinBug(
        "19.KT-35602",
        [pc.ParameterizedClasses(),
         pc.FBounded(),
         pc.ParameterizedTypes(),
         pc.UseVariance(),
         pc.NullAssertion()],
        True,
        sy.CompileTimeError(),
        rc.MissingCase(),
        ct.Approximation()
    ),
    KotlinBug(
        "20.KT-6992",
        [pc.Overloading(),
         pc.ParameterizedClasses(),
         pc.Delegation(),
         pc.This()],
        False,
        sy.MisleadingReport(),
        rc.MissingCase(),
        ct.Resolution()
    )
]
