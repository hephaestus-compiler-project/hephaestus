import random
from collections import defaultdict

from src import utils
from src.ir import ast
from src.ir import types
from src.ir import kotlin_types as kt
import src.transformations.use_graph as ug
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
        self._max_type_params = max_type_params

        self._selected_class = None
        self._selected_class_decl = None
        self._type_constructor_decl = None
        self._selected_namespace = None

        self._type_params_constraints = {}  # Name -> (Type, variance)
        self._type_params = []

        self._parameterized_type = None

        self._in_override = False

        # phases
        self._in_first_pass = False
        self._in_select_type_params = False

        # node = ((namespace, Declaration))

        self._use_graph = None

        # in_select_type_params
        self._use_entries = set()  # set of nodes we can use as type params
        self._type_params_nodes = {}  # node => TypeParameter

        self._namespace = ast.GLOBAL_NAMESPACE
        self.program = None

    def get_candidates_classes(self):
        """Get all simple classifier declarations."""
        return [d for d in self.program.declarations
                if (isinstance(d, ast.ClassDeclaration) and
                type(d.get_type()) is types.SimpleClassifier)]

    def result(self):
        return self.program

    def _create_parameterized_type(self):
        """Create parameterized type based on type_params, constraints, and
        constructor.
        """
        type_args = []
        for tp in self._type_params:
            constraint = self._type_params_constraints[tp.name]
            if constraint is None:
                possible_types = kt.NonNothingTypes
            else:
                constraint = constraint[0]
                # TODO check the code about variance
                if tp.variance == INVARIANT:
                    type_args.append(constraint)
                    continue
                possible_types = []
                if tp.variance == CONTRAVARIANT:
                    possible_types = list(constraint.get_supertypes())
                if tp.variance == COVARIANT:
                    possible_types = self.find_subtypes(constraint, True)
                    possible_types += [bt for bt in kt.NonNothingTypes
                                       if bt.is_subtype(constraint)]
                if tp.bound:
                    possible_types = [t for t in possible_types
                                      if t.is_subtype(tp.bound)]
            type_args.append(random.choice(possible_types))
        return types.ParameterizedType(self._type_constructor_decl.get_type(),
                                       type_args)

    def _use_type_parameter(self, node, t, covariant=False):
        """Change concrete type with type parameter and add the corresponding
        constraints to type parameters.
        """
        if self._in_override:
            return t
        gnode = (self._namespace, node.name)
        #  assert gnode in self._use_graph
        # Check if gnode is bi_reachable to a none node
        if ug.none_reachable(self._use_graph, gnode):
            return t
        # Check if there is a reachable type parameter
        for n in self._type_params_nodes:
            if ug.bi_reachable(self._use_graph, gnode, n):
                return t
        # Use random
        if utils.random.bool():
            return t
        for tp_name, constraints in self._type_params_constraints.items():
            if constraints is None:
                # TODO handle variance
                variance = INVARIANT
                self._type_params_constraints[tp_name] = (t, variance)
                type_param = create_type_parameter(tp_name, t, variance)
                self._type_params.append(type_param)
                self._type_params_nodes[(self._namespace, node.name)] = type_param
                return type_param
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
            if attr_type == self._selected_class:
                setattr(node, attr, self._parameterized_type)
            elif isinstance(attr_type, types.ParameterizedType):
                attr_type.type_args = [
                    self._parameterized_type if t == self._selected_class else t
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
                    name = None
                    try:  # Variable
                        name = return_expr.name
                    except AttributeError:  # FunctionCall
                        name = return_expr.func
                    gnode = (self._namespace, node.name)
                    self._use_graph[gnode] # Safely initialize node
                    match = [tp for v, tp in self._type_params_nodes.items()
                             if ug.reachable(self._use_graph, v, gnode)]
                    # TODO make sure that there cannot be two results
                    if match:
                        setattr(node, attr, match[0])
            # 3
            elif (type(node) == ast.VariableDeclaration or
                  type(node) == ast.ParameterDeclaration or
                  type(node) == ast.FieldDeclaration):
                if node.name == 'x':
                    __import__('ipdb').set_trace()
                gnode = (self._namespace, node.name)
                # There can be only one result
                # TODO make sure that there cannot be two results
                match = [tp for v, tp in self._type_params_nodes.items()
                         if ug.bi_reachable(self._use_graph, gnode, v)]
                if match:
                    setattr(node, attr, match[0])
        return node

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
        self._selected_class = class_decl.get_type()
        total_type_params = utils.random.integer(1, self._max_type_params)
        # Initialize constraints to None
        self._type_params_constraints = {
            name: None for name in get_type_params_names(total_type_params)
        }
        self._in_first_pass = True
        self.program = super(ParameterizedSubstitution, self).visit_program(
                             self.program)
        self._in_first_pass = False
        return super(ParameterizedSubstitution, self).visit_program(
            self.program)

    @change_namespace
    def visit_class_decl(self, node):
        """Do the next steps if the class is the one to replace:

        * Run def-use analysis
        * Initialize the uninitialized type parameters
        * Create the type constructor
        * Create the parameterized type
        """
        if node == self._selected_class_decl and self._in_first_pass:
            # Use Analysis
            analysis = UseAnalysis(self.program)
            analysis.visit(node)
            self._use_graph = analysis.result()
            # Use type parameters
            self._in_select_type_params = True
            # select where to use Type Parameters
            new_node = super(ParameterizedSubstitution, self).visit_class_decl(node)
            self._in_select_type_params = False
            # Initialize unused type_params
            self._type_params.extend([
                create_type_parameter(tp_name, None, INVARIANT)
                for tp_name, constraint in self._type_params_constraints.items()
                if constraint is None
            ])
            self._type_constructor_decl = create_type_constructor_decl(
                new_node, self._type_params
            )
            new_node = self._type_constructor_decl
            self._parameterized_type = self._create_parameterized_type()
        elif self._in_first_pass:
            return node
        else:
            new_node = super(ParameterizedSubstitution, self).visit_class_decl(node)
        return new_node

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
        """Add variable to _var_decl_stack to add flows from it to other
        variables in visit_variable.
        """
        new_node = super(ParameterizedSubstitution, self).visit_var_decl(node)
        return self._update_type(new_node, 'var_type')

    @change_namespace
    def visit_func_decl(self, node):
        if node.override:
            self._in_override = True
        new_node = super(ParameterizedSubstitution, self).visit_func_decl(node)
        new_node = self._update_type(new_node, 'ret_type')
        new_node = self._update_type(new_node, 'inferred_type')
        self._in_override = False
        return new_node

    def visit_new(self, node):
        new_node = super(ParameterizedSubstitution, self).visit_new(node)
        return self._update_type(new_node, 'class_type')

    def visit_super_instantiation(self, node):
        new_node = super(ParameterizedSubstitution, self).visit_super_instantiation(node)
        return self._update_type(new_node, 'class_type')
