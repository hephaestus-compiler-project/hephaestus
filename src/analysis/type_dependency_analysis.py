from copy import deepcopy, copy
from collections import defaultdict
from typing import NamedTuple, Union, Dict, List

from src import utils, graph_utils as gu
from src.ir import ast, types as tp, type_utils as tu
from src.ir.context import get_decl
from src.ir.visitors import DefaultVisitor
from src.transformations.base import change_namespace


RET = "__RET__"


class TypeVarNode(NamedTuple):
    parent_id: str
    t: tp.TypeParameter
    is_decl: bool

    def __str__(self):
        prefix = "!" if self.is_decl else ""
        return prefix + "TypeVariable[{}]".format(self.node_id)

    def __repr__(self):
        return self.__str__()

    @property
    def node_id(self):
        return self.parent_id + "/" + self.t.name

    def is_omittable(self):
        return False

    def get_type(self):
        return self.t


class TypeNode(NamedTuple):
    t: tp.Type
    parent_id: str

    def __str__(self):
        return "Type[{}]".format(self.node_id)

    def __repr__(self):
        return self.__str__()

    @property
    def node_id(self):
        prefix = "" if self.parent_id is None else self.parent_id + "/"
        if self.t is None:
            return prefix + "*"
        return prefix + self.t.name

    def is_omittable(self):
        return False

    def get_type(self):
        return self.t


class DeclarationNode(NamedTuple):
    parent_id: str
    decl: ast.Declaration

    def __str__(self):
        return "Declaration[{}]".format(self.node_id)

    def __repr__(self):
        return self.__str__()

    @property
    def node_id(self):
        return self.parent_id + "/" + self.decl.name

    def is_omittable(self):
        return getattr(self.decl, "inferred_type", False) is not False

    def get_type(self):
        return self.decl.get_type()


class TypeConstructorInstantiationCallNode(NamedTuple):
    parent_id: str
    t: tp.ParameterizedType
    constructor_call: ast.New

    def __str__(self):
        return "TypeConInstCall[{}]".format(self.node_id)

    def __repr__(self):
        return self.__str__()

    @property
    def node_id(self):
        return self.parent_id + "/" + self.t.name

    def is_omittable(self):
        return True

    def get_type(self):
        return self.t


class TypeConstructorInstantiationDeclNode(NamedTuple):
    parent_id: str
    t: tp.ParameterizedType

    def __str__(self):
        return "TypeConInstDecl[{}]".format(self.node_id)

    def __repr__(self):
        return self.__str__()

    @property
    def node_id(self):
        return self.parent_id + "/" + self.t.name

    def is_omittable(self):
        return False

    def get_type(self):
        return self.t


class Edge(NamedTuple):
    DECLARED = 0
    INFERRED = 1

    target: Union[
        TypeVarNode,
        TypeNode,
        DeclarationNode,
        TypeConstructorInstantiationCallNode,
        TypeConstructorInstantiationDeclNode
    ]
    label: int

    def label2str(self):
        if self.is_declared():
            return "declared"
        else:
            return "inferred"

    def __str__(self):
        template = "-> {} ({})"
        return template.format(str(self.target), self.label2str())

    def __repr__(self):
        return self.__str__()

    def is_declared(self):
        return self.label == self.DECLARED

    def is_inferred(self):
        return self.label == self.INFERRED


def construct_edge(type_graph, source, target, edge_label):
    if source not in type_graph:
        type_graph[source] = [Edge(target, edge_label)]
    else:
        type_graph[source].append(Edge(target, edge_label))


def _handle_declaration_node(type_graph, node):
    edges = type_graph[node]
    new_edges = []
    for e in edges:
        if not e.is_declared():
            new_edges.append(e)
            continue
        if isinstance(e.target, TypeConstructorInstantiationDeclNode):
            for type_var in type_graph[e.target]:
                type_graph[type_var.target] = []
            type_graph[e.target] = []
    type_graph[node] = new_edges


def _handle_type_inst_call_node(type_graph, node):
    for type_var in type_graph[node]:
        edges = type_graph[type_var.target]
        edges = [
            e
            for e in edges
            if not e.is_declared()
        ]
        type_graph[type_var.target] = edges


