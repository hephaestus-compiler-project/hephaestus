from collections import defaultdict
from typing import NamedTuple, Union, Dict, List

from src.ir import ast, types as tp, type_utils as tu
from src.ir.context import get_decl
from src.ir.visitors import DefaultVisitor
from src.transformations.base import change_namespace


RET = "__RET__"


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
    node_id: str
    decl: ast.Declaration

    def __str__(self):
        node_id = self.node_id + "/" + self.decl.name
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
        self._types = self.program.get_types()
        self._stack: list = []
        self._inferred_nodes: dict = defaultdict(list)
        self._exp_type: tp.Type = None

    def result(self):
        return self.type_graph

    def _get_node_id(self):
        try:
            top_stack = self._stack[-1]
        except:
            import pdb; pdb.set_trace()
        return top_stack

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
            type_var_id = n.node_id.rsplit("/", 1)[1] + "." + n.t.name
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
        node_id = self._get_node_id()
        self._inferred_nodes[node_id].append(TypeNode(node.integer_type))

    def visit_real_constant(self, node):
        node_id = self._get_node_id()
        self._inferred_nodes[node_id].append(TypeNode(node.real_type))

    def visit_string_constant(self, node):
        node_id = self._get_node_id()
        self._inferred_nodes[node_id].append(
            TypeNode(self._bt_factory.get_string_type()))

    def visit_boolean_constant(self, node):
        node_id = self._get_node_id()
        self._inferred_nodes[node_id].append(
            TypeNode(self._bt_factory.get_boolean_type()))

    def visit_char_constant(self, node):
        node_id = self._get_node_id()
        self._inferred_nodes[node_id].append(
            TypeNode(self._bt_factory.get_char_type()))

    def visit_variable(self, node):
        decl = get_decl(self.program.context,
                        self._namespace, node.name)
        if not decl:
            # If we cannot find declaration in context, then abort.
            return
        namespace, decl = decl
        node_id = self._get_node_id()
        self._inferred_nodes[node_id].append(
            DeclarationNode("/".join(namespace), decl)
        )

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

        if not added_declared and node_type is not None:
            if getattr(node, 'inferred_type', False) is not False:
                # Add this edge only if the type declaration is omittable,
                # i.e., for variables
                construct_edge(self.type_graph, source,
                               TypeNode(node_type), Edge.DECLARED)
        self._exp_type = prev

    def visit_var_decl(self, node):
        self._handle_declaration("/".join(self._namespace),
                                 node, node.expr, 'var_type')

    def visit_field_decl(self, node):
        source = DeclarationNode("/".join(self._namespace), node)
        target = TypeNode(node.get_type())
        construct_edge(self.type_graph, source, target, Edge.DECLARED)
        return super().visit_field_decl(node)

    def visit_param_decl(self, node):
        source = DeclarationNode("/".join(self._namespace), node)
        target = TypeNode(node.get_type())
        construct_edge(self.type_graph, source, target, Edge.DECLARED)
        return super().visit_param_decl(node)

    @change_namespace
    def visit_class_decl(self, node):
        return super().visit_class_decl(node)

    @change_namespace
    def visit_func_decl(self, node):

        children = node.children()
        if node.body is not None:
            children = children[:-1]

        for c in children:
            self.visit(c)

        if node.get_type() == self._bt_factory.get_void_type():
            # If the body of function returns void, we cannot omit the
            # return type of the function. So, we simply visit its body.
            self.visit(node.body)

        node_id = "/".join(self._namespace)

        # We create a "virtual" variable declaration representing the return
        # value of the function.
        ret_decl = ast.VariableDeclaration(RET, node.body, is_final=True,
                                           var_type=node.get_type())
        self._handle_declaration(node_id, ret_decl, node.body,
                                 'var_type')

    def visit_field_access(self, node):
        parent_node_id = self._get_node_id()
        node_id = parent_node_id + "/" + node.f
        self._stack.append(node_id)
        super().visit_field_access(node)
        self._stack.pop()
        self._inferred_nodes[parent_node_id].append(
            TypeNode(tu.get_type_hint(node, self._context, self._namespace,
                                      self._bt_factory, self._types))
        )

    def visit_func_call(self, node):
        parent_node_id = self._get_node_id()
        node_id = parent_node_id + "/" + node.func
        fun_decl = get_decl(self._context, self._namespace,
                            node.func)
        assert fun_decl is not None
        namespace, fun_decl = fun_decl

        for i, c in enumerate(node.children()):
            self._handle_declaration(node_id, fun_decl.params[i],
                                     c, 'param_type')
        self._inferred_nodes[parent_node_id].append(
            TypeNode(tu.get_type_hint(node, self._context, self._namespace,
                                      self._bt_factory, self._types))
        )

    def _infer_type_variables_by_call_arguments(self, node_id, class_decl,
                                                type_var_nodes):
        # Add this point, we furher examine the fields of the constructor to
        # see if any of its type variables can be inferred by the arguments
        # passed in the constructor invocation, i.e., A<String>(x)
        for i, f in enumerate(class_decl.fields):
            if not f.get_type().is_type_var():
                continue
            source = type_var_nodes[f.get_type()]

            inferred_nodes = self.type_graph[DeclarationNode(node_id, f)]
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
            type_var_nodes[t_param] = source
            target = TypeNode(t.type_args[i])
            # This edge connects type constructor with its type variables.
            construct_edge(self.type_graph, main_node, source, Edge.DECLARED)
            # This edge connects every type variable with the type arguments
            # with which it is explicitly instantiated.
            construct_edge(self.type_graph, source, target, Edge.DECLARED)
        return main_node, type_var_nodes

    def visit_new(self, node):
        # First, we use the context to retrieve the declaration of the class
        # we initialize in this node
        class_decl = get_decl(self._context, self._namespace,
                              node.class_type.name)
        assert class_decl is not None
        namespace, class_decl = class_decl

        parent_node_id = self._get_node_id()
        node_id = parent_node_id + "/" + class_decl.name
        # First we visit the children of this node (i.e., its arguments),
        # and handle them as declarations.
        for i, c in enumerate(node.children()):
            self._handle_declaration(node_id, class_decl.fields[i], c,
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
                                                     type_var_nodes)
        if self._exp_type:
            target = self._convert_type_to_node(self._exp_type, main_node,
                                                parent_node_id)
            self._inferred_nodes[parent_node_id].append(target)
