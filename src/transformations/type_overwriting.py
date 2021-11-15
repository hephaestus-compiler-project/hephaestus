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
        self._method_selection = True
        self._candidate_methods = []
        self._selected_method = None

    def visit_program(self, node):
        super().visit_program(node)
        self._method_selection = False
        if not self._candidate_methods:
            return node
        self._selected_method = utils.random.choice(self._candidate_methods)
        return super().visit_program(node)

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

    def _add_candidate_method(self, node):
        t_an = tda.TypeDependencyAnalysis(self.program,
                                          namespace=self._namespace[:-1],
                                          type_graph=None)
        t_an.visit(node)
        type_graph = t_an.result()
        type_graph.update(self.global_type_graph)
        candidate_nodes = [
            n
            for n in type_graph.keys()
            if n.is_omittable() and not (
                isinstance(n, tda.DeclarationNode) and n.decl.name == tda.RET
            )
        ]
        if not candidate_nodes:
            return node
        self._candidate_methods.append((self._namespace, candidate_nodes,
                                        type_graph))
        return node

    @change_namespace
    def visit_func_decl(self, node):
        if self._method_selection:
            return self._add_candidate_method(node)
        namespace, candidate_nodes, type_graph = self._selected_method
        if namespace != self._namespace:
            return node

        # Generate a type that is irrelevant
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
        if ir_type is None:
            return node

        # Perform the mutation
        if isinstance(n, tda.DeclarationNode):
            if isinstance(n.decl, ast.VariableDeclaration):
                n.decl.var_type = ir_type
            else:
                n.decl.ret_type = ir_type
            n.decl.inferred_type = ir_type
        t = getattr(n, 't', None)
        if t is not None:
            type_parameters = (
                t.t_constructor.type_parameters
                if isinstance(t, tp.ParameterizedType)
                else t.type_parameters
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
