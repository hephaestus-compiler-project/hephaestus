from copy import copy

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


def find_omittable_node(node_id, nodes):
    for n in nodes:
        if n.node_id == node_id and n.is_omittable():
            return n
    return None


def test_program1():
    # Foo<String> x = new Foo<String>()
    program = tap.program1
    a = tda.TypeDependencyAnalysis(program)
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
    a = tda.TypeDependencyAnalysis(program)
    a.visit(program)
    res = to_str_dict(a.result())

    assert res == {
        '!TypeVariable[global/y/Foo/T]': ['-> Type[String] (declared)'],
        'Declaration[global/Foo/f]': ['-> Type[T] (declared)'],
        'Declaration[global/x]': [
            '-> Type[String] (inferred)',
            '-> Type[global/x/String] (declared)',
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
    a = tda.TypeDependencyAnalysis(program)
    a.visit(program)
    res = to_str_dict(a.result())

    assert res == {
        '!TypeVariable[global/y/Bar/f/Foo/T]': ['-> Type[String] (declared)'],
        'Declaration[global/Bar/f]': ['-> Type[Foo] (declared)'],
        'Declaration[global/Foo/f]': ['-> Type[T] (declared)'],
        'Declaration[global/x]': [
            '-> Type[String] (inferred)',
            '-> Type[global/x/String] (declared)'
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
            '-> Type[global/y/Bar] (declared)'
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
    a = tda.TypeDependencyAnalysis(program)
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
    a = tda.TypeDependencyAnalysis(program)
    a.visit(program)
    res = to_str_dict(a.result())

    assert res == {
        '!TypeVariable[global/y/A/T]': ['-> Type[String] (declared)'],
        'Declaration[global/A/f]': ['-> Type[T] (declared)'],
        'Declaration[global/foo/__RET__]': [
            '-> Declaration[global/foo/y] (inferred)',
            '-> Type[global/foo/__RET__/String] (declared)',
        ],
        'Declaration[global/foo/x]': ['-> Type[String] (declared)'],
        'Declaration[global/foo/y]': [
            '-> Declaration[global/foo/x] (inferred)',
            '-> Type[global/foo/y/String] (declared)'
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
    a = tda.TypeDependencyAnalysis(program)
    a.visit(program)
    res = to_str_dict(a.result())

    assert res == {
        'Declaration[global/A/foo/foo]': [
            '-> Declaration[global/A/foo/x] (inferred)',
            '-> Type[global/A/foo/foo/T] (declared)'
        ],
        'Declaration[global/A/foo/x]': ['-> Type[T] (declared)'],
        'Declaration[global/x]': [
            '-> Type[String] (inferred)',
            '-> Type[global/x/String] (declared)',
        ],
        'TypeConInstCall[global/x/foo/__REC__/A]': [
            '-> TypeVariable[global/x/foo/__REC__/A/T] (declared)'
        ],
        'TypeVariable[global/x/foo/__REC__/A/T]': ['-> Type[String] (declared)'],
    }


def test_program7():
    # val x: A<String> = new A<String>()
    # val y: A<String> = if (true) x else new A<String>()
    program = tap.program7
    a = tda.TypeDependencyAnalysis(program)
    a.visit(program)
    res = to_str_dict(a.result())

    assert res == {
        '!TypeVariable[global/x/A/T]': ['-> Type[String] (declared)'],
        '!TypeVariable[global/y/A/T]': ['-> Type[String] (declared)'],
        'Declaration[global/x]': [
            '-> TypeConInstCall[global/x/A] (inferred)',
            '-> TypeConInstDecl[global/x/A] (declared)'
        ],
        'Declaration[global/y]': [
            '-> Declaration[global/x] (inferred)',
            '-> TypeConInstCall[global/y/A] (inferred)',
            '-> TypeConInstDecl[global/y/A] (declared)'
        ],
        'TypeConInstCall[global/x/A]': ['-> TypeVariable[global/x/A/T] (declared)'],
        'TypeConInstCall[global/y/A]': ['-> TypeVariable[global/y/A/T] (declared)'],
        'TypeConInstDecl[global/x/A]': ['-> !TypeVariable[global/x/A/T] (declared)'],
        'TypeConInstDecl[global/y/A]': ['-> !TypeVariable[global/y/A/T] (declared)'],
        'TypeVariable[global/x/A/T]': [
            '-> Type[String] (declared)',
            '-> !TypeVariable[global/x/A/T] (inferred)'
         ],
        'TypeVariable[global/y/A/T]': [
            '-> Type[String] (declared)',
            '-> !TypeVariable[global/y/A/T] (inferred)'
        ]
    }


def test_program8():
    # var x: A<String> = TODO()
    # x = A<String>()
    program = tap.program8
    a = tda.TypeDependencyAnalysis(program)
    a.visit(program)
    res = to_str_dict(a.result())

    assert res == {
        '!TypeVariable[global/foo/x/A/T]': ['-> Type[String] (declared)'],
        'Declaration[global/foo/x]': [
            '-> Type[A] (inferred)',
            '-> TypeConInstCall[global/foo/x/A] (inferred)',
            '-> TypeConInstDecl[global/foo/x/A] (declared)'
        ],
        'TypeConInstCall[global/foo/x/A]': [
            '-> TypeVariable[global/foo/x/A/T] (declared)'
        ],
        'TypeConInstDecl[global/foo/x/A]': [
            '-> !TypeVariable[global/foo/x/A/T] (declared)'
        ],
        'TypeVariable[global/foo/x/A/T]': [
            '-> Type[String] (declared)',
            '-> !TypeVariable[global/foo/x/A/T] (inferred)'
        ]
    }


def test_program9():
    # class Bar(val f: A<String)
    # var x: Bar() = TODO()
    # x.f = A<String>()
    program = tap.program9
    a = tda.TypeDependencyAnalysis(program)
    a.visit(program)
    res = to_str_dict(a.result())

    assert res == {
        '!TypeVariable[global/foo/1/B/f/A/T]': ['-> Type[String] (declared)'],
        'Declaration[global/foo/1/B/f]': [
            '-> TypeConInstCall[global/foo/1/B/f/A] (inferred)',
            '-> TypeConInstDecl[global/foo/1/B/f/A] (declared)',
        ],
        'Declaration[global/B/f]': ['-> Type[A] (declared)'],
        'Declaration[global/foo/x]': [
            '-> Type[B] (inferred)',
            '-> Type[global/foo/x/B] (declared)',
        ],
        'TypeConInstCall[global/foo/1/B/f/A]': [
            '-> TypeVariable[global/foo/1/B/f/A/T] (declared)'
        ],
        'TypeConInstDecl[global/foo/1/B/f/A]': [
            '-> !TypeVariable[global/foo/1/B/f/A/T] (declared)'
        ],
        'TypeVariable[global/foo/1/B/f/A/T]': [
            '-> Type[String] (declared)',
            '-> !TypeVariable[global/foo/1/B/f/A/T] (inferred)'
        ]
    }


def test_program10():
    # fun foo() {
    #  (new A<String>("x")).f = "fda"
    # }
    program = tap.program10
    a = tda.TypeDependencyAnalysis(program)
    a.visit(program)
    res = to_str_dict(a.result())

    assert res == {
        'Declaration[global/foo/A/f]': ['-> Type[String] (inferred)'],
        'Declaration[global/foo/1/A/f]': ['-> Type[String] (inferred)'],
        'Declaration[global/A/f]': ['-> Type[T] (declared)'],
        'TypeConInstCall[global/foo/A]': ['-> TypeVariable[global/foo/A/T] (declared)'],
        'TypeVariable[global/foo/A/T]': [
            '-> Type[String] (declared)',
            '-> Type[String] (inferred)',
        ]

    }


def test_program11():
    # fun foo() {
    #  (new A<A<String>>(new A<String>(""))).f = new A<String>("x")
    # }
    program = tap.program11
    a = tda.TypeDependencyAnalysis(program)
    a.visit(program)
    res = to_str_dict(a.result())

    assert res == {
        '!TypeVariable[global/foo/1/A/f/A/T]': ['-> Type[String] (declared)'],
        '!TypeVariable[global/foo/A/f/A/T]': ['-> Type[String] (declared)'],
        '!TypeVariable[global/foo/A/T/A/T]': ['-> Type[String] (declared)'],
        'Declaration[global/foo/1/A/f/A/f]': ['-> Type[String] (inferred)'],
        'Declaration[global/foo/1/A/f]': [
            '-> TypeConInstCall[global/foo/1/A/f/A] (inferred)',
            '-> TypeConInstDecl[global/foo/1/A/f/A] (declared)',
        ],
        'Declaration[global/foo/A/f/A/f]': ['-> Type[String] (inferred)'],
        'Declaration[global/foo/A/f]': [
            '-> TypeConInstCall[global/foo/A/f/A] (inferred)',
            '-> TypeConInstDecl[global/foo/A/f/A] (declared)',
        ],
        'Declaration[global/A/f]': ['-> Type[T] (declared)'],
        'TypeConInstCall[global/foo/1/A/f/A]': ['-> TypeVariable[global/foo/1/A/f/A/T] (declared)'],
        'TypeConInstCall[global/foo/A/f/A]': ['-> TypeVariable[global/foo/A/f/A/T] (declared)'],
        'TypeConInstCall[global/foo/A]': ['-> TypeVariable[global/foo/A/T] (declared)'],
        'TypeConInstDecl[global/foo/A/f/A]': ['-> !TypeVariable[global/foo/A/f/A/T] (declared)'],
        'TypeConInstDecl[global/foo/1/A/f/A]': ['-> !TypeVariable[global/foo/1/A/f/A/T] (declared)'],
        'TypeConInstDecl[global/foo/A/T/A]': [
            '-> !TypeVariable[global/foo/A/T/A/T] (declared)',
        ],
        'TypeVariable[global/foo/1/A/f/A/T]': [
            '-> Type[String] (declared)',
            '-> Type[String] (inferred)',
            '-> !TypeVariable[global/foo/1/A/f/A/T] (inferred)'
        ],
        'TypeVariable[global/foo/A/T]': [
            '-> TypeConInstCall[global/foo/A/f/A] (inferred)',
            '-> TypeConInstDecl[global/foo/A/f/A] (declared)',
        ],
        'TypeVariable[global/foo/A/f/A/T]': [
            '-> Type[String] (declared)',
            '-> Type[String] (inferred)',
            '-> !TypeVariable[global/foo/A/f/A/T] (inferred)'
        ],

    }


def test_program12():
    # class A<T>
    # class B: A<String>()
    # fun foo() {
    #     val x: B = new B()
    #     (if (true) new A<String>() else x).f = "fda"
    # }
    program = tap.program12
    a = tda.TypeDependencyAnalysis(program)
    a.visit(program)
    res = to_str_dict(a.result())


    assert res == {
        'Declaration[global/A/f]': ['-> Type[T] (declared)'],
        'Declaration[global/foo/2/A/f]': ['-> Type[String] (inferred)'],
        'Declaration[global/foo/A/f]': ['-> Type[String] (inferred)'],
        'Declaration[global/foo/x]': [
            '-> Type[B] (inferred)',
            '-> Type[global/foo/x/B] (declared)',
        ],
        'TypeConInstCall[global/foo/A]': [
            '-> TypeVariable[global/foo/A/T] (declared)'
        ],
        'TypeVariable[global/foo/A/T]': [
            '-> Type[String] (declared)',
            '-> Type[String] (inferred)',
        ]
    }


def test_program13():
    # class A<T>
    # class B: A<String>()
    # fun foo() {
    #     val t: String = "fdf"
    #     val x: B = new B()
    #     val y: String = (if (true) new A<String>(t) else x).f
    # }
    program = tap.program13
    a = tda.TypeDependencyAnalysis(program)
    a.visit(program)
    res = to_str_dict(a.result())

    assert res == {
        'Declaration[global/A/f]': ['-> Type[T] (declared)'],
        'Declaration[global/foo/t]': [
            '-> Type[String] (inferred)',
            '-> Type[global/foo/t/String] (declared)',
        ],
        'Declaration[global/foo/x]': [
            '-> Type[B] (inferred)',
            '-> Type[global/foo/x/B] (declared)',
        ],
        'Declaration[global/foo/y/f/A/f]': [
            '-> Declaration[global/foo/t] (inferred)'
        ],
        'Declaration[global/foo/y]': [
            '-> Type[String] (inferred)',
            '-> Type[global/foo/y/String] (declared)',
        ],
        'TypeConInstCall[global/foo/y/f/A]': [
            '-> TypeVariable[global/foo/y/f/A/T] (declared)'
        ],
        'TypeVariable[global/foo/y/f/A/T]': [
            '-> Type[String] (declared)',
            '-> Declaration[global/foo/t] (inferred)'
        ]
    }


def test_program14():
    # fun foo() {
    #     val x: Any = "fdf"
    #     x = Any()
    # }
    program = tap.program14
    a = tda.TypeDependencyAnalysis(program)
    a.visit(program)
    res = to_str_dict(a.result())


    assert res == {
        'Declaration[global/foo/x]': [
            '-> Type[String] (inferred)',
            '-> Type[global/foo/x/Any] (declared)',
            '-> Type[Any] (inferred)',
        ]
    }

    assert not tda.is_combination_feasible(a.result(), list(a.result().keys()))


def test_program15():
    # class A<T1, T2: T1>(val x: T1)
    # val x: A<Number, Intgeger> = new A<Number, Integer>(1)
    program = tap.program15
    a = tda.TypeDependencyAnalysis(program)
    a.visit(program)
    res = to_str_dict(a.result())

    assert res == {
        '!TypeVariable[global/x/A/T2]': ['-> Type[Int] (declared)'],
        '!TypeVariable[global/x/A/T]': ['-> Type[Number] (declared)'],
        'Declaration[global/A/f]': ['-> Type[T] (declared)'],
        'Declaration[global/x/A/f]': ['-> Type[Number] (inferred)'],
        'Declaration[global/x]': [
            '-> TypeConInstCall[global/x/A] (inferred)',
            '-> TypeConInstDecl[global/x/A] (declared)',
        ],
        'TypeConInstCall[global/x/A]': [
            '-> TypeVariable[global/x/A/T] (declared)',
            '-> TypeVariable[global/x/A/T2] (declared)'
        ],
        'TypeConInstDecl[global/x/A]': [
            '-> !TypeVariable[global/x/A/T] (declared)',
            '-> !TypeVariable[global/x/A/T2] (declared)'
        ],
        'TypeVariable[global/x/A/T2]': [
            '-> TypeVariable[global/x/A/T] (inferred)',
            '-> Type[Int] (declared)',
            '-> !TypeVariable[global/x/A/T2] (inferred)'
        ],
        'TypeVariable[global/x/A/T]': [
            '-> Type[Number] (declared)',
            '-> Type[Number] (inferred)',
            '-> !TypeVariable[global/x/A/T] (inferred)'
        ]
    }


def test_program16():
    # fun <T> foo(x: T): String = ""
    # fun bar() {
    #  foo<String>("x")
    # }
    program = tap.program16
    a = tda.TypeDependencyAnalysis(program)
    a.visit(program)
    res = to_str_dict(a.result())

    assert res == {
        'Declaration[global/bar/foo/x]': ['-> Type[String] (inferred)'],
        'Declaration[global/foo/foo]': [
            '-> Type[String] (inferred)',
            '-> Type[global/foo/foo/String] (declared)',
        ],
        'Declaration[global/foo/x]': ['-> Type[T] (declared)'],
        'TypeConInstCall[global/bar/foo]': [
            '-> TypeVariable[global/bar/foo/T] (declared)'
        ],
        'TypeVariable[global/bar/foo/T]': [
            '-> Type[String] (declared)',
            '-> Type[String] (inferred)',
        ]
    }


def test_program17():
    # fun <T> foo(x: T): String = ""
    # fun bar() {
    #  foo<A<String>>(A<String>())
    # }
    program = tap.program17
    a = tda.TypeDependencyAnalysis(program)
    a.visit(program)
    res = to_str_dict(a.result())

    assert res == {
        '!TypeVariable[global/bar/foo/x/A/T2]': ['-> Type[String] (declared)'],
        'Declaration[global/bar/foo/x]': [
            '-> TypeConInstCall[global/bar/foo/x/A] (inferred)',
            '-> TypeConInstDecl[global/bar/foo/x/A] (declared)',
        ],
        'Declaration[global/foo/foo]': [
            '-> Type[String] (inferred)',
            '-> Type[global/foo/foo/String] (declared)',
        ],
        'Declaration[global/foo/x]': ['-> Type[T] (declared)'],
        'TypeConInstCall[global/bar/foo/x/A]': [
            '-> TypeVariable[global/bar/foo/x/A/T2] (declared)'
        ],
        'TypeConInstCall[global/bar/foo]': [
            '-> TypeVariable[global/bar/foo/T] (declared)'
        ],
        'TypeConInstDecl[global/bar/foo/x/A]': [
            '-> !TypeVariable[global/bar/foo/x/A/T2] (declared)'
        ],
        'TypeVariable[global/bar/foo/T]': [
            '-> TypeConInstCall[global/bar/foo/x/A] (inferred)',
            '-> TypeConInstDecl[global/bar/foo/x/A] (declared)',
        ],
        'TypeVariable[global/bar/foo/x/A/T2]': [
            '-> Type[String] (declared)',
            '-> !TypeVariable[global/bar/foo/x/A/T2] (inferred)'
        ]
    }


def test_program18():
    # fun <T> foo(x: A<T>): String = ""
    # fun bar() {
    #  foo<String>(A<String>())
    # }
    program = tap.program18
    a = tda.TypeDependencyAnalysis(program)
    a.visit(program)
    res = to_str_dict(a.result())


    assert res == {
        '!TypeVariable[global/bar/foo/x/A/T2]': [
            '-> TypeVariable[global/bar/foo/T] (inferred)'
        ],
        'Declaration[global/bar/foo/x]': [
            '-> TypeConInstCall[global/bar/foo/x/A] (inferred)',
            '-> TypeConInstDecl[global/bar/foo/x/A] (declared)',
        ],
        'Declaration[global/foo/foo]': [
            '-> Type[String] (inferred)',
            '-> Type[global/foo/foo/String] (declared)',
        ],
        'Declaration[global/foo/x]': ['-> Type[A] (declared)'],
        'TypeConInstCall[global/bar/foo/x/A]': [
            '-> TypeVariable[global/bar/foo/x/A/T2] (declared)'
        ],
        'TypeConInstCall[global/bar/foo]': [
            '-> TypeVariable[global/bar/foo/T] (declared)'
        ],
        'TypeConInstDecl[global/bar/foo/x/A]': [
            '-> !TypeVariable[global/bar/foo/x/A/T2] (declared)'
        ],
        'TypeVariable[global/bar/foo/T]': [
            '-> Type[String] (declared)',
            '-> TypeVariable[global/bar/foo/x/A/T2] (inferred)'
        ],
        'TypeVariable[global/bar/foo/x/A/T2]': [
            '-> Type[String] (declared)',
            '-> !TypeVariable[global/bar/foo/x/A/T2] (inferred)',
        ]
    }


def test_program19():
    # class A<T>
    # class B: A<Int>
    # class C<T> (val f: A<T>)
    # val x: C<Int> = new C<Int>(B())
    program = tap.program19
    a = tda.TypeDependencyAnalysis(program)
    a.visit(program)
    res = to_str_dict(a.result())

    assert res == {
        '!TypeVariable[global/x/C/T]': ['-> Type[Int] (declared)'],
        'Declaration[global/C/f]': ['-> Type[A] (declared)'],
        'Declaration[global/x/C/f]': ['-> Type[B] (inferred)'],
        'Declaration[global/x]': [
            '-> TypeConInstCall[global/x/C] (inferred)',
            '-> TypeConInstDecl[global/x/C] (declared)',
        ],
        'TypeConInstCall[global/x/C]': [
            '-> TypeVariable[global/x/C/T] (declared)'
        ],
        'TypeConInstDecl[global/x/C]': [
            '-> !TypeVariable[global/x/C/T] (declared)'
        ],
        'TypeVariable[global/x/C/T]': [
            '-> Type[Int] (declared)',
            '-> Type[Int] (inferred)',
            '-> !TypeVariable[global/x/C/T] (inferred)'
        ]
    }


def test_program20():
    # class A<T>
    # class B<T> (val f: A<T>)
    # val x: B<String> = new B<String>(new A<String>())
    program = tap.program20
    a = tda.TypeDependencyAnalysis(program)
    a.visit(program)
    res = to_str_dict(a.result())

    assert res == {
        '!TypeVariable[global/x/B/T]': ['-> Type[String] (declared)'],
        '!TypeVariable[global/x/B/f/A/T]': [
            '-> TypeVariable[global/x/B/T] (inferred)'
        ],
        'Declaration[global/B/f]': ['-> Type[A] (declared)'],
        'Declaration[global/x/B/f]': [
            '-> TypeConInstCall[global/x/B/f/A] (inferred)',
            '-> TypeConInstDecl[global/x/B/f/A] (declared)',
        ],
        'Declaration[global/x]': [
            '-> TypeConInstCall[global/x/B] (inferred)',
            '-> TypeConInstDecl[global/x/B] (declared)'
        ],
        'TypeConInstCall[global/x/B/f/A]': [
            '-> TypeVariable[global/x/B/f/A/T] (declared)'
        ],
        'TypeConInstCall[global/x/B]': [
            '-> TypeVariable[global/x/B/T] (declared)'
        ],
        'TypeConInstDecl[global/x/B/f/A]': [
            '-> !TypeVariable[global/x/B/f/A/T] (declared)'
        ],
        'TypeConInstDecl[global/x/B]': [
            '-> !TypeVariable[global/x/B/T] (declared)'
        ],
        'TypeVariable[global/x/B/T]': [
            '-> Type[String] (declared)',
            '-> TypeVariable[global/x/B/f/A/T] (inferred)',
            '-> !TypeVariable[global/x/B/T] (inferred)'
        ],
        'TypeVariable[global/x/B/f/A/T]': [
            '-> Type[String] (declared)',
            '-> !TypeVariable[global/x/B/f/A/T] (inferred)',
        ]
    }


def test_program21():
    # class A<T>
    # class B<T>
    # class C<T> (val x: B<A<T>>)
    # val x: C<String> = new C<String>(B<A<String>>())
    program = tap.program21
    a = tda.TypeDependencyAnalysis(program)
    a.visit(program)
    res = to_str_dict(a.result())

    assert res == {
        '!TypeVariable[global/x/C/T]': ['-> Type[String] (declared)'],
        '!TypeVariable[global/x/C/f/B/T]': ['-> Type[A] (declared)'],
        '!TypeVariable[global/x/C/f/B/T/A/T]': [
            '-> TypeVariable[global/x/C/T] (inferred)'
        ],
        'Declaration[global/B/f]': ['-> Type[A] (declared)'],
        'Declaration[global/C/f]': ['-> Type[B] (declared)'],
        'Declaration[global/x/C/f]': [
            '-> TypeConInstCall[global/x/C/f/B] (inferred)',
            '-> TypeConInstDecl[global/x/C/f/B] (declared)',
        ],
        'Declaration[global/x]': [
            '-> TypeConInstCall[global/x/C] (inferred)',
            '-> TypeConInstDecl[global/x/C] (declared)'
        ],
        'TypeConInstCall[global/x/C/f/B]': [
            '-> TypeVariable[global/x/C/f/B/T] (declared)'
        ],
        'TypeConInstCall[global/x/C]': [
            '-> TypeVariable[global/x/C/T] (declared)'
        ],
        'TypeConInstDecl[global/x/C/f/B/T/A]': [
            '-> !TypeVariable[global/x/C/f/B/T/A/T] (declared)'
        ],
        'TypeConInstDecl[global/x/C/f/B]': [
            '-> !TypeVariable[global/x/C/f/B/T] (declared)'
        ],
        'TypeConInstDecl[global/x/C]': [
            '-> !TypeVariable[global/x/C/T] (declared)'
        ],
        'TypeVariable[global/x/C/T]': [
            '-> Type[String] (declared)',
            '-> TypeVariable[global/x/C/f/B/T/A/T] (inferred)',
            '-> !TypeVariable[global/x/C/T] (inferred)'
        ],
        'TypeVariable[global/x/C/f/B/T]': [
            '-> TypeConInstDecl[global/x/C/f/B/T/A] (declared)',
            '-> !TypeVariable[global/x/C/f/B/T] (inferred)'
        ]
    }


def test_program22():
    # class A<T>
    # class B<T>(val x: T)
    # val x: B<A<String>> = B<A<String>>(A<String>())
    program = tap.program22
    a = tda.TypeDependencyAnalysis(program)
    a.visit(program)
    res = to_str_dict(a.result())

    assert res == {
        '!TypeVariable[global/x/B/T2/A/T]': ['-> Type[String] (declared)'],
        '!TypeVariable[global/x/B/T2]': ['-> Type[A] (declared)'],
        '!TypeVariable[global/x/B/f/A/T]': ['-> Type[String] (declared)'],
        'Declaration[global/B/f]': ['-> Type[T2] (declared)'],
        'Declaration[global/x/B/f]': [
            '-> TypeConInstCall[global/x/B/f/A] (inferred)',
            '-> TypeConInstDecl[global/x/B/f/A] (declared)',
        ],
        'Declaration[global/x]': [
            '-> TypeConInstCall[global/x/B] (inferred)',
            '-> TypeConInstDecl[global/x/B] (declared)',
        ],
        'TypeConInstCall[global/x/B/f/A]': [
            '-> TypeVariable[global/x/B/f/A/T] (declared)'
        ],
        'TypeConInstCall[global/x/B]': [
            '-> TypeVariable[global/x/B/T2] (declared)'
        ],
        'TypeConInstDecl[global/x/B/T2/A]': [
            '-> !TypeVariable[global/x/B/T2/A/T] (declared)'
        ],
        'TypeConInstDecl[global/x/B/f/A]': [
            '-> !TypeVariable[global/x/B/f/A/T] (declared)'
        ],
        'TypeConInstDecl[global/x/B]': ['-> !TypeVariable[global/x/B/T2] (declared)'],
        'TypeVariable[global/x/B/T2]': [
            '-> TypeConInstCall[global/x/B/f/A] (inferred)',
            '-> TypeConInstDecl[global/x/B/f/A] (declared)',
            '-> !TypeVariable[global/x/B/T2] (inferred)',
        ],
        'TypeVariable[global/x/B/f/A/T]': [
            '-> Type[String] (declared)',
            '-> !TypeVariable[global/x/B/f/A/T] (inferred)'
        ]
    }


def test_program23():
    # fun <T> foo(): T
    # var x: String = foo()
    program = tap.program23
    a = tda.TypeDependencyAnalysis(program)
    a.visit(program)
    res = to_str_dict(a.result())

    assert res == {
        'Declaration[global/foo/foo]': [
            '-> Type[T] (inferred)',
            '-> Type[global/foo/foo/T] (declared)'
        ],
        'Declaration[global/x]': [
            '-> Type[global/x/String] (inferred)',
            '-> Type[global/x/String] (declared)',
        ],
        'TypeConInstCall[global/x/foo]': [
            '-> TypeVariable[global/x/foo/T] (declared)'
        ],
        'TypeVariable[global/x/foo/T]': [
            '-> Type[String] (declared)',
            '-> Type[global/x/String] (inferred)'
        ]
    }


def test_program24():
    # fun <T> foo(): T
    # var x: A<String> = foo()
    program = tap.program24
    a = tda.TypeDependencyAnalysis(program)
    a.visit(program)
    res = to_str_dict(a.result())

    assert res == {
        '!TypeVariable[global/x/foo/A/T]': ['-> Type[String] (declared)'],
        'Declaration[global/foo/foo]': [
            '-> Type[T] (inferred)',
            '-> Type[global/foo/foo/T] (declared)'
        ],
        'Declaration[global/x]': [
            '-> TypeConInstDecl[global/x/foo/A] (declared)'
        ],
        'TypeConInstCall[global/x/foo]': [
            '-> TypeVariable[global/x/foo/T] (declared)'
        ],
        'TypeConInstDecl[global/x/foo/A]': [
            '-> !TypeVariable[global/x/foo/A/T] (declared)'
        ],
        'TypeVariable[global/x/foo/T]': [
            '-> Type[String] (declared)',
            '-> TypeConInstDecl[global/x/foo/A] (inferred)',
        ]
    }


def test_program25():
    # fun <T> foo(): A<T>
    # var x: A<String> = foo()
    program = tap.program25
    a = tda.TypeDependencyAnalysis(program)
    a.visit(program)
    res = to_str_dict(a.result())

    assert res == {
        '!TypeVariable[global/x/foo/A/T]': [
            '-> Type[String] (declared)',
        ],
        'Declaration[global/foo/foo]': [
            '-> Type[A] (inferred)',
            '-> Type[global/foo/foo/A] (declared)'
        ],
        'Declaration[global/x]': [
            '-> TypeConInstDecl[global/x/foo/A] (declared)'
        ],
        'TypeConInstCall[global/x/foo]': [
            '-> TypeVariable[global/x/foo/T] (declared)'
        ],
        'TypeConInstDecl[global/x/foo/A]': [
            '-> !TypeVariable[global/x/foo/A/T] (declared)'
        ],
        'TypeVariable[global/x/foo/T]': [
            '-> Type[String] (declared)',
            '-> !TypeVariable[global/x/foo/A/T] (inferred)'
        ]
    }


def test_program26():
    # fun <T> foo(): B<T>
    # var x: A<String> = foo()
    program = tap.program26
    a = tda.TypeDependencyAnalysis(program)
    a.visit(program)
    res = to_str_dict(a.result())

    assert res == {
        '!TypeVariable[global/x/foo/A/T]': [
            '-> Type[String] (declared)',
        ],
        'Declaration[global/foo/foo]': [
            '-> Type[B] (inferred)',
            '-> Type[global/foo/foo/B] (declared)'
        ],
        'Declaration[global/x]': [
            '-> TypeConInstDecl[global/x/foo/A] (declared)'
        ],
        'TypeConInstCall[global/x/foo]': [
            '-> TypeVariable[global/x/foo/T] (declared)'
        ],
        'TypeConInstDecl[global/x/foo/A]': [
            '-> !TypeVariable[global/x/foo/A/T] (declared)'
        ],
        'TypeVariable[global/x/foo/T]': [
            '-> Type[String] (declared)',
            '-> !TypeVariable[global/x/foo/A/T] (inferred)'
        ]

    }


def test_program27():
    # fun <T> foo(): B<T>
    # var x: A<String, String> = foo()
    program = tap.program27
    a = tda.TypeDependencyAnalysis(program)
    a.visit(program)
    res = to_str_dict(a.result())

    assert res == {
        '!TypeVariable[global/x/foo/A/T2]': [
            '-> Type[Int] (declared)',
        ],
        '!TypeVariable[global/x/foo/A/T]': [
            '-> Type[String] (declared)',
        ],
        'Declaration[global/foo/foo]': [
            '-> Type[B] (inferred)',
            '-> Type[global/foo/foo/B] (declared)'
        ],
        'Declaration[global/x]': [
            '-> TypeConInstDecl[global/x/foo/A] (declared)'
        ],
        'TypeConInstCall[global/x/foo]': [
            '-> TypeVariable[global/x/foo/T] (declared)'
        ],
        'TypeConInstDecl[global/x/foo/A]': [
            '-> !TypeVariable[global/x/foo/A/T] (declared)',
            '-> !TypeVariable[global/x/foo/A/T2] (declared)'
        ],
        'TypeVariable[global/x/foo/T]': [
            '-> Type[String] (declared)',
            '-> !TypeVariable[global/x/foo/A/T2] (inferred)'
        ]
    }


def test_program28():
    # class A
    # class B<T>(val x: A)
    # class C<T> {
    #   fun foo(): {
    #     val x: B<T> = B<T>(A())
    #   }
    # }
    program = tap.program28
    a = tda.TypeDependencyAnalysis(tap.program28)
    a.visit(program)
    type_graph = a.result()
    res = to_str_dict(type_graph)

    assert res == {
        '!TypeVariable[global/C/foo/x/B/T]': ['-> Type[T] (declared)'],
        'Declaration[global/B/f]': ['-> Type[A] (declared)'],
        'Declaration[global/C/foo/x/B/f]': ['-> Type[A] (inferred)'],
        'Declaration[global/C/foo/x]': [
            '-> TypeConInstCall[global/C/foo/x/B] (inferred)',
            '-> TypeConInstDecl[global/C/foo/x/B] (declared)',
        ],
        'TypeConInstCall[global/C/foo/x/B]': [
            '-> TypeVariable[global/C/foo/x/B/T] (declared)',
        ],
        'TypeConInstDecl[global/C/foo/x/B]': [
            '-> !TypeVariable[global/C/foo/x/B/T] (declared)'
        ],
        'TypeVariable[global/C/foo/x/B/T]': [
            '-> Type[T] (declared)',
            '-> !TypeVariable[global/C/foo/x/B/T] (inferred)',
        ]
    }

    nodes = type_graph.keys()
    decl_node = find_omittable_node("global/C/foo/x", nodes)
    type_inst_node = find_omittable_node("global/C/foo/x/B", nodes)

    assert not tda.is_combination_feasible(type_graph,
                                           (decl_node, type_inst_node))


def test_program29():
    # class A<T>
    # class B<T> (val f: A<T>)
    # val x: B<String> = new B<String>(new A<String>())
    program = tap.program29
    a = tda.TypeDependencyAnalysis(program)
    a.visit(program)
    type_graph = a.result()
    res = to_str_dict(type_graph)

    nodes = type_graph.keys()
    decl_node = find_omittable_node("global/x", nodes)
    type_inst_node1 = find_omittable_node("global/x/B", nodes)
    type_inst_node2 = find_omittable_node("global/x/B/f/A", nodes)

    tg = copy(type_graph)
    assert not tda.is_combination_feasible(
        tg, (decl_node, type_inst_node1, type_inst_node2))
    tg = copy(type_graph)
    assert tda.is_combination_feasible(
        tg, (type_inst_node1, type_inst_node2)
    )
