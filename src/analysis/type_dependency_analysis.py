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


class TypeNode(NamedTuple):
    t: tp.Type

    def __str__(self):
        return "Type[{}]".format(self.node_id)

    def __repr__(self):
        return self.__str__()

    @property
    def node_id(self):
        if self.t is None:
            return "*"
        return self.t.name

    def is_omittable(self):
        return False


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
    for node in combination:
        if isinstance(node, DeclarationNode):
            reachable = gu.dfs(type_graph, node)
            for n in reachable:
                if isinstance(n, (TypeNode,
                                  TypeConstructorInstantiationCallNode,
                                  TypeConstructorInstantiationDeclNode)):
                    if n.t != node.decl.get_type():
                        return False

        if isinstance(node, TypeConstructorInstantiationCallNode):
            type_assignments = node.t.get_type_variable_assignments()
            for type_var in type_graph[node]:
                assigned_t = type_assignments[type_var.target.t]
                reachable = gu.dfs(type_graph, type_var.target)
                if not any(getattr(n, 't', None) == assigned_t
                           for n in reachable):
                    return False
    return True


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
        self._stack: list = ["global"]
        self._inferred_nodes: dict = defaultdict(list)
        self._exp_type: tp.Type = None
        self._stream = iter(range(0, 10000))
        self._func_non_void_block_type = None
        self._id_gen = utils.IdGen()

    def result(self):
        return self.type_graph

    def _get_node_id(self):
        top_stack = self._stack[-1]
        return self._id_gen.get_node_id(top_stack)

    def _find_target_type_variable(self, source_type_var, type_var_deps,
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

        for n in nodes:
            if not isinstance(n, TypeVarNode):
                continue
            type_var_id = n.parent_id.rsplit("/", 1)[1] + "." + n.t.name
            if type_var == type_var_id:
                return n

        return None

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
            return TypeNode(t)

        if not isinstance(infer_t, TypeConstructorInstantiationCallNode):
            return TypeNode(t)

        main_node = TypeConstructorInstantiationDeclNode(node_id, t)
        type_deps = tu.build_type_variable_dependencies(infer_t.t, t)
        for i, t_param in enumerate(t.t_constructor.type_parameters):
            type_var_id = node_id + "/" + t.name
            source = TypeVarNode(type_var_id, t_param, True)
            target = TypeNode(t.type_args[i])
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
                target_var = self._find_target_type_variable(
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
        self._inferred_nodes[node_id].append(TypeNode(node.integer_type))

    def visit_real_constant(self, node):
        node_id, _ = self._get_node_id()
        self._inferred_nodes[node_id].append(TypeNode(node.real_type))

    def visit_string_constant(self, node):
        node_id, _ = self._get_node_id()
        self._inferred_nodes[node_id].append(
            TypeNode(self._bt_factory.get_string_type()))

    def visit_boolean_constant(self, node):
        node_id, _ = self._get_node_id()
        self._inferred_nodes[node_id].append(
            TypeNode(self._bt_factory.get_boolean_type()))

    def visit_char_constant(self, node):
        node_id, _ = self._get_node_id()
        self._inferred_nodes[node_id].append(
            TypeNode(self._bt_factory.get_char_type()))

    def visit_bottom_constant(self, node):
        if node.t is None:
            return
        node_id, _ = self._get_node_id()
        self._inferred_nodes[node_id].append(TypeNode(node.t))

    def visit_logical_expr(self, node):
        prev = copy(self._stack)
        self._stack.append("LOGICAL")
        super().visit_logical_expr(node)
        self._stack = prev

        node_id, _ = self._get_node_id()
        self._inferred_nodes[node_id].append(
            TypeNode(self._bt_factory.get_boolean_type()))

    def visit_equality_expr(self, node):
        prev = copy(self._stack)
        self._stack.append("EQUALITY")
        super().visit_equality_expr(node)
        self._stack = prev

        node_id, _ = self._get_node_id()
        self._inferred_nodes[node_id].append(
            TypeNode(self._bt_factory.get_boolean_type()))

    def visit_comparison_expr(self, node):
        prev = copy(self._stack)
        self._stack.append("EQUALITY")
        super().visit_comparison_expr(node)
        self._stack = prev

        node_id, _ = self._get_node_id()
        self._inferred_nodes[node_id].append(
            TypeNode(self._bt_factory.get_boolean_type()))

    def visit_array_expr(self, node):
        node_id, _ = self._get_node_id()
        self._inferred_nodes[node_id].append(TypeNode(node.array_type))

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
        self.visit(node.receiver)
        # We need to infer the type of the receiver.
        receiver_t = tu.get_type_hint(node.receiver, self._context,
                                      self._namespace, self._bt_factory,
                                      self._types)
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
            assert decl is not None
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
        self.visit(node.cond)
        self._stack = prev

        namespace = self._namespace

        self._namespace = namespace + ("true_block",)
        self.visit(node.true_branch)
        self._namespace = namespace + ("false_block",)
        self.visit(node.false_branch)
        self._namespace = namespace

    def _handle_declaration(self, parent_node_id: str, node: ast.Node,
                            expr: ast.Expr, type_attr: str):
        node_id = parent_node_id + "/" + node.name
        self._stack.append(node_id)
        node_type = getattr(node, type_attr, None)
        prev = self._exp_type
        self._exp_type = node_type
        self.visit(expr)
        self._stack.pop()
        source = DeclarationNode(parent_node_id, node)

        inferred_nodes = self._inferred_nodes.pop(node_id, [])
        for n in inferred_nodes:
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
                               TypeNode(node_type), Edge.DECLARED)
        self._exp_type = prev

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
        target = TypeNode(node.get_type())
        construct_edge(self.type_graph, source, target, Edge.DECLARED)

    def visit_param_decl(self, node):
        parent = "/".join(self._namespace)
        if node.default is not None:
            self._handle_declaration(parent, node, node.default,
                                     "param_type")
        else:
            source = DeclarationNode("/".join(self._namespace), node)
            target = TypeNode(node.get_type())
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
        if isinstance(node.body, ast.Block):
            self.visit(node.body)
        else:
            # We create a "virtual" variable declaration representing the
            # return value of the function.
            ret_decl = ast.VariableDeclaration(RET, node.body, is_final=True,
                                               var_type=node.get_type())
            self._handle_declaration(node_id, node, node.body,
                                     'ret_type')
        self._stack.pop()
        self._func_non_void_block_type = func_non_void_block_type

    def visit_field_access(self, node):
        parent_node_id, nu = self._get_node_id()
        node_id = parent_node_id + ("/" + nu if nu else "") + "/" + node.field
        self._stack.append(node_id)
        super().visit_field_access(node)
        self._stack.pop()
        self._inferred_nodes[parent_node_id].append(
            TypeNode(tu.get_type_hint(node, self._context, self._namespace,
                                      self._bt_factory, self._types))
        )

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
            if receiver_t.is_type_var():
                receiver_t = receiver_t.get_bound_rec(self._bt_factory)
            fun_decl = tu.get_decl_from_inheritance(receiver_t,
                                                    node.func, self._context)
            # We compute the namespace where the function declaration was
            # found.
            namespace = fun_decl[1].name
            fun_decl = (namespace, fun_decl[0])

        assert fun_decl is not None
        namespace, fun_decl = fun_decl

        if node.receiver is not None:
            rec_node_id = node_id + "/__REC__"
            self._stack.append(rec_node_id)
            self.visit(node.receiver)
            self._stack.pop()

        params_nu = len(fun_decl.params)
        for i, c in enumerate(node.args):
            param_index = i
            # If we provide too much arguments, this is because the parameter
            # is a vararg. So just take the declaration of the last formal
            # parameter.
            if i >= params_nu:
                param_index = params_nu - 1
            self._handle_declaration(node_id, fun_decl.params[param_index],
                                     c, 'param_type')
        ret_type = tu.get_type_hint(node, self._context, self._namespace,
                                    self._bt_factory, self._types)
        if ret_type != self._bt_factory.get_void_type():
            self._inferred_nodes[parent_node_id].append(
                TypeNode(ret_type)
            )

    def _infer_type_variables_by_call_arguments(self, node_id, class_decl,
                                                type_var_nodes,
                                                inferred_fields):
        # Add this point, we furher examine the fields of the constructor to
        # see if any of its type variables can be inferred by the arguments
        # passed in the constructor invocation, i.e., A<String>(x)
        for f, f_type in inferred_fields:
            if not f_type.is_type_var():
                continue
            source = type_var_nodes[f_type]

            inferred_nodes = self.type_graph.get(
                DeclarationNode(node_id, f), [])
            for n in inferred_nodes:
                if n.label == Edge.DECLARED:
                    continue
                # This edge connects the corresponding type variable with
                # the type inferred for the respective argument of
                # constructor.
                construct_edge(self.type_graph, source, n.target,
                               Edge.INFERRED)

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
                                   TypeNode(t_param.bound), Edge.INFERRED)
                for t_var in type_vars:
                    bounded_type_var = TypeVarNode(type_var_id, t_var, False)
                    construct_edge(self.type_graph, source, bounded_type_var,
                                   Edge.INFERRED)
            type_var_nodes[t_param] = source
            target = TypeNode(t.type_args[i])
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
                TypeNode(node.class_type))
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
                TypeNode(node.class_type))
            return

        main_node, type_var_nodes = (
            self._handle_type_constructor_instantiation(node, parent_node_id)
        )
        self._infer_type_variables_by_call_arguments(node_id, class_decl,
                                                     type_var_nodes,
                                                     inferred_fields)
        if self._exp_type:
            target = self._convert_type_to_node(self._exp_type, main_node,
                                                parent_node_id)
            self._remove_declared_edge(parent_node_id)
            self._inferred_nodes[parent_node_id].append(target)
