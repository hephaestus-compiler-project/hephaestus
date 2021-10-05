from copy import deepcopy

from src.ir import ast, builtins
from src.analysis.use_analysis import UseAnalysis, NONE_NODE, GNode
from tests.resources import (
    program1, program2, program3, program4, program5, program6, program7,
    program8)


def str2node(string):
    segs = tuple(string.split("/"))
    return GNode(segs[:-1], segs[-1])


def assert_nodes(nodes, expected_nodes):
    assert len(nodes) == len(expected_nodes)
    assert (nodes - expected_nodes) == set()


def test_program1():
    ua = UseAnalysis(program1.program)
    ua.visit(program1.a_cls)
    ug = ua.result()

    field_x = str2node("global/A/x")
    bar_ret = str2node("global/A/bar/__RET__")
    bar_arg = str2node("global/A/bar/arg")
    bar_y = str2node("global/A/bar/y")
    bar_z = str2node("global/A/bar/z")
    buz_ret = str2node("global/A/buz/__RET__")
    foo_ret = str2node("global/A/foo/__RET__")
    foo_q = str2node("global/A/foo/q")
    foo_x = str2node("global/A/foo/x")
    foo_y = str2node("global/A/foo/y")
    foo_z = str2node("global/A/foo/z")
    spam_ret = str2node("global/A/spam/__RET__")

    assert_nodes(ug[field_x], {NONE_NODE, buz_ret})
    assert_nodes(ug[bar_ret], {foo_ret, NONE_NODE})
    assert_nodes(ug[bar_arg], {NONE_NODE})
    assert_nodes(ug[bar_y], set())
    assert_nodes(ug[bar_z], set())
    assert_nodes(ug[buz_ret], set())
    assert_nodes(ug[foo_ret], set())
    assert_nodes(ug[foo_q], {foo_x, bar_z})
    assert_nodes(ug[foo_x], set())
    assert_nodes(ug[foo_y], {bar_arg})
    assert_nodes(ug[foo_z], {foo_q})
    assert_nodes(ug[spam_ret], {NONE_NODE})
    assert_nodes(ug[NONE_NODE], {bar_y})


def test_program1_foo():
    ua = UseAnalysis(program1.program)
    ua.set_namespace(("global", "A"))
    ua.visit(program1.foo_func)
    ug = ua.result()

    field_x = str2node("global/A/x")
    bar_ret = str2node("global/A/bar/__RET__")
    bar_arg = str2node("global/A/bar/arg")
    bar_y = str2node("global/A/bar/y")
    bar_z = str2node("global/A/bar/z")
    buz_ret = str2node("global/A/buz/__RET__")
    foo_ret = str2node("global/A/foo/__RET__")
    foo_q = str2node("global/A/foo/q")
    foo_x = str2node("global/A/foo/x")
    foo_y = str2node("global/A/foo/y")
    foo_z = str2node("global/A/foo/z")
    spam_ret = str2node("global/A/spam/__RET__")

    assert_nodes(ug[foo_ret], set())
    assert_nodes(ug[foo_q], {foo_x, bar_z})
    assert_nodes(ug[foo_x], set())
    assert_nodes(ug[foo_y], {bar_arg})
    assert_nodes(ug[foo_z], {foo_q})


def test_program2():
    ua = UseAnalysis(program2.program)
    ua.visit(program2.bam_cls)
    ug = ua.result()

    x_field = str2node("global/Bam/x")
    getx_ret = str2node("global/Bam/getX/__RET__")
    getx_z = str2node("global/Bam/getX/z")

    assert_nodes(ug[x_field], {getx_ret})
    assert_nodes(ug[getx_ret], set())
    assert_nodes(ug[getx_z], set())


def test_program3():
    ua = UseAnalysis(program3.program)
    ua.visit(program3.cls)
    ug = ua.result()

    foo_x = str2node("global/A/foo/x")
    foo_y = str2node("global/A/foo/y")
    foo_z = str2node("global/A/foo/z")
    bar_x = str2node("global/A/bar/x")
    bar_y = str2node("global/A/bar/y")
    bar_z = str2node("global/A/bar/z")

    assert_nodes(ug[foo_x], {foo_z})
    assert_nodes(ug[foo_z], {NONE_NODE})
    assert_nodes(ug[foo_y], {NONE_NODE})
    assert_nodes(ug[bar_x], {bar_z})
    assert_nodes(ug[bar_z], set())
    assert_nodes(ug[bar_y], {NONE_NODE})


def test_program4():
    ua = UseAnalysis(program4.program)
    ua.visit(program4.cls)
    ug = ua.result()

    field_x = str2node("global/A/x")
    foo_ret = str2node("global/A/foo/__RET__")
    bar_ret = str2node("global/A/foo/bar/__RET__")

    assert_nodes(ug[field_x], {bar_ret})
    assert_nodes(ug[bar_ret], {foo_ret})
    assert_nodes(ug[foo_ret], set())
    assert_nodes(ug[NONE_NODE], set())


