from copy import deepcopy, copy
import itertools

from src import utils
from src.ir import ast, type_utils as tu
from src.transformations.base import Transformation, change_namespace
from src.analysis import type_dependency_analysis as tda


class TypeOverwriting(Transformation):
    CORRECTNESS_PRESERVING = False

    def __init__(self, program, language, logger=None, options={}):
        super().__init__(program, language, logger, options)
        self._namespace = ast.GLOBAL_NAMESPACE
        self.global_type_graph = {}
        self.types = program.get_types()
        self.bt_factory = program.bt_factory
        self.error_injected = None

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
        if self.is_transformed:
            return node
        t_an = tda.TypeDependencyAnalysis(self.program,
                                          namespace=self._namespace[:-1],
                                          type_graph=None)
        t_an.visit(node)
        type_graph = t_an.result()
        type_graph.update(self.global_type_graph)
        candidate_nodes = [
            n
            for n in type_graph.keys()
            if n.is_omittable and isinstance(n, tda.DeclarationNode)
        ]
        if not candidate_nodes:
            return node
        n = utils.random.choice(candidate_nodes)
        node_type = n.decl.get_type()
        if node_type.name in ["Boolean", "String", "BigInteger"]:
            return node
        ir_type = tu.find_irrelevant_type(node_type, self.types,
                                          self.bt_factory)
        if ir_type is not None and isinstance(n.decl, ast.VariableDeclaration):
            if n.decl.name == tda.RET:
                return node
            old_type = n.decl.get_type()
            # import pdb; pdb.set_trace()
            n.decl.var_type = ir_type
            n.decl.inferred_type = ir_type
            self.is_transformed = True
            self.error_injected = "{} expected but {} found in node {}".format(
                str(old_type), str(ir_type), n.node_id)
        return node
