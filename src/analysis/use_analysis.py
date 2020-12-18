from typing import Tuple, NamedTuple
from collections import defaultdict

from src import graph_utils as gu
from src.ir import ast
from src.ir import kotlin_types as kt
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


class GNode(NamedTuple, gu.Node):
    namespace: Tuple[str, ...]
    name: str

    def __str__(self):
        if self.name is None:
            return "NONE"
        return "/".join(self.namespace + (self.name,))

    def is_none(self):
        return self.name is None

    def __repr__(self):
        return self.__str__()


NONE_NODE = GNode(None, None)
FUNC_RET = '__RET__'


class UseAnalysis(DefaultVisitor):
    def __init__(self, program):
        # The type of each node is: GNode
        self._use_graph = defaultdict(set)  # node => [node]
        self._namespace = ast.GLOBAL_NAMESPACE
        self.program = program

    def result(self):
        return self._use_graph

    def _flow_ret_to_callee(self, expr: ast.FunctionCall, target_node: GNode):
        fun_nsdecl = get_decl(
            self.program.context, self._namespace, expr.func,
            limit=self._selected_namespace)
        if not fun_nsdecl:
            return
        callee_node = GNode(fun_nsdecl[0] + (fun_nsdecl[1].name,),
                            FUNC_RET)
        if target_node:
            self._use_graph[callee_node].add(target_node)

    def _flow_var_to_ref(self, expr: ast.Variable, target_node: GNode):
        var_node = get_decl(self.program.context,
                            self._namespace, expr.name,
                            limit=self._selected_namespace)
        if not var_node:
            # If node is None, this means that we referring to a variable
            # outside the context of class.
            return
        var_node = GNode(var_node[0], var_node[1].name)
        if target_node:
            self._use_graph[var_node].add(target_node)

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
        if not gnode:
            return
        # If this variable reference is not in the return of the
        # current function, we add an edge from this variable to NONE.
        #
        # For example:
        #  * return x == "foo" => We add the edge x -> NONE
        #  * return x => We don't add any edge.
        ret_node = GNode(self._namespace, FUNC_RET)
        gnode = GNode(gnode[0], gnode[1].name)
        nodes = self._use_graph[gnode]
        if ret_node not in nodes:
            self._use_graph[gnode].add(NONE_NODE)

    def visit_var_decl(self, node):
        """Add variable to _var_decl_stack to add flows from it to other
        variables in visit_variable.
        """
        gnode = GNode(self._namespace, node.name)
        self._use_graph[gnode]  # initialize the node
        if isinstance(node.expr, ast.Variable):
            self._flow_var_to_ref(node.expr, gnode)
        elif isinstance(node.expr, ast.FunctionCall):
            self._flow_ret_to_callee(node.expr, gnode)
        else:
            super(UseAnalysis, self).visit_var_decl(node)

    @change_namespace
    def visit_func_decl(self, node):
        ret_node = None
        if node.get_type() != kt.Unit:
            # We add a special node for representing the return of a function.
            ret_node = GNode(self._namespace, FUNC_RET)
            self._use_graph[ret_node]
        expr = None
        if isinstance(node.body, ast.Block):
            expr = node.body.body[-1] if node.body.body else None
        else:
            expr = node.body
        if not expr:
            return
        if isinstance(expr, ast.Variable):
            self._flow_var_to_ref(expr, ret_node)
        if isinstance(expr, ast.FunctionCall):
            self._flow_ret_to_callee(expr, ret_node)
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
            param_node = (
                NONE_NODE
                if add_none
                else GNode(fun_nsdecl[0] + (fun_nsdecl[1].name,),
                           fun_nsdecl[1].params[i].name)
            )
            if isinstance(arg, ast.Variable):
                # The argument is a variable reference. So add edge from the
                # variable to the corresponding functions's parameter.
                self._flow_var_to_ref(arg, param_node)
                continue
            if isinstance(arg, ast.FunctionCall):
                # The argument is a function call. So depending on the callee
                # function, we might add an edge from the callee's function
                # return node ot the corresponding function's parameter.
                self._flow_ret_to_callee(arg, param_node)
                continue
            if param_node is not NONE_NODE:
                # The argument is other than a variable reference or function
                # call. So we add an edge from NONE to the corresponding
                # function's parameter.
                self._use_graph[NONE_NODE].add(param_node)
            self.visit(arg)
        if fun_nsdecl:
            # If this function call is part of an expression other than the
            # return expression of the current function, then we add an edge
            # from the callee's ret node to NONE.
            # For example:
            # * return if (cond) calee(x) else y =>
            #       We add the edge callee_ret -> NONE
            # * return callee(x) => We don't add any edge.
            namespace, fun_decl = fun_nsdecl
            gnode = GNode(namespace + (fun_decl.name,), FUNC_RET)
            ret_node = GNode(self._namespace, FUNC_RET)
            nodes = self._use_graph[gnode]
            if ret_node not in nodes:
                self._use_graph[gnode].add(NONE_NODE)

        if node.receiver:
            self.visit(node.receiver)
