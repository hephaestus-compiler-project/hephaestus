import random
from collections import defaultdict

from src import utils
from src.ir import ast
from src.ir import types
from src.ir import kotlin_types as kt
from src.transformations.base import Transformation, change_namespace


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

        self._old_class = None
        self._old_class_decl = None
        self._type_constructor_decl = None

        self._type_params_constraints = {} # Name -> (Type, variance)
        self._type_params = []

        self._parameterized_type = None

        self._in_changed_type_decl = False
        self._in_override = False
        self._in_analysis = False

        #  self._use_graph = defaultdict(lambda: list())
        self._use_graph = {}  # node ((namespace, name)) => [node]
        self._func_calls = {}  # func_name => (namespace, params)

        self._namespace = ('global',)
        self.program = None

    def _create_parameterized_type(self):
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

    def _use_type_parameter(self, t, covariant=False):
        """Change concrete type with type parameter and add the corresponding
        constraints to type parameters.
        """
        if self._in_changed_type_decl:
            if self._in_override:
                return t
            # We can increase the probability based on already used type_params
            if random.random() < .5:
                return t
            for tp_name, constraints in self._type_params_constraints.items():
                if constraints is None:
                    # TODO handle variance
                    variance = INVARIANT
                    self._type_params_constraints[tp_name] = (t, variance)
                    type_param = create_type_parameter(tp_name, t, variance)
                    self._type_params.append(type_param)
                    return type_param
        return t

    def get_candidates_classes(self):
        """Get all simple classifier declarations."""
        return [d for d in self.program.declarations
                if (isinstance(d, ast.ClassDeclaration) and
                type(d.get_type()) == types.SimpleClassifier)]

    def result(self):
        return self.program

    def update_type(self, node, attr):
        attr_type = getattr(node, attr, None)
        if attr_type:
            if attr_type == self._old_class:
                setattr(node, attr, self._parameterized_type)
            elif isinstance(attr_type, types.ParameterizedType):
                attr_type.type_args = [
                    self._parameterized_type if t == self._old_class else t
                    for t in attr_type.type_args
                ]
                setattr(node, attr, attr_type)
        return node

    def visit_program(self, node):
        """Replace one class declaration with one type constructor and
        initialize type parameters.
        """
        self.program = node
        classes = self.get_candidates_classes()
        if not classes:
            ## There are not user-defined simple classifier declarations.
            return
        index = utils.random.integer(0, len(classes) - 1)
        index = 0
        class_decl = classes[index]
        self._old_class_decl = class_decl
        self._old_class = class_decl.get_type()
        total_type_params = utils.random.integer(1, self._max_type_params)
        # Initialize constraints to None
        self._type_params_constraints = {
            name: None for name in get_type_params_names(total_type_params)
        }
        return super(ParameterizedSubstitution, self).visit_program(self.program)

    @change_namespace
    def visit_class_decl(self, node):
        if node == self._old_class_decl:
            self._in_analysis = True
            # Run analysis
            _ = super(ParameterizedSubstitution, self).visit_class_decl(node)
            print("###Use graph###")
            __import__('pprint').pprint(self._use_graph)
            self._in_analysis = False
            self._in_changed_type_decl = True

        new_node = super(ParameterizedSubstitution, self).visit_class_decl(node)

        if self._in_changed_type_decl and node == self._old_class_decl:
            # Initialize unused type_params
            self._type_params.extend([
                create_type_parameter(tp_name, None, INVARIANT)
                for tp_name, constraint in self._type_params_constraints.items()
                if constraint is None
            ])
            # Here we use new node instead of old_class_decl because
            # old_class_decl contains the old functions and fields
            self._type_constructor_decl = create_type_constructor_decl(
                new_node, self._type_params
            )
            new_node = self._type_constructor_decl
            self._parameterized_type = self._create_parameterized_type()
        self._in_changed_type_decl = False
        return new_node

    def visit_super_instantiation(self, node):
        if self._in_analysis:
            print("Visit (super): " + node.name)
            return super(ParameterizedSubstitution, self).visit_super_instantiation(node)
        new_node = super(ParameterizedSubstitution, self).visit_super_instantiation(node)
        return self.update_type(new_node, 'class_type')

    def visit_var_decl(self, node):
        if self._in_analysis:
            print("Visit(var_decl): " + node.name)
            return super(ParameterizedSubstitution, self).visit_var_decl(node)
        new_node = super(ParameterizedSubstitution, self).visit_var_decl(node)
        return self.update_type(new_node, 'var_type')

    def visit_new(self, node):
        if self._in_analysis:
            print("Visit(new): " + str(node))
            return super(ParameterizedSubstitution, self).visit_new(node)
        new_node = super(ParameterizedSubstitution, self).visit_new(node)
        return self.update_type(new_node, 'class_type')

    def visit_field_decl(self, node):
        if self._in_analysis:
            gnode = (self._namespace, node.name)
            self._use_graph[gnode] = []
            print("Visit(field_decl): " + node.name)
            return super(ParameterizedSubstitution, self).visit_field_decl(node)
        node.field_type = self._use_type_parameter(node.field_type, True)
        return self.update_type(node, 'field_type')

    def visit_param_decl(self, node):
        if self._in_analysis:
            gnode = (self._namespace, node.name)
            self._use_graph[gnode] = []
            print("Visit(param_decl): " + node.name)
            return super(ParameterizedSubstitution, self).visit_param_decl(node)
        node.param_type = self._use_type_parameter(node.param_type)
        return self.update_type(node, 'param_type')

    @change_namespace
    def visit_func_decl(self, node):
        if self._in_analysis:
            # TODO check types
            # FIXME if the declaration is after the use, then we will not
            # detect the use.
            if (node.name in self._func_calls and
                len(self._func_calls[node.name]) == len(node.params)):
                args = self._func_calls[node.name]
                for arg, param in zip(args, node.params):
                    if arg in self._use_graph:
                        self._use_graph[arg].append((self._namespace, param.name))
            print("Visit(func_decl): " + node.name)
            return super(ParameterizedSubstitution, self).visit_func_decl(node)
        if node.override:
            self._in_override = True
        # TODO return statement must return a value of TypeParameter.
        # Maybe if the return statement returns a function parameter or
        # a field, then we can replace the types for both the return and
        # the function parameter or the field to have the same TypeParameter
        # a value
        #  if node.ret_type != kt.Unit:
            #  node.ret_type = self._use_type_parameter(node.ret_type, True)
        new_node = super(ParameterizedSubstitution, self).visit_func_decl(node)
        new_node = self.update_type(new_node, 'ret_type')
        new_node = self.update_type(new_node, 'inferred_type')
        self._in_override = False
        return new_node

    def visit_func_call(self, node):
        if self._in_analysis:
            self._func_calls[node.func] = [
                (self._namespace, getattr(x, 'name', None)) for x in node.args
            ]
            print("Visit(func_call): " + node.func)
            return super(ParameterizedSubstitution, self).visit_func_call(node)
        return super(ParameterizedSubstitution, self).visit_func_call(node)

    def visit_variable(self, node):
        if self._in_analysis:
            print("Visit(variable): " + node.name)
            return super(ParameterizedSubstitution, self).visit_variable(node)
        return super(ParameterizedSubstitution, self).visit_variable(node)

    def visit_string_constant(self, node):
        if self._in_analysis:
            print("Visit(string_const): " + str(node))
            return super(ParameterizedSubstitution, self).visit_string_constant(node)
        return super(ParameterizedSubstitution, self).visit_string_constant(node)
