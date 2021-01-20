# pylint: disable=too-many-instance-attributes
from dataclasses import dataclass
from typing import List
from copy import deepcopy

from src import utils
from src.ir import ast
from src.ir import types, type_utils as tu
from src.ir import kotlin_types as kt
import src.graph_utils as gutils
from src.transformations.base import Transformation, change_namespace
from src.analysis.use_analysis import UseAnalysis, GNode, FUNC_RET


INVARIANT = types.TypeParameter.INVARIANT
COVARIANT = types.TypeParameter.COVARIANT
CONTRAVARIANT = types.TypeParameter.CONTRAVARIANT
VARIANCE = (INVARIANT, COVARIANT, CONTRAVARIANT)


def get_type_params_names(total):
    random_caps = []
    for _ in range(0, total):
        random_caps += utils.random.caps(1, random_caps)
    return random_caps


def create_type_parameter(name: str, type_constraint: types.Type, ptypes,
                          variance):
    def bounds_filter(bound):
        # In case the constraint is a parameterized type, then we should check
        # that the bound confronts to the constraints of type_constraint's
        # type constructor.
        if isinstance(bound, types.ParameterizedType):
            type_params = bound.t_constructor.type_parameters
            for targ, tparam in zip(bound.type_args, type_params):
                # Handle case where targ is ParameterizedType recursively.
                if (isinstance(targ, types.ParameterizedType) and
                        not bounds_filter(targ)):
                    return False
                # In some odd/rare cases (~1/1000) targ is an abstract type.
                # In those cases return False
                if isinstance(targ, types.AbstractType):
                    return False
                if tparam.bound and not targ.is_subtype(tparam.bound):
                    return False
        return True
    bound = None
    if utils.random.bool():
        if type_constraint is None:
            bound = utils.random.choice(kt.NonNothingTypes)
        else:
            candidate_bounds = list(
                filter(bounds_filter,
                       tu.find_supertypes(type_constraint,
                                          ptypes,
                                          include_self=True,
                                          concrete_only=True)))
            if candidate_bounds:
                bound = utils.random.choice(candidate_bounds)
    return types.TypeParameter(name, variance, bound)


def create_type_constructor_decl(class_decl, type_parameters):
    return ast.ClassDeclaration(
        class_decl.name, class_decl.superclasses,
        class_type=class_decl.class_type,
        fields=class_decl.fields,
        functions=class_decl.functions,
        is_final=class_decl.is_final,
        type_parameters=type_parameters
    )


def get_connected_type_param(use_graph, type_params, gnode):
    if gnode in use_graph:
        for tp in type_params:
            if (tp.node is not None and
                    gutils.connected(use_graph, gnode, tp.node)):
                return tp.type_param
    return None


def get_variance(context, use_graph, node):
    variance = INVARIANT
    # Find all source nodes of the node, i.e., top level-nodes that have a flow
    # to the node.
    source_nodes = gutils.find_sources(use_graph, node)
    # Find all nodes that are connected with the node.
    connected_nodes = gutils.find_all_connected(use_graph, node)
    sn_decl = [context.get_decl(n.namespace, n.name) for n in source_nodes]
    cn_decl = [context.get_decl(n.namespace, n.name) for n in connected_nodes]
    # Final FieldDeclaration (val) is an 'out' position (covariant)
    # FieldDeclaration (var) is an 'invariant' position (covariant)
    # ParameterDeclaration is an 'in' position (contravariant)
    # Return is an 'out' position (covariant)
    # If all source nodes of the node are final FieldDeclarations and none of
    # its connected nodes is ParameterDeclaration, then the type parameter can
    # be covariant.
    if (all(isinstance(s, ast.FieldDeclaration) and s.is_final
            for s in sn_decl)
            and not any(isinstance(c, ast.ParameterDeclaration)
                        for c in cn_decl)
            and utils.random.bool()):
        variance = COVARIANT
    # if all source nodes are ParameterDeclaration and none of its connected
    # nodes is a RETURN node, then the type parameter can be contravariant.
    elif (all(isinstance(s, ast.ParameterDeclaration) for s in sn_decl)
          and not any(n.name == FUNC_RET for n in connected_nodes)
          and utils.random.bool()):
        variance = CONTRAVARIANT
    return variance


