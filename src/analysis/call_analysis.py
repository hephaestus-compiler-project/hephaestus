# pylint: disable=inherit-non-class,pointless-statement,expression-not-assigned
from typing import Tuple, NamedTuple
from collections import defaultdict

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


def get_gnode_type(gnode, namespace, context):
    # TODO Do we need to add limit?
    decl = get_decl(context, namespace, gnode.name)
    if decl:
        return decl[1].get_type()
    return None


def find_gnode_type(gnode, namespace, context, use_graph):
    """Find the type of a gnode

    If gnode is a declaration return its type, otherwise return the type
    of an adjacent node.
    """
    def get_adj(gnode):
        return [v for v, e in use_graph.items if gnode in e]

    gnode_type = get_gnode_type(gnode, namespace, context)
    if gnode_type:
        return gnode_type

    visited = {v: False for v in use_graph.keys()}

    queue = get_adj(gnode)

    while len(queue) > 0:
        adjacent = queue.pop(0)
        if not visited[adjacent]:
            visited[adjacent] = True
            adj_type = get_gnode_type(adjacent, namespace, context)
            if adj_type:
                return adj_type
            queue.extend(get_adj(adjacent))
    return None


def namespaces_reduction(namespace, all_namespaces):
    """Try to find filter out namespaces that cannot be called.
    """
    declared_inside_namespace = [ns for ns in all_namespaces
                                 if ut.prefix_lst(namespace, ns)]
    if len(declared_inside_namespace) > 0:
        return declared_inside_namespace
    tmp_namespace = namespace
    while len(tmp_namespace) > 0:
        tmp_namespace = tmp_namespace[:-1]
        same_prefix_ns = [ns for ns in all_namespaces
                          if ut.prefix_lst(tmp_namespace, ns)]
        if len(same_prefix_ns) > 0:
            # Consider we having those functions:
            # [('global', 'First', 'foo'), ('global', 'foo')]
            # and we have called foo from ('global', 'bar')
            # then the function that will be called is ('global', 'foo')
            return list(filter(
                lambda x: len(x) <= len(namespace),
                same_prefix_ns))
    return all_namespaces


class CallAnalysis(DefaultVisitor):
    """Get the call graph of a program.

    Currently we only handle simple function calls.
    For example we don't support multi functions.
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

        all_namespaces = [func[0] for func in funcs]

        # There are multiple functions defined with the same name.
        # Select the namespace that is closer to current namespace.
        if receiver is None:
            return namespaces_reduction(self._namespace, all_namespaces)

        # Handle receiver
        if isinstance(receiver, ast.Variable):
            gnode = GNode(self._namespace, receiver.name)
            gnode_type = find_gnode_type(
                gnode, self._namespace, self.program.context, self._use_graph)
            if isinstance(gnode_type, tp.Builtin) or gnode_type is None:
                return all_namespaces
            # Get the namespace of source_type
            # It is not possible to have multiple classes with the same name
            namespace, _ = list(self.program.context.get_namespaces_decls(
                self._namespace, gnode_type.name, 'classes'))[0]
            return get_filtered_or_all(namespace, all_namespaces)
        if isinstance(receiver, ast.New):
            # There should be only one class declaration per name.
            new_namespace, _ = list(self.program.context.get_namespaces_decls(
                self._namespace,
                receiver.class_type.name,
                'classes'))[0]
            return namespaces_reduction(new_namespace, all_namespaces)
        if isinstance(receiver, ast.FunctionCall):
            if receiver.receiver:
                # TODO
                return all_namespaces
            # Possible Function declaration
            function_decls = self.program.context.get_namespaces_decls(
                self._namespace, receiver.func, 'funcs')
            function_namespaces = list(zip(*function_decls))[0]
            # FIXME if it has a receiver we must be more precise
            function_namespace = namespaces_reduction(
                self._namespace, all_namespaces)
            # We cannot find the exact function declaration
            if len(function_namespace) != 1:
                return all_namespaces
            function_namespace = function_namespace[0]
            function_decl = self.program.context.get_decl(
                    function_namespace[:-1], function_namespace[-1])
            function_type = function_decl.inferred_type
            if isinstance(function_type, tp.Builtin) or function_type is None:
                return all_namespaces
            # It is not possible to have multiple classes with the same name
            namespace, _ = list(self.program.context.get_namespaces_decls(
                self._namespace, function_type.name, 'classes'))[0]
            return get_filtered_or_all(namespace, all_namespaces)
        # TODO
        # if isinstance(receiver, ast.FieldAccess):
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
