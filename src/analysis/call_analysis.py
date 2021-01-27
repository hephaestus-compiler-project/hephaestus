# pylint: disable=inherit-non-class,pointless-statement
from typing import Tuple, NamedTuple, List
from collections import defaultdict

from src.ir import ast
from src.ir.visitors import DefaultVisitor
from src.transformations.base import change_namespace
from src.analysis.use_analysis import UseAnalysis


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
    We only support user defined functions.
    In case a function is not declared in the context, we simple ignore it.

    Graphs:
        * _call_graph: caller => callee
        * _calls:      callee => call sites (FunctionCall objects)

    To employ CallAnalysis use the following instructions.

    analysis = CallAnalysis(self.program)
    call_graph, calls = analysis.result()
    """
    def __init__(self, program):
        # The type of each node is: CNode
        self._call_graph = defaultdict(set)  # namespace => [CNode]
        # All call sites of a function
        self._calls = defaultdict(set)  # namespace => [FunctionCall]
        self._namespace = ast.GLOBAL_NAMESPACE
        # We compute the use_graph for each top level declaration.
        self._use_graph = None
        self.program = program
        self.visit(self.program)

    def result(self):
        return self._call_graph, self._calls

    def _get_func_namespace(self, func: str, receiver: str = None):
        funcs = self.program.context.get_namespaces_decls(
            self._namespace, func, 'funcs')
        if len(funcs) == 0:
            return None
        # TODO handle receiver
        namespace, _ = list(funcs)[0]
        return namespace

    def _compute_use_graph(self, node):
        if len(self._namespace) == 2:
            analysis = UseAnalysis(self.program)
            analysis.visit(node)
            self._use_graph = analysis.result()

    @change_namespace
    def visit_class_decl(self, node):
        self._compute_use_graph(node)
        super().visit_class_decl(node)

    @change_namespace
    def visit_func_decl(self, node):
        self._compute_use_graph(node)
        self._call_graph[CNode(self._namespace)]
        self._calls[CNode(self._namespace)]
        super().visit_func_decl(node)

    def visit_func_call(self, node):
        super().visit_func_call(node)
        callee_ns = self._get_func_namespace(node.func, node.receiver)
        if callee_ns:
            self._call_graph[CNode(self._namespace)].add(CNode(callee_ns))
            self._calls[CNode(callee_ns)].add(node)
