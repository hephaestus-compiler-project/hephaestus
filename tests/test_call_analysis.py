from copy import deepcopy

from src.ir import ast
from src.analysis.call_analysis import CallAnalysis, CNode
from tests.resources import program9


def str2node(string):
    segs = tuple(string.split("/"))
    return CNode(segs)


def assert_nodes(nodes, expected_nodes):
    assert len(nodes) == len(expected_nodes)
    assert (nodes - expected_nodes) == set()


def assert_nodes_len(nodes, length):
    assert len(nodes) == length


def test_program9():
    ca = CallAnalysis(program9.program)
    cg, calls = ca.result()

    foo = str2node("global/foo")
    bar = str2node("global/bar")

    assert_nodes(cg[foo], set())
    assert_nodes_len(calls[foo], 1)
    assert_nodes(cg[bar], {foo})
    assert_nodes_len(calls[bar], 0)
