from src.analysis import type_dependency_analysis as tda
from src.ir import ast, types as tp, kotlin_types as kt, context as ctx
from tests.resources import type_analysis_programs as tap



def assert_nodes(nodes, expected_nodes):
    assert set(nodes) == set(expected_nodes)


def tuple2str(tpl):
    return "/".join(tpl)


def to_str_dict(res):
    new_res = {}
    for k, v in res.items():
        new_res[str(k)] = [str(i) for i in v]
    return new_res


def test_program1():
    # Foo<String> x = new Foo<String>()
    program = tap.program1
    a = tda.TypeDependencyAnalysis(program, kt.KotlinBuiltinFactory())
    a.visit(program)
    res = to_str_dict(a.result())
    assert res == {
        '!TypeVariable[global/x/Foo/T]': [
            "-> Type[String] (declared)",
        ],
        "Declaration[global/x]": [
            "-> TypeConInstCall[global/x/Foo] (inferred)",
            "-> TypeConInstDecl[global/x/Foo] (declared)"
        ],
        'TypeConInstCall[global/x/Foo]': [
            '-> TypeVariable[global/x/Foo/T] (declared)'
        ],
        'TypeConInstDecl[global/x/Foo]': [
            '-> !TypeVariable[global/x/Foo/T] (declared)'
        ],
        'TypeVariable[global/x/Foo/T]': [
            '-> Type[String] (declared)',
            "-> !TypeVariable[global/x/Foo/T] (inferred)",
        ]
    }


def test_program2():
    # String x = "f"
    # Foo<String> y = new Foo<String>(x)
    program = tap.program2
    a = tda.TypeDependencyAnalysis(program, kt.KotlinBuiltinFactory())
    a.visit(program)
    res = to_str_dict(a.result())

    assert res == {
        '!TypeVariable[global/y/Foo/T]': ['-> Type[String] (declared)'],
        'Declaration[global/Foo/f]': ['-> Type[T] (declared)'],
        'Declaration[global/x]': [
            '-> Type[String] (inferred)',
            '-> Type[String] (declared)',
        ],
        'Declaration[global/y/Foo/f]': [
            '-> Declaration[global/x] (inferred)',
        ],
        'Declaration[global/y]': [
            '-> TypeConInstCall[global/y/Foo] (inferred)',
            '-> TypeConInstDecl[global/y/Foo] (declared)'
        ],
        'TypeConInstCall[global/y/Foo]': [
            '-> TypeVariable[global/y/Foo/T] (declared)',
        ],
        'TypeConInstDecl[global/y/Foo]': [
            '-> !TypeVariable[global/y/Foo/T] (declared)',
        ],
        'TypeVariable[global/y/Foo/T]': [
            '-> Type[String] (declared)',
            '-> Declaration[global/x] (inferred)',
            '-> !TypeVariable[global/y/Foo/T] (inferred)'
        ]
    }



def test_program3():
    # String x ="f"
    # Bar y = new Bar(new Foo<String>(x))
    program = tap.program3
    a = tda.TypeDependencyAnalysis(program, kt.KotlinBuiltinFactory())
    a.visit(program)
    res = to_str_dict(a.result())

    assert res == {
        '!TypeVariable[global/y/Bar/f/Foo/T]': ['-> Type[String] (declared)'],
        'Declaration[global/Bar/f]': ['-> Type[Foo] (declared)'],
        'Declaration[global/Foo/f]': ['-> Type[T] (declared)'],
        'Declaration[global/x]': [
            '-> Type[String] (inferred)',
            '-> Type[String] (declared)'
        ],
        'Declaration[global/y/Bar/f/Foo/f]': [
            '-> Declaration[global/x] (inferred)',
        ],
        'Declaration[global/y/Bar/f]': [
            '-> TypeConInstCall[global/y/Bar/f/Foo] (inferred)',
            '-> TypeConInstDecl[global/y/Bar/f/Foo] (declared)'
        ],
        'Declaration[global/y]': [
            '-> Type[Bar] (inferred)',
            '-> Type[Bar] (declared)'
        ],
        'TypeConInstCall[global/y/Bar/f/Foo]': [
            '-> TypeVariable[global/y/Bar/f/Foo/T] (declared)'
        ],
        'TypeConInstDecl[global/y/Bar/f/Foo]': [
            '-> !TypeVariable[global/y/Bar/f/Foo/T] (declared)',
        ],
        'TypeVariable[global/y/Bar/f/Foo/T]': [
            '-> Type[String] (declared)',
            '-> Declaration[global/x] (inferred)',
            '-> !TypeVariable[global/y/Bar/f/Foo/T] (inferred)'
        ]

    }