@dataclass
class TP:
    """Data class to save Type Parameters and their constraints"""
    name: str
    type_param: types.TypeParameter
    node: GNode
    constraint: types.Type
    variance: int  # INVARIANT, COVARIANT, CONTRAVARIANT


class ParameterizedSubstitution(Transformation):
    """To create a ParameterizedType, we do the following steps:

        1. Select a SimpleClassifier ClassDeclaration (visit_program)
        2. Select how many TypeParameters to use (visit_program)
        3. Run _analyse_selected_class to: (a) select which variables to
           convert to TypeParameters, (b) propagate TypeParameters inside class
           (c) create TypeConstructor, and (d) create ParameterizedType
        4. Visit program to update occurrences of selected_class type to
           the new ParameterizedType
    """
    CORRECTNESS_PRESERVING = True
    NAME = 'Parameterized Substitution'

    def __init__(self, program, logger=None, max_type_params=3,
                 find_classes_blacklist=True):
        super().__init__(program, logger)
        self._max_type_params: int = max_type_params

        self._selected_class_decl: ast.ClassDeclaration = None
        self._type_constructor_decl: ast.ClassDeclaration = None
        self._parameterized_type: types.ParameterizedType = None

        self._type_params: List[TP] = []

        self._use_graph: dict = None

        # Use it as a flag to do specific operations when visiting nodes to
        # select which variables to replace their types with TypeParameters
        self._in_select_type_params: bool = False
        self._in_find_classes_blacklist: bool = False
        self.find_classes_blacklist = find_classes_blacklist
        self._blacklist_classes = set()

        self._namespace: tuple = ast.GLOBAL_NAMESPACE

    def _discard_node(self):
        return self._in_select_type_params or self._in_find_classes_blacklist

    def get_candidates_classes(self):
        """Get all simple classifier declarations."""
        # pylint: disable=unidiomatic-typecheck
        classes = {d for d in self.program.declarations
                   if (isinstance(d, ast.ClassDeclaration) and
                       type(d.get_type()) is types.SimpleClassifier)}
        return list(classes.difference(self._blacklist_classes))

    def _create_parameterized_type(self) -> types.ParameterizedType:
        """Create ParameterizedType from _type_constructor_decl based on
        type_params constraints
        """
        type_args = []
        for tp in self._type_params:
            type_arg = None
            if tp.variance == INVARIANT:
                type_arg = tp.constraint if tp.constraint else \
                    utils.random.choice(kt.NonNothingTypes)
                type_args.append(type_arg)
                continue
            if tp.constraint is None:
                possible_types = kt.NonNothingTypes
            else:
                possible_types = []
                if tp.variance == CONTRAVARIANT:
                    possible_types = tu.find_supertypes(
                        tp.constraint, self.types, include_self=True,
                        concrete_only=True)
                if tp.variance == COVARIANT:
                    possible_types = tu.find_subtypes(
                        tp.constraint, self.types, True, concrete_only=True)
                # To preserve correctness, the only possible type is
                # tp.constraint. For example,
                #
                # class A<T : Number>
                # val x: Number = 1
                # val y: A<Int> = A<Int>(x)
                #
                # does not compile.
                #
                # To use any other type, we must be sure that any argument is
                # of the newly selected type. For example, in the previous
                # example, if we update val x to be Int, then it will work.
                #
                # class A<T : Number>
                # val x: Int = 1
                # val y: A<Int> = A<Int>(x)
                #
                # compiles successfully. Hence to use other types we must do
                # more changes.
                possible_types = [tp.constraint]
            if tp.type_param.bound:
                possible_types = [t for t in possible_types
                                  if t.is_subtype(tp.type_param.bound)]
            type_args.append(utils.random.choice(list(possible_types)))
        return types.ParameterizedType(self._type_constructor_decl.get_type(),
                                       type_args)

    def _propagate_type_parameter(self, gnode: GNode,
                                  type_param: types.TypeParameter):
        """Replace concrete types of gnode's connected nodes with tp
        """
        types_lookup = {ast.VariableDeclaration: 'var_type',
                        ast.ParameterDeclaration: 'param_type',
                        ast.FieldDeclaration: 'field_type'}
        for node in gutils.find_all_connected(self._use_graph, gnode):
            if node.is_none():
                continue
            decl = self.program.context.get_decl(
                node.namespace, node.name)
            if decl:
                attr = types_lookup.get(type(decl))
                setattr(decl, attr, type_param)

    def _use_type_parameter(self, namespace, node, old_type):
        """Select a node to replace its concrete type with a type parameter.

        * Check if node can be used
        * Initialize type parameter
        * Propagate type parameter to connected nodes
        """
        gnode = GNode(namespace, node.name)

        if gutils.none_connected(self._use_graph, gnode):
            return old_type

        # Check if there is a connected (reachable++) type parameter
        connected_type_param = get_connected_type_param(
            self._use_graph, self._type_params, gnode)
        if connected_type_param:
            return connected_type_param

        if utils.random.bool():
            return old_type

        for tp in self._type_params:
            if tp.constraint is None:
                tp.constraint = old_type
                tp.node = GNode(namespace, node.name)
                tp.variance = get_variance(
                    self.program.context, self._use_graph, tp.node)
                tp.type_param = create_type_parameter(
                    tp.name, old_type, self.types, tp.variance)
                self._propagate_type_parameter(gnode, tp.type_param)
                return tp.type_param
        return old_type

    def _check_new_infer(self, node: ast.New):
        """In case of ParameterizedType check if type arguments can be inferred.
        """
        # Check if all type parameters of constructor are used in field
        # declarations.
        # For example, in this case we can infer the type of type arguments
        #   class A<T, K> (val x: T, val y: K)
        #   val a = A("a", if (true) -1 else "a")
        # whereas in the following case we can't
        #   class A<T, K> (val x: T)
        #   val a = A("a") // not enough information to infer type variable K
        # TODO Add randomness
        if (isinstance(node.class_type, types.ParameterizedType) and
                node.class_type.name == self._parameterized_type.name and
                self._type_constructor_decl.all_type_params_in_fields()):
            node.class_type.can_infer_type_args = True
        return node

    def _check_var_decl_infer(self, node: ast.VariableDeclaration):
        """If the expr is a New ParameterizedType check if type arguments
        can be inferred.
        """
        # Check if var_type is set and not a super--sub class.
        # For instance, in the following example we can remove the type arg.
        #   class A<T>
        #   val a: A<String> = A<String>()
        # But in the next one we can't.
        #   open class A
        #   class B<T>: A()
        #   val a: A = B<Int>()
        # TODO Add randomness
        if (node.var_type and
                node.var_type.name == node.expr.class_type.name and
                isinstance(node.expr, ast.New) and
                isinstance(node.expr.class_type, types.ParameterizedType) and
                node.expr.class_type.name == self._parameterized_type.name):
            node.expr.class_type.can_infer_type_args = True
        return node

    def _update_type(self, node, attr):
        """Replace _selected_class type occurrences with _parameterized_type
        """
        attr_type = getattr(node, attr, None)
        if not attr_type:
            return node
        new_type = deepcopy(
            tu.update_type(attr_type, self._parameterized_type))
        setattr(node, attr, new_type)
        return node

    def _initialize_uninitialize_type_params(self):
        for tp in self._type_params:
            if tp.type_param is None:
                tp.type_param = create_type_parameter(
                    tp.name, None, self.types, utils.random.choice(VARIANCE))

    def _select_type_params(self, node) -> ast.Node:
        self._in_select_type_params = True
        node = self.visit_class_decl(node)
        self._in_select_type_params = False
        return node

    def _analyse_selected_class(self, node) -> ast.ClassDeclaration:
        """Analyse selected class by following the next steps:

        * Run def-use analysis
        * Select where to use type parameters
        * Initialize the uninitialized type parameters
        * Create the type constructor
        * Create the parameterized type
        """
        analysis = UseAnalysis(self.program)
        analysis.visit(node)
        self._use_graph = analysis.result()
        self.log(self._use_graph)

        node = self._select_type_params(node)

        self._initialize_uninitialize_type_params()

        self._type_constructor_decl = create_type_constructor_decl(
            node, [tp.type_param for tp in self._type_params]
        )

        self._parameterized_type = self._create_parameterized_type()

        return self._type_constructor_decl

    def visit_program(self, node):
        """Select which class declaration to replace, and select how many
        type parameters to use.
        """
        if self.find_classes_blacklist:
            # If find_classes_blacklist is True, we need to perform one
            # pass to the AST, to find blacklisted classes, i.e., classes
            # that cannot be parameterized.
            # These classes are those included in an Is expression
            # e.g., if (x is Foo). In this example, Foo cannot be parameterized
            # because we cannot convert the Is expression as
            # if (x is Foo<TypeArg>) due to type erasure.
            self._in_find_classes_blacklist = True
            super().visit_program(node)
            self._in_find_classes_blacklist = False
        classes = self.get_candidates_classes()
        if not classes:
            # There are not user-defined simple classifier declarations.
            return None
        self.is_transformed = True
        class_decl = utils.random.choice(classes)
        self._selected_class_decl = class_decl

        total_type_params = utils.random.integer(1, self._max_type_params)
        self._type_params = [
            TP(name, None, None, None, None)
            for name in get_type_params_names(total_type_params)
        ]

        node = self._analyse_selected_class(self._selected_class_decl)
        self.program.context.add_class(self._namespace, node.name, node)

        return super().visit_program(self.program)

    @change_namespace
    def visit_class_decl(self, node):
        return super().visit_class_decl(node)

    def visit_type_param(self, node):
        if self._discard_node():
            return node
        new_node = super().visit_type_param(node)
        return self._update_type(new_node, 'bound')

    def visit_field_decl(self, node):
        # Note that we cannot parameterize a field having the keyword
        # 'override', because this would require the modification of the
        # parent class.
        if self._in_select_type_params:
            if not node.override:
                node.field_type = self._use_type_parameter(
                    self._namespace, node, node.get_type())
            return node
        if self._in_find_classes_blacklist:
            return node
        new_node = super().visit_field_decl(node)
        return self._update_type(new_node, 'field_type')

    def visit_param_decl(self, node):
        if self._in_select_type_params:
            node.param_type = self._use_type_parameter(
                self._namespace, node, node.get_type())
            return node
        if self._in_find_classes_blacklist:
            return node
        new_node = super().visit_param_decl(node)
        return self._update_type(new_node, 'param_type')

    def visit_var_decl(self, node):
        if self._in_select_type_params:
            return node
        new_node = super().visit_var_decl(node)
        if self._in_find_classes_blacklist:
            return new_node
        new_node = self._update_type(new_node, 'var_type')
        new_node = self._update_type(new_node, 'inferred_type')
        new_node = self._check_var_decl_infer(new_node)
        return new_node

    @change_namespace
    def visit_func_decl(self, node):
        # Again, we do not update the parameters and return types of
        # override functions, because this would require the mofication of
        # the parent class.
        if self._in_select_type_params and node.override:
            return node
        new_node = super().visit_func_decl(node)
        if self._discard_node():
            return new_node
        return_gnode = GNode(self._namespace, FUNC_RET)

        # Check if return is connected to a type parameter
        ret_type = get_connected_type_param(
            self._use_graph, self._type_params, return_gnode)
        if ret_type:
            new_node.ret_type = ret_type
            new_node.inferred_type = ret_type

        new_node = self._update_type(new_node, 'ret_type')
        new_node = self._update_type(new_node, 'inferred_type')
        return new_node

    def visit_new(self, node):
        if self._in_select_type_params:
            return node
        new_node = super().visit_new(node)
        if self._in_find_classes_blacklist:
            return new_node
        new_node = self._update_type(new_node, 'class_type')
        new_node = self._check_new_infer(new_node)
        return new_node

    def visit_super_instantiation(self, node):
        if self._in_select_type_params:
            return node
        new_node = super().visit_super_instantiation(node)
        if self._in_find_classes_blacklist:
            return new_node
        return self._update_type(new_node, 'class_type')

    def visit_is(self, node):
        if self._in_select_type_params:
            return node
        if self._in_find_classes_blacklist:
            etype = node.rexpr
            class_decl = self.program.context.get_decl(
                ast.GLOBAL_NAMESPACE, etype.name)
            self._blacklist_classes.add(class_decl)
        return super().visit_is(node)
