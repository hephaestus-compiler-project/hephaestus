# pylint: disable=pointless-statement
from typing import Tuple, NamedTuple
from collections import defaultdict

from src.ir import ast
from src.ir.context import get_decl
from src.ir.visitors import DefaultVisitor
from src.transformations.base import change_namespace


class GNode(NamedTuple):
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
    """Get the use graph for a node.

    To employ UseAnalysis use the following instructions.

    analysis = UseAnalysis(self.program)
    analysis.visit(node)
    use_graph = analysis.result()
    """
    def __init__(self, program):
        # The type of each node is: GNode
        self._use_graph = defaultdict(set)  # node => [node]
        self._use_graph[NONE_NODE]
        self._namespace = ast.GLOBAL_NAMESPACE
        self.program = program
        self.add_none_to_call = True
        self._ret_vars = set()
        self._selected_namespace = None

    def set_namespace(self, namespace):
        self._namespace = namespace

    def result(self):
        return self._use_graph

    def _flow_ret_to_callee(self, expr: ast.FunctionCall, target_node: GNode):
        fun_nsdecl = get_decl(
            self.program.context, self._namespace, expr.func,
            limit=self._selected_namespace)
        if not fun_nsdecl:
            self._use_graph[target_node].add(NONE_NODE)
            return
        callee_node = GNode(fun_nsdecl[0] + (fun_nsdecl[1].name,),
                            FUNC_RET)
        if target_node:
            self._use_graph[target_node]
            self._use_graph[callee_node].add(target_node)

    def _flow_var_to_ref(self, expr: ast.Variable, target_node: GNode):
        var_node = get_decl(self.program.context,
                            self._namespace, expr.name,
                            limit=self._selected_namespace)
        if not var_node:
            # If node is None, this means that we referring to a variable
            # outside the context of class.
            self._use_graph[target_node].add(NONE_NODE)
            return
        var_node = GNode(var_node[0], var_node[1].name)
        if target_node:
            self._use_graph[target_node]
            self._use_graph[var_node].add(target_node)

    @change_namespace
    def visit_class_decl(self, node):
        self._selected_namespace = self._namespace
        super().visit_class_decl(node)

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
        if ret_node not in nodes or node.name not in self._ret_vars:
            self._use_graph[gnode].add(NONE_NODE)
        else:
            self._ret_vars.discard(node.name)

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
            prev = self.add_none_to_call
            self.add_none_to_call = False
            self.visit(node.expr)
            self.add_none_to_call = prev
        else:
            self._use_graph[gnode].add(NONE_NODE)
            super().visit_var_decl(node)

    def visit_assign(self, node):
        self._flow_var_to_ref(node, NONE_NODE)
        super().visit_assign(node)

    @change_namespace
    def visit_func_decl(self, node):
        """NOTE that you should set the namespace (use set_namespace), in case
        the function is not a top_level declaration.
        """
        ret_node = None
        if node.get_type() != self.program.bt_factory.get_void_type():
            # We add a special node for representing the return of a function.
            ret_node = GNode(self._namespace, FUNC_RET)
            self._use_graph[ret_node]
        expr = None
        if isinstance(node.body, ast.Block):
            expr = node.body.body[-1] if node.body.body else None
        else:
            expr = node.body
        if not expr:
            return super().visit_func_decl(node)
        if isinstance(expr, ast.Variable):
            self._ret_vars.add(expr.name)
            self._flow_var_to_ref(expr, ret_node)
        elif isinstance(expr, ast.FunctionCall):
            self._flow_ret_to_callee(expr, ret_node)
        else:
            if ret_node:
                self._use_graph[ret_node].add(NONE_NODE)
        super().visit_func_decl(node)

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
            if add_none:
                param_node = NONE_NODE
            else:
                len_p = len(fun_nsdecl[1].params)
                if i < len_p:
                    param_index = i
                else:
                    # Ok, the formal parameter is a vararg, and we have
                    # provided more than one arguments.
                    param_index = len_p - 1
                    assert fun_nsdecl[1].params[param_index].vararg

                param_node = GNode(fun_nsdecl[0] + (fun_nsdecl[1].name,),
                                   fun_nsdecl[1].params[param_index].name)
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
                # The ret variable of this function should not point to None.
                prev = self.add_none_to_call
                self.add_none_to_call = False
                self.visit(arg)
                self.add_none_to_call = prev
                continue
            if param_node is not NONE_NODE:
                # The argument is other than a variable reference or function
                # call. So we add an edge from NONE to the corresponding
                # function's parameter.
                self._use_graph[param_node]
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
            if ret_node not in nodes and self.add_none_to_call:
                self._use_graph[gnode].add(NONE_NODE)

        if node.receiver:
            self.visit(node.receiver)
