import random
from collections import defaultdict
from dataclasses import dataclass
from typing import Tuple, List, NamedTuple, Set

from src import utils
from src.ir import ast
from src.ir import types
from src.ir import kotlin_types as kt
import src.graph_utils as gutils
from src.transformations.base import Transformation, change_namespace
from src.analysis.use_analysis import UseAnalysis, GNode, FUNC_RET
from src.utils import lst_get


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
    # TODO: add bounds
    # Bounds were SimpleClassifier when it should be ParameterizedType
    #  if type_constraint is not None and random.random() < .5:
        #  bound = random.choice(list(type_constraint.get_supertypes()))
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
    and in namespace's children, etc.
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
        2. Select how many TypeParameters we'll use (visit_program)
        3. We choose where we will use the TypeParameters in the body of the
           selected SimpleClassifier. Currently, we select only
           FieldDeclarations, and FunctionDeclarations. Every time we choose
           to replace a concrete type with a TypeParameter, we add the
           corresponding constraints for the specific TypeParameter.
           For example, suppose we replace the return type of a function.
           In that case, the type argument for the specific TypeParameter must
           have the same type as the return type we replaced, or we can specify
           the TypeParameter to be covariant and the type argument to be a
           supertype of the replaced return type.
           (_use_type_parameter)
        4. Create the TypeParameters based on the restrictions from step 3.
           (_use_type_parameter)
        5. Create the ParameterizedType with type arguments that respect the
           constraints of TypeParameters.
           (visit_class_decl)
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

        self._in_select_type_params: bool = False

        self._use_graph: dict = None

        #  self._in_override = False
        self._namespace: tuple = ast.GLOBAL_NAMESPACE
        self.program = None

    def get_candidates_classes(self):
        """Get all simple classifier declarations."""
        return [d for d in self.program.declarations
                if (isinstance(d, ast.ClassDeclaration) and
                type(d.get_type()) is types.SimpleClassifier)]

    def result(self):
        return self.program

    def _create_parameterized_type(self) -> types.ParameterizedType:
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
                    possible_types = self.find_subtypes(tp.constraint, True)
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
        """Select node to replace concrete type with type parameter.

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
        for tp in self._type_params:
            if (tp.node is not None and
                gutils.connected(self._use_graph, gnode, tp.node)):
                return tp.type_param

        if utils.random.bool():
            return t

        for tp in self._type_params:
            if tp.constraint is None:
                # TODO handle variance
                variance = INVARIANT
                tp.constraint = t
                tp.variance = variance
                tp.type_param = create_type_parameter(tp.name, t, variance)
                tp.node = (self._namespace, node.name)
                self._propagate_type_parameter(gnode, tp.type_param)
                return tp.type_param
        return t

    def _update_type(self, node, attr):
        """Update types in the program.

        Change _selected_class to _parameterized_type
        """
        attr_type = getattr(node, attr, None)
        if attr_type:
            # 1
            if attr_type == self._selected_class_decl.get_type():
                setattr(node, attr, self._parameterized_type)
            elif isinstance(attr_type, types.ParameterizedType):
                attr_type.type_args = [
                    self._parameterized_type
                    if t == self._selected_class_decl.get_type() else t
                    for t in attr_type.type_args
                ]
                setattr(node, attr, attr_type)
        return node

    def _initialize_uninitialize_type_params(self):
        for tp in self._type_params:
            if tp.type_param is None:
                tp.type_param = create_type_parameter(
                    tp.name, None, INVARIANT)

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
        __import__('pprint').pprint(self._use_graph)  # DEBUG

        self._in_select_type_params = True
        #  namespace = self._namespace + (node.name,)
        #  decls = get_field_param_decls(self.program.context, namespace, set())
        #  for ns, ndecl in decls:
            #  if type(ndecl) == ast.FieldDeclaration:
                #  ndecl.field_type = self._use_type_parameter(
                    #  ns, ndecl, ndecl.field_type, True)
            #  else:  # ParameterDeclaration
                #  ndecl.param_type = self._use_type_parameter(
                    #  ns, ndecl, ndecl.param_type)
            #  self.program.context.add_var(ns, ndecl.name, ndecl)
        # Get the updated node
        #  node = self.program.context.get_decl(self._namespace, node.name)
        node = self.visit_class_decl(node)
        self._in_select_type_params = False

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

    def visit_field_decl(self, node):
        if self._in_select_type_params:
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
        new_node = super(ParameterizedSubstitution, self).visit_var_decl(node)
        return self._update_type(new_node, 'var_type')

    @change_namespace
    def visit_func_decl(self, node):
        #  if node.override:
            #  self._in_override = True
        new_node = super(ParameterizedSubstitution, self).visit_func_decl(node)
        return_gnode = GNode(self._namespace, FUNC_RET)
        ret_type = None
        if return_gnode in self._use_graph:
            for tp in self._type_params:
                if (tp.node is not None and
                    gutils.connected(self._use_graph, return_gnode, tp.node)):
                    ret_type = tp.type_param
        if ret_type:
            new_node.ret_type = ret_type
            new_node.inferred_type = ret_type
        #  self._in_override = False
        new_node = self._update_type(new_node, 'ret_type')
        new_node = self._update_type(new_node, 'inferred_type')
        return new_node

    def visit_new(self, node):
        new_node = super(ParameterizedSubstitution, self).visit_new(node)
        return self._update_type(new_node, 'class_type')

    def visit_super_instantiation(self, node):
        new_node = super(ParameterizedSubstitution, self).visit_super_instantiation(node)
        return self._update_type(new_node, 'class_type')
