import pytest
from src.analysis.use_analysis import GNode, NONE_NODE
from src.graph_utils import *


NONE = NONE_NODE
X = GNode(('global', 'A'), 'x')
BAR_Y = GNode(('global', 'A', 'bar'), 'y')
BAR_Z = GNode(('global', 'A', 'bar'), 'z')
BAR_ARG = GNode(('global', 'A', 'bar'), 'arg')
FOO_Q = GNode(('global', 'A', 'foo'), 'q')
FOO_X = GNode(('global', 'A', 'foo'), 'x')
FOO_Y = GNode(('global', 'A', 'foo'), 'y')
FOO_Z = GNode(('global', 'A', 'foo'), 'z')
BUZ_K = GNode(('global', 'A', 'buz'), 'k')
GRAPH = {NONE: {GNode(('global', 'A', 'bar'), 'y')},
         X: {NONE},
         BAR_ARG: {NONE},
         BAR_Y: {BUZ_K},
         BAR_Z: set(),
         FOO_Q: {BAR_Z, FOO_X},
         FOO_X: set(),
         FOO_Y: {BAR_ARG},
         FOO_Z: {FOO_Q},
         BUZ_K: set()
}

N0 = "N0"
N1 = "N1"
N2 = "N2"
N3 = "N3"
N4 = "N4"
GRAPH2 = {N0: {N1},
          N1: {N2},
          N2: {N3},
          N4: {N3},
          N3: {}
}
#             N4
#               \
#                -> N3
#               /
# N0 -> N1 -> N2
GRAPH3 = {X: {NONE}}


def test_reachable():
    assert reachable(GRAPH, X, X)
    assert reachable(GRAPH, X, NONE)
    assert reachable(GRAPH, X, BAR_Y)
    assert reachable(GRAPH, BAR_ARG, NONE)
    assert reachable(GRAPH, FOO_Q, FOO_X)
    assert reachable(GRAPH, FOO_Q, BAR_Z)
    assert reachable(GRAPH, FOO_Y, BAR_ARG)
    assert reachable(GRAPH, FOO_Y, NONE)
    assert reachable(GRAPH, FOO_Z, FOO_Q)
    assert reachable(GRAPH, FOO_Q, BAR_Z)
    assert not reachable(GRAPH, BAR_Y, NONE)
    assert not reachable(GRAPH, BAR_Y, X)
    assert not reachable(GRAPH, BUZ_K, NONE)
    assert not reachable(GRAPH, BAR_Z, FOO_Q)
    assert not reachable(GRAPH, BAR_Z, FOO_Z)
    assert not reachable(GRAPH, BAR_Z, FOO_X)
    assert not reachable(GRAPH, BAR_ARG, FOO_Z)
    assert reachable(GRAPH2, N0, N1)
    assert reachable(GRAPH2, N0, N3)
    assert not reachable(GRAPH2, N3, N0)
    assert not reachable(GRAPH2, N3, N2)
    assert not reachable(GRAPH2, N3, N4)
    assert not reachable(GRAPH2, N4, N2)
    assert not reachable(GRAPH2, N0, N4)
    assert not reachable(GRAPH3, X, BAR_ARG)


def test_bi_reachable():
    assert bi_reachable(GRAPH, X, X)
    assert bi_reachable(GRAPH, X, NONE)
    assert bi_reachable(GRAPH, X, BAR_Y)
    assert bi_reachable(GRAPH, BAR_ARG, NONE)
    assert bi_reachable(GRAPH, FOO_Q, FOO_X)
    assert bi_reachable(GRAPH, FOO_Q, BAR_Z)
    assert bi_reachable(GRAPH, FOO_Y, BAR_ARG)
    assert bi_reachable(GRAPH, FOO_Y, NONE)
    assert bi_reachable(GRAPH, FOO_Z, FOO_Q)
    assert bi_reachable(GRAPH, FOO_Q, BAR_Z)
    assert bi_reachable(GRAPH, BAR_Y, NONE)
    assert bi_reachable(GRAPH, BAR_Y, X)
    assert bi_reachable(GRAPH, BUZ_K, NONE)
    assert bi_reachable(GRAPH, BAR_Z, FOO_Q)
    assert bi_reachable(GRAPH, BAR_Z, FOO_Z)
    assert not bi_reachable(GRAPH, BAR_Z, FOO_X)
    assert not bi_reachable(GRAPH, BAR_ARG, FOO_Z)
    assert bi_reachable(GRAPH2, N0, N1)
    assert bi_reachable(GRAPH2, N0, N3)
    assert bi_reachable(GRAPH2, N3, N0)
    assert bi_reachable(GRAPH2, N3, N2)
    assert bi_reachable(GRAPH2, N3, N4)
    assert not bi_reachable(GRAPH2, N4, N2)
    assert not bi_reachable(GRAPH2, N0, N4)
    assert not bi_reachable(GRAPH3, X, BAR_ARG)