def is_combination_feasible(type_graph, combination):
    # Step 1: Remove all required edges from the graph. These edge removals
    # represent the type infromation that is omitted from the program.
    for node in combination:
        assert node in type_graph, (
            "Node {} was not found in type graph".format(node))
        if isinstance(node, DeclarationNode):
            _handle_declaration_node(type_graph, node)
        elif isinstance(node, TypeConstructorInstantiationCallNode):
            _handle_type_inst_call_node(type_graph, node)
        else:
            continue

    # Step 2 (Verification): verify that all declaration node lead to type
    # nodes corresponding to the same type with that they are declared. Also
    # verify that all type variable nodes lead to type nodes that are the same
    # with those they are instantiated.
    removed_decls = set()
    for node in combination:
        if not isinstance(node, DeclarationNode):
            continue
        reachable = gu.dfs(type_graph, node)
        for n in reachable:
            if isinstance(n, (TypeNode,
                              TypeConstructorInstantiationCallNode,
                              TypeConstructorInstantiationDeclNode)):
                if n.t != node.decl.get_type():
                    return False
        removed_decls.add(node.node_id)

    for node in combination:
        if isinstance(node, TypeConstructorInstantiationCallNode):
            type_assignments = node.t.get_type_variable_assignments()
            for type_var in type_graph[node]:
                assigned_t = type_assignments[type_var.target.t]
                reachable = gu.dfs(type_graph, type_var.target)
                is_ok = False
                for n in reachable:
                    if isinstance(n, TypeNode):
                        is_ok = n.t == assigned_t
                        if n.parent_id:
                            is_ok = is_ok and n.parent_id not in removed_decls
                    if is_ok:
                        break
                if not is_ok:
                    return False

    return True


def _is_recursive_call(func_name, func_body):
    if not func_body:
        return False
    if isinstance(func_body, ast.FunctionCall):
        return func_name == func_body.func
    return False


