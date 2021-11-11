from copy import deepcopy, copy

from src import utils
from src.ir import ast, type_utils as tu, types as tp
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
            if n.is_omittable and isinstance(n, tda.TypeConstructorInstantiationCallNode)
        ]
        if not candidate_nodes:
            return node
        n = utils.random.choice(candidate_nodes)
        if isinstance(n, tda.TypeConstructorInstantiationCallNode):
            type_params = [
                n.target for n in type_graph[n]
                if any(e.is_inferred() for e in type_graph[n.target])
            ]
            if not type_params:
                return node
            type_param = utils.random.choice(type_params)
            node_type = n.t.get_type_variable_assignments()[type_param.t]
            old_type = node_type
        else:
            node_type = n.decl.get_type()
            old_type = node_type
        if node_type.name in ["Boolean", "String", "BigInteger"]:
            return node
        ir_type = tu.find_irrelevant_type(node_type, self.types,
                                          self.bt_factory)
        if ir_type is not None:
            if isinstance(n, tda.DeclarationNode) and n.decl.name == tda.RET:
                return node

            if isinstance(n, tda.DeclarationNode):
                n.decl.var_type = ir_type
                n.decl.inferred_type = ir_type
            type_parameters = (
                n.t.t_constructor.type_parameters
                if isinstance(n.t, tp.ParameterizedType)
                else n.t.type_parameters
            )
            if isinstance(n, tda.TypeConstructorInstantiationCallNode):
                indexes = {
                    t_param: i
                    for i, t_param in enumerate(type_parameters)
                }
                n.t.type_args[indexes[type_param.t]] = ir_type
            self.is_transformed = True
            self.error_injected = "{} expected but {} found in node {}".format(
                str(old_type), str(ir_type), n.node_id)
        return node