def test_none_reachable():
    assert none_reachable(GRAPH, X)
    assert none_reachable(GRAPH, FOO_Y)
    assert none_reachable(GRAPH, BAR_Y)
    assert none_reachable(GRAPH, BUZ_K)
    assert none_reachable(GRAPH, BUZ_K)
    assert not none_reachable(GRAPH, FOO_Q)
    assert not none_reachable(GRAPH, BAR_Z)


def test_connected():
    assert connected(GRAPH, X, X)
    assert connected(GRAPH, X, NONE)
    assert connected(GRAPH, X, BAR_Y)
    assert connected(GRAPH, BAR_ARG, NONE)
    assert connected(GRAPH, FOO_Q, FOO_X)
    assert connected(GRAPH, FOO_Q, BAR_Z)
    assert connected(GRAPH, FOO_Y, BAR_ARG)
    assert connected(GRAPH, FOO_Y, NONE)
    assert connected(GRAPH, FOO_Z, FOO_Q)
    assert connected(GRAPH, FOO_Q, BAR_Z)
    assert connected(GRAPH, BAR_Y, NONE)
    assert connected(GRAPH, BAR_Y, X)
    assert connected(GRAPH, BUZ_K, NONE)
    assert connected(GRAPH, BAR_Z, FOO_Q)
    assert connected(GRAPH, BAR_Z, FOO_Z)
    assert connected(GRAPH, BAR_Z, FOO_X)
    assert not connected(GRAPH, BAR_ARG, FOO_Z)
    assert connected(GRAPH2, N0, N1)
    assert connected(GRAPH2, N0, N3)
    assert connected(GRAPH2, N3, N0)
    assert connected(GRAPH2, N3, N2)
    assert connected(GRAPH2, N3, N4)
    assert connected(GRAPH2, N4, N2)
    assert connected(GRAPH2, N0, N4)
    assert not connected(GRAPH3, X, BAR_ARG)


def test_none_connected():
    assert none_connected(GRAPH, X)
    assert none_connected(GRAPH, FOO_Y)
    assert none_connected(GRAPH, BAR_Y)
    assert none_connected(GRAPH, BUZ_K)
    assert none_connected(GRAPH, BUZ_K)
    assert not none_connected(GRAPH, FOO_Q)
    assert not none_connected(GRAPH, BAR_Z)


def compare_lists(a, b):
    return sorted(a) == sorted(b)


def test_find_all_paths():
    assert compare_lists(find_all_paths(GRAPH, BAR_Z), [[BAR_Z]])
    assert compare_lists(find_all_paths(GRAPH, FOO_Q),
            [
                [FOO_Q],
                [FOO_Q, BAR_Z],
                [FOO_Q, FOO_X]
            ])
    assert compare_lists(find_all_paths(GRAPH, FOO_Z),
            [
                [FOO_Z],
                [FOO_Z, FOO_Q],
                [FOO_Z, FOO_Q, BAR_Z],
                [FOO_Z, FOO_Q, FOO_X]
            ])


def test_find_longest_paths():
    assert find_longest_paths(GRAPH, BAR_Z) == [[BAR_Z]]
    assert compare_lists(find_longest_paths(GRAPH, FOO_Q),
            [
                [FOO_Q, BAR_Z],
                [FOO_Q, FOO_X]
            ])
    assert compare_lists(find_longest_paths(GRAPH, FOO_Z),
            [
                [FOO_Z, FOO_Q, BAR_Z],
                [FOO_Z, FOO_Q, FOO_X]
            ])


def test_find_all_reachable():
    assert find_all_reachable(GRAPH, BAR_Z) == {BAR_Z}
    assert find_all_reachable(GRAPH, FOO_Q) == {FOO_Q, BAR_Z, FOO_X}
    assert find_all_reachable(GRAPH, FOO_Z) == {FOO_Z, FOO_Q, BAR_Z, FOO_X}


def test_find_all_bi_reachable():
    assert find_all_bi_reachable(GRAPH, BAR_Z) == {BAR_Z, FOO_Q, FOO_Z}
    assert find_all_bi_reachable(GRAPH, FOO_Q) == {BAR_Z, FOO_Q, FOO_Z, FOO_X}
    assert find_all_bi_reachable(GRAPH, FOO_Z) == {BAR_Z, FOO_Q, FOO_Z, FOO_X}


def test_find_all_connected():
    assert find_all_connected(GRAPH, BAR_Z) == {BAR_Z, FOO_Q, FOO_Z, FOO_X}
    assert find_all_connected(GRAPH, FOO_Q) == {BAR_Z, FOO_Q, FOO_Z, FOO_X}
    assert find_all_connected(GRAPH, FOO_Z) == {BAR_Z, FOO_Q, FOO_Z, FOO_X}
    assert find_all_connected(GRAPH2, N0) == {N0, N1, N2, N3, N4}


def test_find_sources():
    assert find_sources(GRAPH2, N0) == [N0]
    assert find_sources(GRAPH2, N1) == [N0]
    assert find_sources(GRAPH2, N2) == [N0]
    assert find_sources(GRAPH2, N3) == [N4, N0]
    assert find_sources(GRAPH2, N4) == [N4]