class TypeDependencyAnalysis(DefaultVisitor):
    def __init__(self, program, namespace=None, type_graph=None):
        self._bt_factory = program.bt_factory
        self.type_graph: Dict[
            Union[
                TypeNode,
                TypeVarNode,
                DeclarationNode,
                TypeConstructorInstantiationCallNode,
                TypeConstructorInstantiationDeclNode
            ],
            List[Edge]
        ] = type_graph or {}
        self.program = program
        self._context = self.program.context
        self._namespace = namespace or ast.GLOBAL_NAMESPACE
        self._types = self.program.get_types()
        self._stack: list = list(ast.GLOBAL_NAMESPACE)
        self._inferred_nodes: dict = defaultdict(list)
        self._exp_type: tp.Type = None
        self._exp_node_id = None
        self._stream = iter(range(0, 10000))
        self._func_non_void_block_type = None
        self._id_gen = utils.IdGen()

    def result(self):
        return self.type_graph

    def _get_node_id(self):
        top_stack = self._stack[-1]
        return self._id_gen.get_node_id(top_stack)

    def _find_target_type_variable(self, type_var_id):
        nodes = set(self.type_graph.keys())
        nodes.update({v for value in self.type_graph.values() for v in value})

        for n in nodes:
            if not isinstance(n, TypeVarNode):
                continue
            if n.node_id == type_var_id:
                return n
        return None

    def _find_dependent_type_variable(self, source_type_var, type_var_deps,
                                      target_type_constructor, node_id):
        if not type_var_deps:
            return None
        targets = type_var_deps.get(source_type_var, [])
        type_var = None
        while targets:
            assert len(targets) == 1
            t = targets[0]
            type_con_name, type_var = t.split('.')
            if type_con_name == target_type_constructor:
                type_var = t
                break

            targets = type_var_deps.get(t, [])
        if not type_var:
            return None

        nodes = set(self.type_graph.keys())
        nodes.update({v for value in self.type_graph.values() for v in value})
        type_var_id = node_id + "/" + type_var.replace(".", "/")
        return self._find_target_type_variable(type_var_id)

    def _convert_type_to_node(self, t, infer_t, node_id):
        """
        This function converts a type to a node. There are three possible
        scenarios:

        1) The given type is not parameterized. In this case, we simply
           construct a TypeNode containing the given type.
        2) The given type is parameterized but the inferred node is not
           a type constructor instantiation. In this case, again, we simply
           construct a TypeNode containing the given type.
        3) Othewrise, we construct a TypeConstructorInstantiationDeclNode
           and connect it with the type parameters of the type constructor.
        """
        if not t.is_parameterized():
            return TypeNode(t, None)

        if not isinstance(infer_t, TypeConstructorInstantiationCallNode):
            return TypeNode(t, None)

        main_node = TypeConstructorInstantiationDeclNode(node_id, t)
        type_deps = tu.build_type_variable_dependencies(infer_t.t, t)
        for i, t_param in enumerate(t.t_constructor.type_parameters):
            type_var_id = node_id + "/" + t.name
            source = TypeVarNode(type_var_id, t_param, True)
            target = TypeNode(t.type_args[i], None)
            # we connect type variables with the types with which they
            # are instantiated.
            construct_edge(self.type_graph, source, target, Edge.DECLARED)
            # We connect type constructor with the type parameters.
            construct_edge(self.type_graph, main_node, source,
                           Edge.DECLARED)

            # Here, the TypeConstructorInstantiationCallNode and
            # the TypeConstructorInstantiationDeclNode correspond to the same
            # type constructor. In this case, we connect the included type
            # variables. In other words, in this case we handle the following
            # scenario:
            # -TypeInstDeclNode-   -TypeInstCallNode-
            # Foo<String> x =       new Foo<String>()
            if t.name == infer_t.t.name:
                target_var = TypeVarNode(type_var_id, t_param, False)
            else:
                # Otherwise, we are trying to find a target type variable
                # to connect the type variable of TypeInstDeclNode with.
                # This handles subtyping. For example
                # class A<T>
                # class B<T> : A<T>()
                #
                # A<String> x = new Bar<String>()
                #
                # In the above example, we connect the type variable of A
                # with the type variable of A.
                target_var = self._find_dependent_type_variable(
                    t.name + "." + t_param.name, type_deps, infer_t.t.name,
                    node_id)
            use_site_type_var, decl_site_type_var = target_var, source
            if target_var in self.type_graph:
                # At this point we connect a type variable found in the
                # use site with a type variable found in the decl site.
                # Example.
                # A<T> x = new A<T>()
                #   ^            |
                #   |____________|
                construct_edge(self.type_graph, use_site_type_var,
                               decl_site_type_var, Edge.INFERRED)
        return main_node

    def visit_integer_constant(self, node):
        node_id, _ = self._get_node_id()
        self._inferred_nodes[node_id].append(TypeNode(node.integer_type, None))

    def visit_real_constant(self, node):
        node_id, _ = self._get_node_id()
        self._inferred_nodes[node_id].append(TypeNode(node.real_type, None))

    def visit_string_constant(self, node):
        node_id, _ = self._get_node_id()
        self._inferred_nodes[node_id].append(
            TypeNode(self._bt_factory.get_string_type(), None))

    def visit_boolean_constant(self, node):
        node_id, _ = self._get_node_id()
        self._inferred_nodes[node_id].append(
            TypeNode(self._bt_factory.get_boolean_type(), None))

    def visit_char_constant(self, node):
        node_id, _ = self._get_node_id()
        self._inferred_nodes[node_id].append(
            TypeNode(self._bt_factory.get_char_type(), None))

    def visit_bottom_constant(self, node):
        if node.t is None:
            return
        node_id, _ = self._get_node_id()
        self._inferred_nodes[node_id].append(TypeNode(node.t, None))

    def visit_logical_expr(self, node):
        prev = copy(self._stack)
        self._stack.append("LOGICAL")
        prev_expt = self._exp_type
        self._exp_type = None
        super().visit_logical_expr(node)
        self._stack = prev
        self._exp_type = prev_expt

        node_id, _ = self._get_node_id()
        self._inferred_nodes[node_id].append(
            TypeNode(self._bt_factory.get_boolean_type(), None))

    def visit_equality_expr(self, node):
        prev = copy(self._stack)
        self._stack.append("EQUALITY")
        prev_expt = self._exp_type
        self._exp_type = None
        super().visit_equality_expr(node)
        self._stack = prev
        self._exp_type = prev_expt

        node_id, _ = self._get_node_id()
        self._inferred_nodes[node_id].append(
            TypeNode(self._bt_factory.get_boolean_type(), None))

    def visit_comparison_expr(self, node):
        prev = copy(self._stack)
        self._stack.append("EQUALITY")
        prev_expt = self._exp_type
        self._exp_type = None
        super().visit_comparison_expr(node)
        self._stack = prev
        self._exp_type = prev_expt

        node_id, _ = self._get_node_id()
        self._inferred_nodes[node_id].append(
            TypeNode(self._bt_factory.get_boolean_type(), None))

    def visit_array_expr(self, node):
        node_id, _ = self._get_node_id()
        self._inferred_nodes[node_id].append(TypeNode(node.array_type, None))

    def visit_variable(self, node):
        decl = get_decl(self.program.context,
                        self._namespace, node.name)
        if not decl:
            # If we cannot find declaration in context, then abort.
            return
        namespace, decl = decl
        node_id, _ = self._get_node_id()
        self._inferred_nodes[node_id].append(
            DeclarationNode("/".join(namespace), decl)
        )

    def _visit_assign_with_receiver(self, node):
        prev_expt = self._exp_type
        self._exp_type = None
        self.visit(node.receiver)
        self._exp_type = prev_expt

        # We need to infer the type of the receiver.
        receiver_t = tu.get_type_hint(node.receiver, self._context,
                                      self._namespace, self._bt_factory,
                                      self._types)
        if receiver_t is None:
            return
        type_var_map = {}
        # If the receiver type is parameterized, compute type variable
        # assignments
        if receiver_t.is_parameterized():
            type_var_map = receiver_t.get_type_variable_assignments()
        # If the type of receiver is a type variable, get its bound.
        if receiver_t.is_type_var():
            receiver_t = receiver_t.get_bound_rec(self._bt_factory)

        f = tu.get_decl_from_inheritance(receiver_t, node.name, self._context)
        assert f is not None, (
            "Field " + node.name + " was not found in class " +
            receiver_t.name)
        f, _ = f
        # Substitute field type
        field_type = tp.substitute_type(f.get_type(), type_var_map)
        field_decl = deepcopy(f)
        field_decl.field_type = field_type
        parent_id, nu = self._get_node_id()
        node_id = parent_id + ("/" + nu if nu else "") + "/" + receiver_t.name
        self._handle_declaration(node_id, field_decl, node.expr,
                                 "field_type")

    def visit_assign(self, node):
        attribute_names = {
            ast.FieldDeclaration: "field_type",
            ast.ParameterDeclaration: "param_type",
            ast.VariableDeclaration: "var_type"
        }
        if node.receiver is None:
            decl = get_decl(self._context,
                            self._namespace, node.name)
            if not decl:
                return node
            namespace, decl = decl
            node_id = "/".join(namespace)
            self._handle_declaration(node_id, decl, node.expr,
                                     attribute_names[type(decl)])
        else:
            self._visit_assign_with_receiver(node)

    def visit_conditional(self, node):
        from copy import copy
        prev = copy(self._stack)
        self._stack.append("COND")
        prev_expt = self._exp_type
        self._exp_type = None
        self.visit(node.cond)
        self._stack = prev
        self._exp_type = prev_expt

        namespace = self._namespace

        self._namespace = namespace + ("true_block",)
        self.visit(node.true_branch)
        self._namespace = namespace + ("false_block",)
        self.visit(node.false_branch)
        self._namespace = namespace

    def _handle_declaration(self, parent_node_id: str, node: ast.Node,
                            expr: ast.Expr, type_attr: str,
                            propagate_decl_nodes=False):
        node_id = parent_node_id + "/" + node.name
        self._stack.append(node_id)
        node_type = getattr(node, type_attr, None)
        prev = self._exp_type
        prev_node_id = self._exp_node_id
        self._exp_type = node_type
        self._exp_node_id = node_id
        self.visit(expr)
        self._stack.pop()
        source = DeclarationNode(parent_node_id, node)

        inferred_nodes = self._inferred_nodes.pop(node_id, [])
        for n in inferred_nodes:
            if isinstance(n, TypeConstructorInstantiationDeclNode) and \
                    propagate_decl_nodes:
                self._inferred_nodes[node_id].append(n)
            edge_label = (
                Edge.DECLARED
                if isinstance(n, TypeConstructorInstantiationDeclNode)
                else Edge.INFERRED
            )
            construct_edge(self.type_graph, source, n, edge_label)

        added_declared = any(e.is_declared()
                             for e in self.type_graph.get(source, []))

        if not added_declared and node_type is not None and inferred_nodes:
            if getattr(node, 'inferred_type', False) is not False:
                # Add this edge only if the type declaration is omittable,
                # i.e., for variables
                construct_edge(self.type_graph, source,
                               TypeNode(node_type, node_id), Edge.DECLARED)
        self._exp_type = prev
        self._exp_node_id = prev_node_id

    def visit_block(self, node):
        if not self._func_non_void_block_type:
            super().visit_block(node)
            return
        children = node.children()
        for c in children[:-1]:
            self.visit(c)
        ret_expr = children[-1]
        # We create a "virtual" variable declaration representing the
        # return value of the function.
        parent_id, _ = self._get_node_id()
        ret_decl = ast.VariableDeclaration(
            RET, ret_expr, is_final=True,
            var_type=self._func_non_void_block_type)
        self._handle_declaration(parent_id, ret_decl, ret_expr,
                                 'var_type')

    def visit_var_decl(self, node):
        self._handle_declaration("/".join(self._namespace),
                                 node, node.expr, 'var_type')

    def visit_field_decl(self, node):
        source = DeclarationNode("/".join(self._namespace), node)
        target = TypeNode(node.get_type(), None)
        construct_edge(self.type_graph, source, target, Edge.DECLARED)

    def visit_param_decl(self, node):
        parent = "/".join(self._namespace)
        if node.default is not None:
            self._handle_declaration(parent, node, node.default,
                                     "param_type")
        else:
            source = DeclarationNode("/".join(self._namespace), node)
            target = TypeNode(node.get_type(), None)
            construct_edge(self.type_graph, source, target, Edge.DECLARED)

    @change_namespace
    def visit_class_decl(self, node):
        if node.superclasses:
            prev = copy(self._stack)
            self._stack.append("SUPER " + node.name)
            self.visit(node.superclasses[0])
            self._stack = prev

        for c in node.fields + node.functions:
            self.visit(c)

    @change_namespace
    def visit_func_decl(self, node):

        children = node.children()
        if node.body is not None:
            children = children[:-1]

        for c in children:
            self.visit(c)

        if node.body is None:
            return

        node_id = "/".join(self._namespace)
        self._stack.append(node_id)
        func_non_void_block_type = self._func_non_void_block_type
        self._func_non_void_block_type = (
            None
            if node.get_type() == self._bt_factory.get_void_type()
            else node.get_type()
        )
        if isinstance(node.body, ast.Block) or _is_recursive_call(
                node.name, node.body):
            # If the corresponding function contains a block or makes a
            # recursive call, its type is not omittable.
            self.visit(node.body)
        else:
            # We create a "virtual" variable declaration representing the
            # return value of the function.
            self._handle_declaration(node_id, node, node.body,
                                     'ret_type')
        self._stack.pop()
        self._func_non_void_block_type = func_non_void_block_type

    @change_namespace
    def visit_lambda(self, node):
        return node

    def visit_field_access(self, node):
        parent_node_id, nu = self._get_node_id()
        node_id = parent_node_id + ("/" + nu if nu else "") + "/" + node.field
        prev = self._exp_type
        self._exp_type = None
        self._stack.append(node_id)
        super().visit_field_access(node)
        self._stack.pop()
        self._exp_type = prev
        self._inferred_nodes[parent_node_id].append(
            TypeNode(tu.get_type_hint(node, self._context, self._namespace,
                                      self._bt_factory, self._types), None)
        )

    def _handle_parameterized_func_call(self, fun_call, fun_decl,
                                        parent_id, node_id):
        fun_call.type_parameters = fun_decl.type_parameters
        main_node = TypeConstructorInstantiationCallNode(
            parent_id, fun_call, fun_decl)
        type_var_nodes = {}
        for i, t_param in enumerate(fun_decl.type_parameters):
            source = TypeVarNode(node_id, t_param, False)
            type_var_nodes[t_param] = source
            target = TypeNode(fun_call.type_args[i], None)
            # This edge connects type constructor with its type variables.
            construct_edge(self.type_graph, main_node, source, Edge.DECLARED)
            # This edge connects every type variable with the type arguments
            # with which it is explicitly instantiated.
            construct_edge(self.type_graph, source, target, Edge.DECLARED)
        return main_node, type_var_nodes

    def _infer_type_variables_parameterized_by_ret(self, parent_id,
                                                   node_id, ret_type,
                                                   func_type_parameters,
                                                   type_var_nodes):
        target = (
            self._parameterized_type2node(node_id, self._exp_type)
            if self._exp_type.is_parameterized()
            else TypeNode(self._exp_type, parent_id)
        )
        for t_var, assigned_t in ret_type.\
                get_type_variable_assignments().items():
            if assigned_t not in func_type_parameters:
                continue
            source = type_var_nodes.get(assigned_t)
            if not source:
                return

            # Case 1:
            # fun <T> foo(): A<T>
            # val x: A<String> = foo()
            if self._exp_type.name == ret_type.name:
                type_var_id = "/".join((node_id, self._exp_type.name))
                target_var = TypeVarNode(type_var_id, t_var, True)
                construct_edge(self.type_graph, source, target_var,
                               Edge.INFERRED)
            # Case 2:
            # fun <T> foo(): B<T>
            # val x: A<String> = foo()
            elif self._exp_type.is_parameterized():
                # Presumably the expected type and the ret type have
                # subtyping relations.
                type_deps = tu.build_type_variable_dependencies(
                    ret_type, self._exp_type)
                t_var_name = ret_type.name + "." + t_var.name
                for k, v in type_deps.items():
                    if t_var_name not in v:
                        continue
                    type_var_id = node_id + "/" + k.replace(".", "/")
                    target_var = self._find_target_type_variable(type_var_id)
                    if target_var:
                        construct_edge(self.type_graph, source,
                                       target_var, Edge.INFERRED)
            else:
                construct_edge(self.type_graph, source, target,
                               Edge.INFERRED)
        self._inferred_nodes[parent_id].append(target)

    def _infer_type_variable_by_ret(self, parent_id, node_id, ret_type,
                                    decl_ret_type, type_var_nodes,
                                    func_type_parameters):
        if not self._exp_type or not decl_ret_type.has_type_variables():
            self._inferred_nodes[parent_id].append(TypeNode(ret_type, None))
            return
        if decl_ret_type.is_type_var() and \
                decl_ret_type in func_type_parameters:
            source = type_var_nodes.get(decl_ret_type)
            if not source:
                return
            if self._exp_type.is_parameterized():
                target = self._parameterized_type2node(node_id, self._exp_type)
            else:
                # This target type depends on the declaration of the parent,
                # so we also provide the parent id to the ID.
                target = TypeNode(self._exp_type, self._exp_node_id)

            construct_edge(self.type_graph, source, target, Edge.INFERRED)
            self._inferred_nodes[parent_id].append(target)
        else:
            # This means that the ret type is a type variable corresponding
            # to a type parameter of the class.
            if decl_ret_type.is_type_var():
                self._inferred_nodes[parent_id].append(
                    TypeNode(ret_type, None))
                return
            self._infer_type_variables_parameterized_by_ret(
                parent_id, node_id, decl_ret_type, func_type_parameters,
                type_var_nodes)

    def visit_func_call(self, node):
        parent_node_id, nu = self._get_node_id()
        node_id = parent_node_id + ("/" + nu if nu else "") + "/" + node.func
        if node.receiver is None:
            fun_decl = get_decl(self._context, self._namespace,
                                node.func)
        else:
            # If the function call involves a receiver, we need to look up
            # this function in the inheritance chain of the receiver.
            receiver_t = tu.get_type_hint(node.receiver, self._context,
                                          self._namespace, self._bt_factory,
                                          self._types)
            if receiver_t is None:
                return

            if receiver_t.is_type_var():
                receiver_t = receiver_t.get_bound_rec(self._bt_factory)
            fun_decl = tu.get_decl_from_inheritance(receiver_t,
                                                    node.func, self._context)
            if fun_decl is None:
                return
            # We compute the namespace where the function declaration was
            # found.
            namespace = fun_decl[1].name
            fun_decl = (namespace, fun_decl[0])

        if not fun_decl:
            return
        namespace, fun_decl = fun_decl

        if not isinstance(fun_decl, ast.FunctionDeclaration):
            return

        if node.receiver is not None:
            prev = self._exp_type
            self._exp_type = None
            rec_node_id = node_id + "/__REC__"
            self._stack.append(rec_node_id)
            self.visit(node.receiver)
            self._stack.pop()
            self._exp_type = prev

        params_nu = len(fun_decl.params)
        type_var_map = {}
        if node.receiver and receiver_t.is_parameterized():
            type_var_map.update(receiver_t.get_type_variable_assignments())
        func_type_var_map = {}
        if fun_decl.is_parameterized():
            func_type_var_map = {
                t_param: node.type_args[i]
                for i, t_param in enumerate(fun_decl.type_parameters)
            }
            type_var_map.update(func_type_var_map)
        inferred_params = []
        for i, c in enumerate(node.args):
            param_index = i
            # If we provide too much arguments, this is because the parameter
            # is a vararg. So just take the declaration of the last formal
            # parameter.
            if i >= params_nu:
                param_index = params_nu - 1
            p = fun_decl.params[param_index]
            param = deepcopy(p)
            param.param_type = tp.substitute_type(param.get_type(),
                                                  type_var_map)
            self._handle_declaration(node_id, param, c, 'param_type')
            inferred_params.append((param, p.get_type()))
        _, type_var_nodes = self._handle_parameterized_func_call(
            node, fun_decl, parent_node_id, node_id)
        self._infer_type_variables_by_call_arguments(node_id,
                                                     type_var_nodes,
                                                     inferred_params)
        ret_type = tp.substitute_type(fun_decl.get_type(), type_var_map)
        if ret_type != self._bt_factory.get_void_type():
            self._infer_type_variable_by_ret(parent_node_id, node_id, ret_type,
                                             fun_decl.get_type(),
                                             type_var_nodes,
                                             fun_decl.type_parameters)

    def _infer_reciprocal_type_var_deps(self, node_id, t, type_var_node):
        type_var_map = t.get_type_variable_assignments()
        for k, v in type_var_map.items():
            if v.name == type_var_node.t.name:
                nid = node_id + "/" + t.name
                call_type_var_node = TypeVarNode(nid, k, False)
                decl_type_var_node = TypeVarNode(nid, k, True)
                self.type_graph[decl_type_var_node] = []
                construct_edge(self.type_graph, decl_type_var_node,
                               type_var_node, Edge.INFERRED)
                construct_edge(self.type_graph, type_var_node,
                               call_type_var_node, Edge.INFERRED)
            elif v.is_parameterized():
                nid = "/".join([node_id, t.name, k.name])
                self._infer_reciprocal_type_var_deps(
                    nid, v, type_var_node)
            else:
                pass

    def _infer_type_variables(self, node_id, t, type_var_nodes, param_decl):
        inferred_nodes = self.type_graph.get(
            DeclarationNode(node_id, param_decl), [])
        type_assignments = {}
        has_decl_node = False
        for n in inferred_nodes:
            if not type_assignments:
                # Compute how the type variables at declaration point are
                # instantiated based on the type of passed in the corresponding
                # argument.
                type_assignments = tu.unify_types(n.target.get_type(), t,
                                                  self._bt_factory,
                                                  same_type=False)
            # We know now that that the argument corresponds to a
            # type constructor instantiation
            if isinstance(n.target, TypeConstructorInstantiationDeclNode):
                has_decl_node = True
                break

        for t_var, t_arg in type_assignments.items():

            source = type_var_nodes.get(t_var)
            if source is None:
                continue
            # We are in the following case:
            # class A<T> (val f: T)
            #
            # Therefore, connect the corresponding type variable with all
            # the nodes inferred for call argument.
            if t.is_type_var():
                for n in inferred_nodes:
                    # Remove the previously added declaration node, and
                    # add the new one.
                    if n.is_declared():
                        self.type_graph[source] = [
                            e
                            for e in self.type_graph.get(source, [])
                            if not e.is_declared()
                        ]
                    construct_edge(self.type_graph, source, n.target,
                                   n.label)
            # In this case we have a scenario like the following.
            # class A<T> (val f: B<T>)
            # class C: B<String>()
            # A<String>(new C())
            #
            # In this case, the things are simple add an edge from the type
            # variable of type constructor A to a hardcoded type, which is
            # previously inferred from the type unification we performed.
            elif not has_decl_node:
                construct_edge(self.type_graph, source, TypeNode(t_arg, None),
                               Edge.INFERRED)
            # Otherwise, we are in a case like the following:
            # class A<T>(val f: B<T>)
            # A<String>(new B<String>())
            #
            # i.e., the argument of the primary type constructor corresponds
            # to another type constructor.
            # In this case, the type variable of TypeConstInstDeclNode
            # corresponding to the declaration of field f has a dependency
            # to type variable A.T. Moreover, the type variable A.T has
            # dependency to the type variable B.T. Therefore, we add the
            # corresponding edges.
            else:
                nid = node_id + "/" + param_decl.name
                self._infer_reciprocal_type_var_deps(nid, t, source)

    def _infer_type_variables_by_call_arguments(self, node_id, type_var_nodes,
                                                inferred_fields):
        # Add this point, we furher examine the arguments of a call to
        # see if any of its type variables can be inferred by the arguments
        # passed in the invocation, i.e., A<String>(x)
        for f, f_type in inferred_fields:
            if not f_type.has_type_variables():
                continue

            self._infer_type_variables(node_id, f_type, type_var_nodes, f)

    def _parameterized_type2node(self, node_id, t):
        main_node = TypeConstructorInstantiationDeclNode(node_id, t)
        type_var_id = node_id + "/" + t.name
        for i, t_param in enumerate(t.t_constructor.type_parameters):
            t_var = TypeVarNode(type_var_id, t_param, True)
            construct_edge(self.type_graph, main_node, t_var, Edge.DECLARED)
            type_arg = t.type_args[i]
            if type_arg.is_parameterized():

                target = self._parameterized_type2node(t_var.node_id,
                                                       type_arg)
                construct_edge(self.type_graph, t_var, target, Edge.DECLARED)
            else:
                construct_edge(self.type_graph, t_var,
                               TypeNode(type_arg, None), Edge.DECLARED)
        return main_node

    def _handle_type_constructor_instantiation(self, node,
                                               parent_node_id):
        # If we initialize a type constructor, then create a node for
        # representing the type constructor instantiatiation (at use-site).
        main_node = TypeConstructorInstantiationCallNode(
            parent_node_id, node.class_type, node)
        self._inferred_nodes[parent_node_id].append(main_node)
        t = node.class_type
        type_var_nodes = {}
        for i, t_param in enumerate(t.t_constructor.type_parameters):
            type_var_id = parent_node_id + "/" + t.name
            source = TypeVarNode(type_var_id, t_param, False)
            # At this point, we connect type variables that have dependencies
            # with other type variables. For example
            # class A<T1, T2: T1>
            # In this case, we connect T2 -> T1 (i.e., meaning that the
            # compiler can infer the type argument of T2, if it knows the
            # type argument of T1).
            if t_param.bound and t_param.bound.has_type_variables():
                if t_param.bound.is_type_var():
                    type_vars = [t_param.bound]
                else:
                    type_vars = t_param.bound.get_type_variables(
                        self._bt_factory)
                if t_param.bound.is_parameterized():
                    construct_edge(self.type_graph, source,
                                   TypeNode(t_param.bound, None),
                                   Edge.INFERRED)
                for t_var in type_vars:
                    bounded_type_var = TypeVarNode(type_var_id, t_var, False)
                    construct_edge(self.type_graph, source, bounded_type_var,
                                   Edge.INFERRED)
            type_var_nodes[t_param] = source
            if t.type_args[i].is_parameterized():
                target = self._parameterized_type2node(source.node_id,
                                                       t.type_args[i])
            else:
                target = TypeNode(t.type_args[i], None)
            # This edge connects type constructor with its type variables.
            construct_edge(self.type_graph, main_node, source, Edge.DECLARED)
            # This edge connects every type variable with the type arguments
            # with which it is explicitly instantiated.
            construct_edge(self.type_graph, source, target, Edge.DECLARED)
        return main_node, type_var_nodes

    def _remove_declared_edge(self, parent_node_id):
        node = None
        for k in self.type_graph.keys():
            if not isinstance(k, DeclarationNode):
                continue
            if k.node_id == parent_node_id:
                node = k
                break
        if node is not None:
            edges = [
                e
                for e in self.type_graph[node]
                if not e.is_declared()
            ]
            self.type_graph[node] = edges

    def visit_new(self, node):
        parent_node_id, nu = self._get_node_id()
        if node.class_type == self._bt_factory.get_any_type() or (
              node.class_type.name == self._bt_factory.get_array_type().name):
            self._inferred_nodes[parent_node_id].append(
                TypeNode(node.class_type, None))
            return

        # First, we use the context to retrieve the declaration of the class
        # we initialize in this node
        class_decl = get_decl(self._context, self._namespace,
                              node.class_type.name)
        assert class_decl is not None
        namespace, class_decl = class_decl

        node_id = parent_node_id + ("/" + nu if nu else "") + "/" + class_decl.name
        # First we visit the children of this node (i.e., its arguments),
        # and handle them as declarations.
        inferred_fields = []
        for i, c in enumerate(node.children()):
            f = deepcopy(class_decl.fields[i])
            if node.class_type.is_parameterized():
                type_var_map = node.class_type.get_type_variable_assignments()
                f.field_type = tp.substitute_type(f.get_type(), type_var_map)
                # Here we add fields initialized in a constructor invocation,
                # which are also used for inferring the type arguments of
                # the corresponding type constructor instantiation.
                inferred_fields.append((f, class_decl.fields[i].get_type()))
            self._handle_declaration(node_id, f, c,
                                     'field_type')

        if not node.class_type.is_parameterized():
            # We initialize a simple class, so there's nothing special to
            # do here.
            self._inferred_nodes[parent_node_id].append(
                TypeNode(node.class_type, None))
            return

        main_node, type_var_nodes = (
            self._handle_type_constructor_instantiation(node, parent_node_id)
        )
        self._infer_type_variables_by_call_arguments(node_id,
                                                     type_var_nodes,
                                                     inferred_fields)
        if self._exp_type:
            target = self._convert_type_to_node(self._exp_type, main_node,
                                                parent_node_id)
            self._remove_declared_edge(parent_node_id)
            self._inferred_nodes[parent_node_id].append(target)