def test_program5():
    ua = UseAnalysis(program5.program)
    ua.visit(program5.cls)
    ug = ua.result()

    field_x = str2node("global/A/x")
    foo_y = str2node("global/A/foo/y")
    foo_ret = str2node("global/A/foo/__RET__")
    bar_y = str2node("global/A/bar/y")
    bar_z = str2node("global/A/bar/z")
    baz_ret = str2node("global/A/bar/baz/__RET__")
    bar_ret = str2node("global/A/bar/__RET__")
    quz_y = str2node("global/A/quz/y")
    quz_ret = str2node("global/A/quz/__RET__")

    assert_nodes(ug[field_x], {baz_ret})
    assert_nodes(ug[foo_y], {foo_ret})
    assert_nodes(ug[bar_y], set())
    assert_nodes(ug[baz_ret], {bar_z})
    assert_nodes(ug[bar_z], {foo_y})
    assert_nodes(ug[foo_ret], {quz_y})
    assert_nodes(ug[quz_ret], {bar_ret, NONE_NODE})
    assert_nodes(ug[quz_y], set())
    assert_nodes(ug[NONE_NODE], set())


def test_program5_if():
    # In program 5 we perform the following modification:
    # return quz(foo(z)) => quz(if (true) foo(z) else "bar")
    program = deepcopy(program5.program)
    bar_fun = program.context.get_decl(ast.GLOBAL_NAMESPACE + ("A",), "bar")
    bar_fun.body.body[-1].args[0] = ast.Conditional(
        ast.BooleanConstant("true"),
        ast.FunctionCall("foo", [ast.Variable("z")]),
        ast.StringConstant("bar"),
        builtins.String,
    )
    ua = UseAnalysis(program)
    ua.visit(program.context.get_decl(ast.GLOBAL_NAMESPACE, "A"))
    ug = ua.result()

    field_x = str2node("global/A/x")
    foo_y = str2node("global/A/foo/y")
    foo_ret = str2node("global/A/foo/__RET__")
    bar_y = str2node("global/A/bar/y")
    bar_z = str2node("global/A/bar/z")
    baz_ret = str2node("global/A/bar/baz/__RET__")
    bar_ret = str2node("global/A/bar/__RET__")
    quz_y = str2node("global/A/quz/y")
    quz_ret = str2node("global/A/quz/__RET__")

    assert_nodes(ug[field_x], {baz_ret})
    assert_nodes(ug[foo_y], {foo_ret})
    assert_nodes(ug[bar_y], set())
    assert_nodes(ug[baz_ret], {bar_z})
    assert_nodes(ug[bar_z], {foo_y})
    assert_nodes(ug[foo_ret], {NONE_NODE})
    assert_nodes(ug[quz_ret], {bar_ret, NONE_NODE})
    assert_nodes(ug[quz_y], set())
    assert_nodes(ug[NONE_NODE], {quz_y})


def test_program5_if2():
    # In program 5 we perform the following modification:
    # return quz(foo(z)) => quz(foo(if (true) z else z))
    program = deepcopy(program5.program)

    bar_fun = program.context.get_decl(ast.GLOBAL_NAMESPACE + ("A",), "bar")
    bar_fun.body.body[-1].args[0].args[0] = ast.Conditional(
        ast.BooleanConstant("true"),
        ast.Variable("z"),
        ast.Variable("z"),
        builtins.Any
    )
    ua = UseAnalysis(program)
    ua.visit(program.context.get_decl(ast.GLOBAL_NAMESPACE, "A"))
    ug = ua.result()

    field_x = str2node("global/A/x")
    foo_y = str2node("global/A/foo/y")
    foo_ret = str2node("global/A/foo/__RET__")
    bar_y = str2node("global/A/bar/y")
    bar_z = str2node("global/A/bar/z")
    baz_ret = str2node("global/A/bar/baz/__RET__")
    bar_ret = str2node("global/A/bar/__RET__")
    quz_y = str2node("global/A/quz/y")
    quz_ret = str2node("global/A/quz/__RET__")

    assert_nodes(ug[field_x], {baz_ret})
    assert_nodes(ug[foo_y], {foo_ret})
    assert_nodes(ug[bar_y], set())
    assert_nodes(ug[baz_ret], {bar_z})
    assert_nodes(ug[bar_z], {NONE_NODE})
    assert_nodes(ug[foo_ret], {quz_y})
    assert_nodes(ug[quz_ret], {bar_ret, NONE_NODE})
    assert_nodes(ug[quz_y], set())
    assert_nodes(ug[NONE_NODE], {foo_y})


