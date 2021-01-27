# pylint: disable=inherit-non-class,pointless-statement
from typing import Tuple, NamedTuple, List
from collections import defaultdict

from src.ir import ast
from src.ir.visitors import DefaultVisitor
from src.transformations.base import change_namespace


class CNode(NamedTuple):
    namespace: Tuple[str, ...]

    def __str__(self):
        return "/".join(self.namespace)

    def is_none(self):
        return self.namespace is None

    def __repr__(self):
        return self.__str__()


class CallAnalysis(DefaultVisitor):
    """Get the call graph of a program.

    Currently we only handle simple function calls.

    Graphs:
        * _call_graph: caller => callee
        * _calls:      callee => call sites (FunctionCall objects)

    To employ CallAnalysis use the following instructions.

    analysis = CallAnalysis(self.program)
    use_graph = analysis.result()
    """
    def __init__(self, program):
        # The type of each node is: CNode
        self._call_graph = defaultdict(set)  # namespace => [CNode]
        # All call sites of a function
        self._calls = defaultdict(set)  # namespace => [CNode]
        self._namespace = ast.GLOBAL_NAMESPACE
        self.program = program
        self.visit(self.program)

    def result(self):
        return self._call_graph, self._calls

    def _get_func_namespace(self, func: str, receiver: str = None):
        funcs = self.program.context.get_namespaces_decls(
            self._namespace, func, 'funcs')
        # TODO handle receiver
        namespace, _ = list(funcs)[0]
        return namespace

    @change_namespace
    def visit_class_decl(self, node):
        super().visit_class_decl(node)

    @change_namespace
    def visit_func_decl(self, node):
        self._call_graph[CNode(self._namespace)]
        self._calls[CNode(self._namespace)]
        super().visit_func_decl(node)

    def visit_func_call(self, node):
        callee_ns = self._get_func_namespace(node.func, node.receiver)
        self._call_graph[CNode(self._namespace)].add(CNode(callee_ns))
        self._calls[CNode(callee_ns)].add(node)
