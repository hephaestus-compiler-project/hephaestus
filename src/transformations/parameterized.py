import random
from dataclasses import dataclass
from typing import List

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


def get_type_params_names(total):
    random_caps = []
    for _ in range(0, total):
        random_caps += utils.random.caps(1, random_caps)
    return random_caps


def create_type_parameter(name: str, type_constraint: types.Type, variance):
    bound = None
    if type_constraint is not None and random.random() < .5:
        bound = random.choice(list(type_constraint.get_supertypes()))
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


def get_field_param_decls(context, namespace, decls):
    """Get all the field and parameter declaration in a namespace
    and namespace's children, etc.
    """
    # TODO move some logic from here to context
    for dname, dnode in context.get_declarations(namespace, True).items():
        new_namespace = namespace + (dname,)
        if type(dnode) in (ast.FieldDeclaration, ast.ParameterDeclaration):
            decls.add((namespace, dnode))
        if type(dnode) == ast.FunctionDeclaration:
            decls.update(get_field_param_decls(context, new_namespace, decls))
        namespace = namespace
    return decls


# TODO This functionality must be provided by context.
# This function is *incomplete*
def hard_update_context_variable(context, namespace, decl):
    context.add_var(namespace, decl.name, decl)
    parent = namespace[-1]
    namespace = namespace[:-1]
    parent_decl = context.get_decl(namespace, parent)
    if type(parent_decl) == ast.ClassDeclaration:
        if type(decl) == ast.FieldDeclaration:
            d = next(d for d in parent_decl.fields if decl.name == d.name)
            d.field_type = decl.field_type
    elif type(parent_decl) == ast.FunctionDeclaration:
        if type(decl) == ast.ParameterDeclaration:
            d = next(d for d in parent_decl.params if decl.name == d.name)
            d.param_type = decl.param_type