def test_program5_varargs():
    program = deepcopy(program5.program)
    quz_fun = program.context.get_decl(ast.GLOBAL_NAMESPACE + ("A",), "quz")
    quz_fun.params[0].vararg = True


    bar_fun = program.context.get_decl(ast.GLOBAL_NAMESPACE + ("A",), "bar")
    expr = ast.IntegerConstant(1, builtins.Integer)
    bar_fun.body.body[-1].args.insert(0, expr)

    ua = UseAnalysis(program)
    ua.visit(program.context.get_decl(ast.GLOBAL_NAMESPACE, "A"))
    ug = ua.result()

    field_x = str2node("global/A/x")
    foo_y = str2node("global/A/foo/y")
    foo_ret = str2node("global/A/foo/__RET__")
    bar_y = str2node("global/A/bar/y")
    bar_z = str2node("global/A/bar/z")
    baz_ret = str2node("global/A/bar/baz/__RET__")
    bar_ret = str2node("global/A/bar/__RET__")
    quz_y = str2node("global/A/quz/y")
    quz_ret = str2node("global/A/quz/__RET__")

    assert_nodes(ug[field_x], {baz_ret})
    assert_nodes(ug[foo_y], {foo_ret})
    assert_nodes(ug[bar_y], set())
    assert_nodes(ug[baz_ret], {bar_z})
    assert_nodes(ug[bar_z], {foo_y})
    assert_nodes(ug[foo_ret], {quz_y})
    assert_nodes(ug[quz_ret], {bar_ret, NONE_NODE})
    assert_nodes(ug[quz_y], set())
    assert_nodes(ug[NONE_NODE],{quz_y})


def test_program5_varargs2():
    program = deepcopy(program5.program)
    quz_fun = program.context.get_decl(ast.GLOBAL_NAMESPACE + ("A",), "quz")
    quz_fun.params[0].vararg = True

    bar_fun = program.context.get_decl(ast.GLOBAL_NAMESPACE + ("A",), "bar")
    bar_fun.body.body[-1].args.insert(0, deepcopy(
        bar_fun.body.body[-1].args[0]))

    ua = UseAnalysis(program)
    ua.visit(program.context.get_decl(ast.GLOBAL_NAMESPACE, "A"))
    ug = ua.result()

    field_x = str2node("global/A/x")
    foo_y = str2node("global/A/foo/y")
    foo_ret = str2node("global/A/foo/__RET__")
    bar_y = str2node("global/A/bar/y")
    bar_z = str2node("global/A/bar/z")
    baz_ret = str2node("global/A/bar/baz/__RET__")
    bar_ret = str2node("global/A/bar/__RET__")
    quz_y = str2node("global/A/quz/y")
    quz_ret = str2node("global/A/quz/__RET__")

    assert_nodes(ug[field_x], {baz_ret})
    assert_nodes(ug[foo_y], {foo_ret})
    assert_nodes(ug[bar_y], set())
    assert_nodes(ug[baz_ret], {bar_z})
    assert_nodes(ug[bar_z], {foo_y})
    assert_nodes(ug[foo_ret], {quz_y})
    assert_nodes(ug[quz_ret], {bar_ret, NONE_NODE})
    assert_nodes(ug[quz_y], set())
    assert_nodes(ug[NONE_NODE], set())


def test_program6():
    ua = UseAnalysis(program6.program)
    ua.visit(program6.cls)
    ug = ua.result()

    field_x = str2node("global/A/x")
    bar_y = str2node("global/A/bar/y")
    bar_ret = str2node("global/A/bar/__RET__")
    baz_ret = str2node("global/A/baz/__RET__")

    assert_nodes(ug[field_x], {bar_y})
    assert_nodes(ug[bar_y], {NONE_NODE})
    assert_nodes(ug[bar_ret], {NONE_NODE})
    assert_nodes(ug[baz_ret], {NONE_NODE})
    assert_nodes(ug[NONE_NODE], set())


def test_program7():
    ua = UseAnalysis(program7.program)
    ua.visit(program7.cls)
    ug = ua.result()

    foo_x = str2node("global/A/foo/x")
    foo_ret = str2node("global/A/foo/__RET__")
    bar_ret = str2node("global/A/bar/__RET__")

    assert_nodes(ug[foo_x], {foo_ret, NONE_NODE})
    assert_nodes(ug[foo_ret], {bar_ret})
    assert_nodes(ug[bar_ret], set())
    assert_nodes(ug[NONE_NODE], set())


def test_program8():
    ua = UseAnalysis(program8.program)
    ua.visit(program8.cls)
    ug = ua.result()

    foo_x = str2node("global/A/foo/x")
    foo_ret = str2node("global/A/foo/__RET__")

    assert_nodes(ug[foo_x], {foo_ret, NONE_NODE})
    assert_nodes(ug[NONE_NODE], set())
