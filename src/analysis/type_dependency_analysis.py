from collections import defaultdict
from typing import NamedTuple, Union, Tuple, Dict, List

from src.ir import ast, types as tp
from src.ir.context import get_decl
from src.ir.visitors import DefaultVisitor
from src.transformations.base import change_namespace


class TypeVarNode(NamedTuple):
    node_id: str
    t: tp.TypeParameter
    is_decl: bool

    def __str__(self):
        node_id = self.node_id + "/" + self.t.name
        prefix = "!" if self.is_decl else ""
        return prefix + "TypeVariable[{}]".format(node_id)

    def __repr__(self):
        return self.__str__()


class TypeNode(NamedTuple):
    t: tp.Type

    def __str__(self):
        return "Type[{}]".format(self.t.name)

    def __repr__(self):
        return self.__str__()


class DeclarationNode(NamedTuple):
    namespace: Tuple[str, ...]
    decl: ast.Declaration

    def __str__(self):
        node_id = "/".join(self.namespace) + "/" + self.decl.name
        return "Declaration[{}]".format(node_id)

    def __repr__(self):
        return self.__str__()


class TypeConstructorInstantiationCallNode(NamedTuple):
    node_id: str
    t: tp.ParameterizedType
    constructor_call: ast.New

    def __str__(self):
        node_id = self.node_id + "/" + self.t.name
        return "TypeConInstCall[{}]".format(node_id)

    def __repr__(self):
        return self.__str__()


class TypeConstructorInstantiationDeclNode(NamedTuple):
    node_id: str
    t: tp.ParameterizedType

    def __str__(self):
        node_id = self.node_id + "/" + self.t.name
        return "TypeConInstDecl[{}]".format(node_id)

    def __repr__(self):
        return self.__str__()


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


