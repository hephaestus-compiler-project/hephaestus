import random
from collections import defaultdict
from dataclasses import dataclass
from typing import Tuple, List

from src import utils
from src.ir import ast
from src.ir import types
from src.ir import kotlin_types as kt
import src.graph_utils as gutils
from src.transformations.base import Transformation, change_namespace
from src.analysis.use_analysis import UseAnalysis
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


@dataclass
class TP:
    """Data class to save Type Parameters and their constraints"""
    name: str
    type_param: types.TypeParameter
    node: Tuple[Tuple[str, ...], str]
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

        # phases
        self._in_select_type_params: bool = False
        self._use_entries: set = set()  # set of nodes we can use as type params

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
        """Create parameterized type based on type_params, constraints, and
        constructor.
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
                    possible_types = self.find_subtypes(tp.constraint, True)
                    possible_types += [bt for bt in kt.NonNothingTypes
                                       if bt.is_subtype(tp.constraint)]
                if tp.type_param.bound:
                    possible_types = [t for t in possible_types
                                      if t.is_subtype(tp.type_param.bound)]
            type_args.append(random.choice(possible_types))
        return types.ParameterizedType(self._type_constructor_decl.get_type(),
                                       type_args)

    def _use_type_parameter(self, node, t, covariant=False):
        """Replace concrete type with type parameter and add the corresponding
        constraints to type parameters.
        """
        #  if self._in_override:
            #  return t
        gnode = (self._namespace, node.name)

        if gutils.none_connected(self._use_graph, gnode):
            return t

        # Check if there is a connected (reachable++) type parameter
        for tp in self._type_params:
            if (tp.node is not None and
                gutils.connected(self._use_graph, gnode, tp.node)):
                return t

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
                return tp.type_param
        return t

    def _update_type(self, node, attr):
        """Update types in the program.

        This method does the following conversions.

        1. Change _selected_class to _parameterized_type
        2. Update return type for affected functions in _selected_class_decl
        3. Update the type for VariableDeclaration, ParameterDeclaration,
         and FieldDeclaration if there is a flow from a changed type to it

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
            # 2
            elif isinstance(node, ast.FunctionDeclaration):
                return_expr = None
                if isinstance(node.body, ast.Expr):
                    return_expr = node.body
                elif len(node.body.body) > 0:
                    return_expr = node.body.body[-1]
                if type(return_expr) in (ast.Variable, ast.FunctionCall):
                    try:  # Variable
                        name = return_expr.name
                    except AttributeError:  # FunctionCall
                        name = return_expr.func
                    gnode = (self._namespace, name)
                    self._use_graph[gnode] # Safely initialize node
                    match = [tp.type_param
                             for tp in self._type_params
                             if tp.node is not None and
                             gutils.connected(self._use_graph, tp.node, gnode)]
                    # TODO make sure that there cannot be two results
                    if match:
                        setattr(node, attr, match[0])
            # 3
            elif (type(node) == ast.VariableDeclaration or
                  type(node) == ast.ParameterDeclaration or
                  type(node) == ast.FieldDeclaration):
                gnode = (self._namespace, node.name)
                # There can be only one result
                # TODO make sure that there cannot be two results
                match = [tp.type_param
                         for tp in self._type_params
                         if tp.node is not None and
                         gutils.connected(self._use_graph, tp.node, gnode)]
                if match:
                    setattr(node, attr, match[0])
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
        new_node = self.visit_class_decl(node)
        self._in_select_type_params = False

        self._initialize_uninitialize_type_params()
        self._type_constructor_decl = create_type_constructor_decl(
            new_node, [tp.type_param for tp in self._type_params]
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
        """FieldDeclaration nodes can be used to get a TypeParameter type.
        """
        if self._in_select_type_params:
            gnode = (self._namespace, node.name)
            self._use_entries.add(gnode)
            node.field_type = self._use_type_parameter(node, node.field_type, True)
            return super(ParameterizedSubstitution, self).visit_field_decl(node)
        new_node = super(ParameterizedSubstitution, self).visit_field_decl(node)
        return self._update_type(new_node, 'field_type')

    def visit_param_decl(self, node):
        """ParameterDeclaration nodes can be used to get a TypeParameter type.
        """
        if self._in_select_type_params:
            gnode = (self._namespace, node.name)
            self._use_entries.add(gnode)
            node.param_type = self._use_type_parameter(node, node.param_type)
            return super(ParameterizedSubstitution, self).visit_param_decl(node)
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
        new_node = self._update_type(new_node, 'ret_type')
        new_node = self._update_type(new_node, 'inferred_type')
        #  self._in_override = False
        return new_node

    def visit_new(self, node):
        new_node = super(ParameterizedSubstitution, self).visit_new(node)
        return self._update_type(new_node, 'class_type')

    def visit_super_instantiation(self, node):
        new_node = super(ParameterizedSubstitution, self).visit_super_instantiation(node)
        return self._update_type(new_node, 'class_type')
