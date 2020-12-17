import pytest
from src.graph_utils import *


GRAPH = {((), None): {(('global', 'A', 'bar'), 'y')},
         (('global', 'A'), 'x'): {((), None)},
         (('global', 'A', 'bar'), 'arg'): {((), None)},
         (('global', 'A', 'bar'), 'y'): {(('global', 'A', 'buz'), 'k')},
         (('global', 'A', 'bar'), 'z'): set(),
         (('global', 'A', 'foo'), 'q'): {(('global', 'A', 'bar'), 'z'),
                                         (('global', 'A', 'foo'), 'x')},
         (('global', 'A', 'foo'), 'x'): set(),
         (('global', 'A', 'foo'), 'y'): {(('global', 'A', 'bar'), 'arg')},
         (('global', 'A', 'foo'), 'z'): {(('global', 'A', 'foo'), 'q')},
         (('global', 'A', 'buz'), 'k'): set()
}
NONE = ((), None)
X = (('global', 'A'), 'x')
BAR_Y = (('global', 'A', 'bar'), 'y')
BAR_Z = (('global', 'A', 'bar'), 'z')
BAR_ARG = (('global', 'A', 'bar'), 'arg')
FOO_Q = (('global', 'A', 'foo'), 'q')
FOO_X = (('global', 'A', 'foo'), 'x')
FOO_Y = (('global', 'A', 'foo'), 'y')
FOO_Z = (('global', 'A', 'foo'), 'z')
BUZ_K = (('global', 'A', 'buz'), 'k')

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


def test_none_reachable():
    assert none_reachable(GRAPH, X)
    assert none_reachable(GRAPH, FOO_Y)
    assert none_reachable(GRAPH, BAR_Y)
    assert none_reachable(GRAPH, BUZ_K)
    assert none_reachable(GRAPH, BUZ_K)
    assert not none_reachable(GRAPH, FOO_Q)
    assert not none_reachable(GRAPH, BAR_Z)


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
