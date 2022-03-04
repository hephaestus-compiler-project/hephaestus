# pylint: disable=too-many-instance-attributes,dangerous-default-value
from copy import copy
import itertools

from src.ir import ast
from src.transformations.base import Transformation, change_namespace
from src.analysis import type_dependency_analysis as tda


class TypeErasure(Transformation):
    CORRECTNESS_PRESERVING = True

    def __init__(self, program, language, logger=None, options={}):
        super().__init__(program, language, logger, options)
        self._namespace = ast.GLOBAL_NAMESPACE
        self.max_combinations = options.get(
            'max_combinations', 500000
        )
        self.global_type_graph = {}

    @change_namespace
    def visit_class_decl(self, node):
        return super().visit_class_decl(node)

    def visit_var_decl(self, node):
        if self._namespace != ast.GLOBAL_NAMESPACE:
            return super().visit_var_decl(node)

        # We need this analysis, we have to include type information of global
        # variables.
        t_an = tda.TypeDependencyAnalysis(self.program,
                                          namespace=ast.GLOBAL_NAMESPACE)
        t_an.visit(node)
        self.global_type_graph.update(t_an.result())
        return node

    @change_namespace
    def visit_func_decl(self, node):
        t_an = tda.TypeDependencyAnalysis(self.program,
                                          namespace=self._namespace[:-1],
                                          type_graph=None)
        t_an.visit(node)
        type_graph = t_an.result()
        type_graph.update(self.global_type_graph)
        omittable_nodes = [n for n in type_graph.keys()
                           if n.is_omittable()]
        omittable_nodes = [
            n
            for n in omittable_nodes
            if tda.is_combination_feasible(type_graph, (n,))
        ]
        # We compute the powerset of omittable nodes.
        combinations = itertools.chain.from_iterable(
            itertools.combinations(omittable_nodes, r)
            for r in range(len(omittable_nodes), 0, -1)
        )
        for i, combination in enumerate(combinations):
            if self.max_combinations and i > self.max_combinations:
                break
            c_type_graph = copy(type_graph)
            # We are trying to find the maximal combination that is feasible.
            if tda.is_combination_feasible(c_type_graph, combination):
                for g_node in combination:
                    self.is_transformed = True
                    if isinstance(g_node, tda.DeclarationNode):
                        g_node.decl.omit_type()
                    if isinstance(g_node,
                                  tda.TypeConstructorInstantiationCallNode):
                        g_node.t.can_infer_type_args = True
                break
        return node
