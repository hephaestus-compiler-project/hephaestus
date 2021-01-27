# pylint: disable=inherit-non-class,pointless-statement
from typing import Tuple, NamedTuple, List
from collections import defaultdict

import src.graph_utils as gu
import src.ir.type_utils as tu
import src.utils as ut
from src.ir import ast
from src.ir import types as tp
from src.ir.visitors import DefaultVisitor
from src.transformations.base import change_namespace
from src.analysis.use_analysis import UseAnalysis, GNode, get_decl


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

    def _get_func_namespace(self, func: str, receiver: ast.Expr = None):
        def get_filtered_or_all(namespace, namespaces):
            res = []
            for ns in namespaces:
                if ut.prefix_lst(namespace, ns):
                    res.append(ns)
            if len(res) == 0:
                return namespaces
            return res

        funcs = self.program.context.get_namespaces_decls(
            self._namespace, func, 'funcs')

        # Not a user defined function
        if len(funcs) == 0:
            return None

        if len(funcs) == 1:
            namespace, _ = list(funcs)[0]
            return [namespace]

        # Handle receiver
        all_namespaces = [func[0] for func in funcs]
        if isinstance(receiver, ast.Variable):
            # Find the type of the source of the variable
            gnode = GNode(self._namespace, receiver.name)
            sources = gu.find_sources(self._use_graph, gnode)
            if len(sources) > 1:
                return all_namespaces
            source = sources[0]
            _, source_decl = get_decl(self.program.context,
                                      self._namespace, source.name)
            source_type = source_decl.get_type()
            if isinstance(source_type, tp.Builtin):
                return all_namespaces
            # Get the namespace of source_type
            # It is not possible to have multiple classes with the same name
            namespace, _ = list(self.program.context.get_namespaces_decls(
                self._namespace, source_type.name, 'classes'))[0]
            return get_filtered_or_all(namespace, all_namespaces)
        if isinstance(receiver, ast.New):
            pass
        if isinstance(receiver, ast.FunctionCall):
            pass
        if isinstance(receiver, ast.FieldAccess):
            pass
        return all_namespaces

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
            for ns in callee_ns:
                self._call_graph[CNode(self._namespace)].add(CNode(ns))
                self._calls[CNode(ns)].add(node)