def get_connected_type_param(use_graph, type_params, gnode):
    if gnode in use_graph:
        for tp in type_params:
            if (tp.node is not None and
                gutils.connected(use_graph, gnode, tp.node)):
                return tp.type_param
    return None


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

    def __init__(self, max_type_params=3):
        super(ParameterizedSubstitution, self).__init__()
        self._max_type_params: int = max_type_params

        self._selected_class_decl: ast.ClassDeclaration = None
        self._type_constructor_decl: ast.ClassDeclaration = None
        self._parameterized_type: types.ParameterizedType = None

        self._type_params: List[TP] = []

        self._use_graph: dict = None

        # Use it as a flag to do specific operations when visiting nodes to
        # select which variables to replace their types with TypeParameters
        self._in_select_type_params: bool = False
        #  self._in_override: bool = False

        self._namespace: tuple = ast.GLOBAL_NAMESPACE
        self.program = None

    def result(self):
        return self.program

    def get_candidates_classes(self):
        """Get all simple classifier declarations."""
        return [d for d in self.program.declarations
                if (isinstance(d, ast.ClassDeclaration) and
                type(d.get_type()) is types.SimpleClassifier)]

    def _create_parameterized_type(self) -> types.ParameterizedType:
        """Create ParameterizedType from _type_constructor_decl based on
        type_params constraints
        """
        type_args = []
        for tp in self._type_params:
            if tp.constraint is None:
                possible_types = kt.NonNothingTypes
            else:
                # TODO check the code about variance
                if tp.variance == INVARIANT:
                    type_args.append(tp.constraint)
                    continue
                possible_types = []
                if tp.variance == CONTRAVARIANT:
                    possible_types = list(tp.constraint.get_supertypes())
                if tp.variance == COVARIANT:
                    possible_types = tu.find_subtypes(tp.constraint,
                                                      self.types, True)
                    possible_types += [bt for bt in kt.NonNothingTypes
                                       if bt.is_subtype(tp.constraint)]
                if tp.type_param.bound:
                    possible_types = [t for t in possible_types
                                      if t.is_subtype(tp.type_param.bound)]
            type_args.append(random.choice(possible_types))
        return types.ParameterizedType(self._type_constructor_decl.get_type(),
                                       type_args)

    def _propagate_type_parameter(self, gnode: GNode, tp: types.TypeParameter):
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
                setattr(decl, attr, tp)

    def _use_type_parameter(self, namespace, node, t, covariant=False):
        """Select a node to replace its concrete type with a type parameter.

        * Check if node can be used
        * Initialize type parameter
        * Propagate type parameter to connected nodes
        """
        #  if self._in_override:
            #  return t
        gnode = GNode(namespace, node.name)

        if gutils.none_connected(self._use_graph, gnode):
            return t

        # Check if there is a connected (reachable++) type parameter
        connected_type_param = get_connected_type_param(
            self._use_graph, self._type_params, gnode)
        if connected_type_param:
            return connected_type_param

        if utils.random.bool():
            return t

        for tp in self._type_params:
            if tp.constraint is None:
                # TODO handle variance
                variance = INVARIANT
                tp.constraint = t
                tp.variance = variance
                tp.type_param = create_type_parameter(tp.name, t, variance)
                tp.node = (namespace, node.name)
                self._propagate_type_parameter(gnode, tp.type_param)
                return tp.type_param
        return t

    def _update_type(self, node, attr):
        """Replace _selected_class type occurrences with _parameterized_type
        """
        attr_type = getattr(node, attr, None)
        if not attr_type:
            return node
        new_type = tu.update_type(attr_type, self._parameterized_type)
        setattr(node, attr, new_type)
        return node

    def _initialize_uninitialize_type_params(self):
        for tp in self._type_params:
            if tp.type_param is None:
                tp.type_param = create_type_parameter(
                    tp.name, None, INVARIANT)

    def _select_type_params(self, node) -> ast.Node:
        # To use this instead of visiting the whole program to select which
        # variables to change their types to type parameters we must be able
        # to do complete updates in the context.
        #  namespace = self._namespace + (node.name,)
        #  decls = get_field_param_decls(self.program.context, namespace, set())
        #  for ns, ndecl in decls:
            #  if type(ndecl) == ast.FieldDeclaration:
                #  ndecl.field_type = self._use_type_parameter(
                    #  ns, ndecl, ndecl.field_type, True)
            #  else:  # ParameterDeclaration
                #  ndecl.param_type = self._use_type_parameter(
                    #  ns, ndecl, ndecl.param_type)
            #  hard_update_context_variable(self.program.context, ns, ndecl)
        #  node = self.program.context.get_decl(self._namespace, node.name)

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
        #import pprint; pprint.pprint(self._use_graph)

        node = self._select_type_params(node)

        self._initialize_uninitialize_type_params()

        self._type_constructor_decl = create_type_constructor_decl(
            node, [tp.type_param for tp in self._type_params]
        )

        self._parameterized_type = self._create_parameterized_type()

        return self._type_constructor_decl

    def visit_program(self, node):
        """Select which class declaration to replace and select how many
        type parameters to use.
        """
        self.program = node
        classes = self.get_candidates_classes()
        if not classes:
            # There are not user-defined simple classifier declarations.
            return
        class_decl = utils.random.choice(classes)
        self._selected_class_decl = class_decl

        total_type_params = utils.random.integer(1, self._max_type_params)
        self._type_params = [
            TP(name, None, None, None, None)
            for name in get_type_params_names(total_type_params)
        ]

        node = self._analyse_selected_class(self._selected_class_decl)
        self.program.context.add_class(self._namespace, node.name, node)

        return super(ParameterizedSubstitution, self).visit_program(
            self.program)

    @change_namespace
    def visit_class_decl(self, node):
        return super(ParameterizedSubstitution, self).visit_class_decl(node)

    def visit_type_param(self, node):
        if self._in_select_type_params:
            return node
        new_node = super(ParameterizedSubstitution, self).visit_type_param(node)
        return self._update_type(new_node, 'bound')

    def visit_field_decl(self, node):
        # Note that we cannot parameterize a field having the keyword
        # 'override', because this would require the modification of the
        # parent class.
        if self._in_select_type_params:
            if not node.override:
                node.field_type = self._use_type_parameter(
                    self._namespace, node, node.field_type, True)
            return node
        new_node = super(ParameterizedSubstitution, self).visit_field_decl(node)
        return self._update_type(new_node, 'field_type')

    def visit_param_decl(self, node):
        if self._in_select_type_params:
            node.param_type = self._use_type_parameter(
                self._namespace, node, node.param_type)
            return node
        new_node = super(ParameterizedSubstitution, self).visit_param_decl(node)
        return self._update_type(new_node, 'param_type')

    def visit_var_decl(self, node):
        if self._in_select_type_params:
            return node
        new_node = super(ParameterizedSubstitution, self).visit_var_decl(node)
        new_node = self._update_type(new_node, 'var_type')
        return self._update_type(new_node, 'inferred_type')

    @change_namespace
    def visit_func_decl(self, node):
        # Again, we do not update the parameters and return types of
        # override functions, because this would require the mofication of
        # the parent class.
        if self._in_select_type_params and node.override:
            return node
        new_node = super(ParameterizedSubstitution, self).visit_func_decl(node)
        if self._in_select_type_params:
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
        #  self._in_override = False
        return new_node

    def visit_new(self, node):
        if self._in_select_type_params:
            return node
        new_node = super(ParameterizedSubstitution, self).visit_new(node)
        return self._update_type(new_node, 'class_type')

    def visit_super_instantiation(self, node):
        if self._in_select_type_params:
            return node
        new_node = super(ParameterizedSubstitution,
                         self).visit_super_instantiation(node)
        return self._update_type(new_node, 'class_type')

    def visit_is(self, node):
        if self._in_select_type_params:
            return node
        new_node = super(ParameterizedSubstitution,
                         self).visit_is(node)
        return self._update_type(new_node, 'rexpr')