class TypeDependencyAnalysis(DefaultVisitor):
    def __init__(self, program, bt_factory):
        self._bt_factory = bt_factory
        self.type_graph: Dict[
            Union[
                TypeNode,
                TypeVarNode,
                DeclarationNode,
                TypeConstructorInstantiationCallNode,
                TypeConstructorInstantiationDeclNode
            ],
            List[Edge]
        ] = {}
        self.program = program
        self._context = self.program.context
        self._namespace = ast.GLOBAL_NAMESPACE
        self._stack: list = []
        self._inferred_nodes: dict = defaultdict(list)
        self._exp_type: tp.Type = None

    def result(self):
        return self.type_graph

    def _construct_node_id(self):
        top_stack = self._stack[-1]
        f = "/".join(self._namespace) + "/" + top_stack
        return f

    def _convert_type_to_node(self, t, infer_t, node_id):
        if not t.is_parameterized():
            return TypeNode(t)

        if not isinstance(infer_t, TypeConstructorInstantiationCallNode):
            return TypeNode(t)

        if t.name == infer_t.t.name:
            main_node = TypeConstructorInstantiationDeclNode(node_id, t)
            for i, t_param in enumerate(t.t_constructor.type_parameters):
                source = TypeVarNode(node_id, t_param, True)
                target_var = TypeVarNode(node_id, t_param, False)
                if target_var in self.type_graph:
                    construct_edge(self.type_graph, source, target_var,
                                   Edge.INFERRED)
                target = TypeNode(t.type_args[i])
                construct_edge(self.type_graph, source, target, Edge.DECLARED)
                construct_edge(self.type_graph, main_node, source,
                               Edge.DECLARED)
            return main_node

    def visit_integer_constant(self, node):
        node_id = self._construct_node_id()
        self._inferred_nodes[node_id].append(TypeNode(node.integer_type))

    def visit_real_constant(self, node):
        node_id = self._construct_node_id()
        self._inferred_nodes[node_id].append(TypeNode(node.real_type))

    def visit_string_constant(self, node):
        node_id = self._construct_node_id()
        self._inferred_nodes[node_id].append(
            TypeNode(self._bt_factory.get_string_type()))

    def visit_boolean_constant(self, node):
        node_id = self._construct_node_id()
        self._inferred_nodes[node_id].append(
            TypeNode(self._bt_factory.get_boolean_type()))

    def visit_char_constant(self, node):
        node_id = self._construct_node_id()
        self._inferred_nodes[node_id].append(
            TypeNode(self._bt_factory.get_char_type()))

    def visit_variable(self, node):
        decl = get_decl(self.program.context,
                        self._namespace, node.name)
        if not decl:
            # If we cannot find declaration in context, then abort.
            return
        namespace, decl = decl
        node_id = self._construct_node_id()
        self._inferred_nodes[node_id].append(
            DeclarationNode(namespace, decl)
        )

    def visit_var_decl(self, node):
        self._stack.append(node.name)
        node_id = self._construct_node_id()
        self._exp_type = node.var_type
        super().visit_var_decl(node)
        self._stack.pop()
        source = DeclarationNode(self._namespace, node)

        inferred_nodes = self._inferred_nodes.pop(node_id)
        added_declared = False
        for n in inferred_nodes:
            edge_label = (
                Edge.DECLARED
                if isinstance(n, TypeConstructorInstantiationDeclNode)
                else Edge.INFERRED
            )
            if edge_label == Edge.DECLARED:
                added_declared = True
            construct_edge(self.type_graph, source, n, edge_label)

        if not added_declared and node.var_type is not None:
            construct_edge(self.type_graph, source,
                           TypeNode(node.var_type), Edge.DECLARED)

    def visit_field_decl(self, node):
        source = DeclarationNode(self._namespace, node)
        target = TypeNode(node.get_type())
        construct_edge(self.type_graph, source, target, Edge.DECLARED)
        return super().visit_field_decl(node)

    def visit_param_decl(self, node):
        source = DeclarationNode(self._namespace, node)
        target = TypeNode(node.get_type())
        construct_edge(self.type_graph, source, target, Edge.DECLARED)
        return super().visit_param_decl(node)

    @change_namespace
    def visit_class_decl(self, node):
        return super().visit_class_decl(node)

    @change_namespace
    def visit_func_decl(self, node):
        return super().visit_func_decl(node)

    def visit_new(self, node):
        # First, we use the context to retrieve the declaration of the class
        # we initialize in this node
        class_decl = get_decl(self._context, self._namespace,
                              node.class_type.name)
        assert class_decl is not None
        namespace, class_decl = class_decl

        node_id = self._construct_node_id()
        for i, c in enumerate(node.children()):
            field_type = class_decl.fields[i].get_type()
            prev = self._exp_type
            self._exp_type = field_type
            self._stack.append(
                class_decl.name + "/" + class_decl.fields[i].name)
            self.visit(c)
            self._exp_type = prev
            self._stack.pop()

        if not node.class_type.is_parameterized():
            # We initialize a simple class, so there's nothing special to
            # do here.
            self._inferred_nodes[node_id].append(TypeNode(node.class_type))
            return

        main_node = TypeConstructorInstantiationCallNode(
            node_id, node.class_type, node)
        self._inferred_nodes[node_id].append(main_node)  # TODO revisit
        t = node.class_type
        type_var_nodes = {}
        for i, t_param in enumerate(t.t_constructor.type_parameters):
            source = TypeVarNode(node_id, t_param, False)
            type_var_nodes[t_param] = source
            target = TypeNode(t.type_args[i])
            construct_edge(self.type_graph, main_node, source, Edge.DECLARED)
            construct_edge(self.type_graph, source, target, Edge.DECLARED)
        for i, f in enumerate(class_decl.fields):
            if not f.get_type().is_type_var():
                continue
            source = type_var_nodes[t_param]

            field_node_id = "/".join(
                ("/".join(self._namespace),
                 class_decl.name,
                 class_decl.fields[i].name)
            )
            inferred_nodes = self._inferred_nodes.pop(field_node_id)
            for n in inferred_nodes:
                construct_edge(self.type_graph, source, n, Edge.INFERRED)
        if self._exp_type:
            target = self._convert_type_to_node(self._exp_type, main_node,
                                                node_id)
            self._inferred_nodes[node_id].append(target)