def test_program4():
    # class A<T>
    # class B<T, T2> : A<T2>()
    # class C<T> : B<String, T>()
    # val x: A<String> = new C<String>()

    program = tap.program4
    a = tda.TypeDependencyAnalysis(program, kt.KotlinBuiltinFactory())
    a.visit(program)
    res = to_str_dict(a.result())

    assert res == {
        '!TypeVariable[global/x/A/T]': [
            '-> Type[String] (declared)'
        ],
        'Declaration[global/x]': [
            '-> TypeConInstCall[global/x/C] (inferred)',
            '-> TypeConInstDecl[global/x/A] (declared)'
        ],
        'TypeConInstCall[global/x/C]': [
            '-> TypeVariable[global/x/C/T] (declared)'
        ],
        'TypeConInstDecl[global/x/A]': [
            '-> !TypeVariable[global/x/A/T] (declared)'
        ],
        'TypeVariable[global/x/C/T]': [
            '-> Type[String] (declared)',
            '-> !TypeVariable[global/x/A/T] (inferred)',
        ]
    }


def test_program5():
    # fun foo(x): String {
    #    var y: String = x
    #    return y
    # }
    # val y: A<String> = A<String>(foo())
    program = tap.program5
    a = tda.TypeDependencyAnalysis(program, kt.KotlinBuiltinFactory())
    a.visit(program)
    res = to_str_dict(a.result())

    assert res == {
        '!TypeVariable[global/y/A/T]': ['-> Type[String] (declared)'],
        'Declaration[global/A/f]': ['-> Type[T] (declared)'],
        'Declaration[global/foo/__RET__]': [
            '-> Declaration[global/foo/y] (inferred)',
            '-> Type[String] (declared)',
        ],
        'Declaration[global/foo/x]': ['-> Type[String] (declared)'],
        'Declaration[global/foo/y]': [
            '-> Declaration[global/foo/x] (inferred)',
            '-> Type[String] (declared)'
        ],
        'Declaration[global/y/A/f/foo/x]': ['-> Type[String] (inferred)'],
        'Declaration[global/y/A/f]': ['-> Type[String] (inferred)'],
        'Declaration[global/y]': [
            '-> TypeConInstCall[global/y/A] (inferred)',
            '-> TypeConInstDecl[global/y/A] (declared)'
        ],
        'TypeConInstCall[global/y/A]': [
            '-> TypeVariable[global/y/A/T] (declared)'
        ],
        'TypeConInstDecl[global/y/A]': [
            '-> !TypeVariable[global/y/A/T] (declared)'
        ],
        'TypeVariable[global/y/A/T]': [
            '-> Type[String] (declared)',
            '-> Type[String] (inferred)',
            '-> !TypeVariable[global/y/A/T] (inferred)',
        ]
    }


def test_program6():
    # class A<T> {
    #     fun foo(x: T) = x
    # }
    # val y: String = A<String>().foo()
    program = tap.program6
    a = tda.TypeDependencyAnalysis(program, kt.KotlinBuiltinFactory())
    a.visit(program)
    res = to_str_dict(a.result())

    assert res == {
        'Declaration[global/A/foo/__RET__]': [
            '-> Declaration[global/A/foo/x] (inferred)',
            '-> Type[T] (declared)'
        ],
        'Declaration[global/A/foo/x]': ['-> Type[T] (declared)'],
        'Declaration[global/x]': [
            '-> Type[String] (inferred)',
            '-> Type[String] (declared)',
        ],
        'TypeConInstCall[global/x/foo/__REC__/A]': [
            '-> TypeVariable[global/x/foo/__REC__/A/T] (declared)'
        ],
        'TypeVariable[global/x/foo/__REC__/A/T]': ['-> Type[String] (declared)'],
    }
