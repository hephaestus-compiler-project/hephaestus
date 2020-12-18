from typing import Tuple
from collections import defaultdict

from src import graph_utils as gu
from src.ir import ast
from src.ir.visitors import DefaultVisitor
from src.transformations.base import change_namespace


def get_decl(context, namespace, decl_name: str, limit=None) -> Tuple[str, ast.Declaration]:
    """
    We search the context for a declaration with the given name (`decl_name`).

    The search begins from the given namespace `namespace` up to the namespace
    given by `limit`.
    """
    def stop_cond(ns):
        # If 'limit' is provided, we search the given declaration 'node'
        # up to a certain namespace.
        return (len(ns)
                if limit is None
                else any(limit == ns[:i]
                         for i in range(1, len(limit) + 1)))

    while stop_cond(namespace):
        decls = context.get_declarations(namespace, True)
        decl = decls.get(decl_name)
        if decl:
            return namespace, decl
        namespace = namespace[:-1]
    return None


class GNode(gu.Node):

    def __init__(self, namespace, name):
        self.namespace: Tuple[str, ...] = namespace
        self.name: str = name
        if not self.name:
            assert self.namespace is None

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.namespace == other.namespace and
                self.name == other.name)

    def __hash__(self):
        return hash(str(self.namespace) + str(self.name))

    def __str__(self):
        if self.name is None:
            return "NONE"
        return "/".join(self.namespace + (self.name,))

    def __lt__(self, other):
        return self.namespace < other.namespace and self.name < other.name

    def is_none(self):
        return self.name is None

    def __repr__(self):
        return self.__str__()


NONE_NODE = GNode(None, None)


class UseAnalysis(DefaultVisitor):
    def __init__(self, program):
        # The type of each node is: GNode
        self._use_graph = defaultdict(set)  # node => [node]
        self._namespace = ast.GLOBAL_NAMESPACE
        self.program = program

    def result(self):
        return self._use_graph

    @change_namespace
    def visit_class_decl(self, node):
        self._selected_namespace = self._namespace
        super(UseAnalysis, self).visit_class_decl(node)

    def visit_field_decl(self, node):
        gnode = GNode(self._namespace, node.name)
        self._use_graph[gnode]  # initialize the node

    def visit_param_decl(self, node):
        gnode = GNode(self._namespace, node.name)
        self._use_graph[gnode]  # initialize the node

    def visit_variable(self, node):
        gnode = get_decl(self.program.context,
                         self._namespace, node.name,
                         limit=self._selected_namespace)
        if gnode:
            gnode = GNode(gnode[0], gnode[1].name)
            self._use_graph[gnode].add(NONE_NODE)

    def visit_var_decl(self, node):
        """Add variable to _var_decl_stack to add flows from it to other
        variables in visit_variable.
        """
        gnode = GNode(self._namespace, node.name)
        self._use_graph[gnode]  # initialize the node
        if type(node.expr) is ast.Variable:
            # Find the node corresponding to the variable of the right-hand
            # side.
            var_node = get_decl(self.program.context,
                                self._namespace, node.expr.name,
                                limit=self._selected_namespace)
            # If node is None, this means that we referring to a variable
            # outside the context of class.
            if var_node:
                var_node = GNode(var_node[0], var_node[1].name)
                self._use_graph[var_node].add(gnode)
        else:
            super(UseAnalysis, self).visit_var_decl(node)

    @change_namespace
    def visit_func_decl(self, node):
        # TODO handle return types.
        super(UseAnalysis, self).visit_func_decl(node)

    def visit_func_call(self, node):
        """Add flows from function call arguments to function declaration
        parameters.
        """
        # Find the namespace and the declaration of the functions that is
        # being called.
        fun_nsdecl = get_decl(
            self.program.context, self._namespace, node.func,
            limit=self._selected_namespace)
        add_none = False
        if not fun_nsdecl:
            # The function is outer, so, if we pass a variable to this function
            # we must add an edge from this variable to the None node.
            add_none = True

        for i, arg in enumerate(node.args):
            if type(arg) is not ast.Variable:
                if not add_none:
                    namespace, func_decl = fun_nsdecl
                    param_namespace = namespace + (func_decl.name,)
                    self._use_graph[NONE_NODE].add(GNode(
                        param_namespace, func_decl.params[i].name))
                self.visit(arg)
                continue
            var_node = get_decl(self.program.context, self._namespace,
                                arg.name, limit=self._selected_namespace)
            # Case 1: we have a variable reference 'x' in a function declared
            # in the current class.
            # So, we add an edge from 'x' to the parameter of the function.
            if var_node and not add_none:
                namespace, func_decl = fun_nsdecl
                param_namespace = namespace + (func_decl.name,)
                var_node = (var_node[0], var_node[1].name)
                self._use_graph[var_node].add(
                    GNode(param_namespace, func_decl.params[i].name))
            if var_node and add_none:
                var_node = GNode(var_node[0], var_node[1].name)
                self._use_graph[var_node].add(NONE_NODE)

        if node.receiver:
            self.visit(node.receiver)
