from src.ir import ast
from src.analysis.use_analysis import UseAnalysis, NONE_NODE, GNode
from tests.resources import program1


def str2node(string):
    segs = tuple(string.split("/"))
    return GNode(segs[:-1], segs[-1])


def assert_nodes(nodes, expected_nodes):
    assert len(nodes) == len(expected_nodes)
    assert (nodes - expected_nodes) == set()

def test_class_a():
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
