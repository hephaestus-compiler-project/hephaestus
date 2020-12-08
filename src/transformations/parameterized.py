import random
from collections import defaultdict

from src import utils
from src.ir import ast
from src.ir import types
from src.ir import kotlin_types as kt
from src.transformations.base import Transformation


def create_type_parameters(total):
    # TODO Add variance and bound
    random_caps = []
    for _ in range(0, total):
        random_caps += utils.random.caps(1, random_caps)
    return [types.TypeParameter(c) for c in random_caps]


def create_type_constructor_decl(class_decl, type_parameters):
    # TODO update body accordingly
    return ast.ClassDeclaration(
        class_decl.name, class_decl.superclasses,
        class_type=class_decl.class_type,
        fields=class_decl.fields,
        functions=class_decl.functions,
        is_final=class_decl.is_final,
        type_parameters=type_parameters
    )


class ParameterizedSubstitution(Transformation):
    CORRECTNESS_PRESERVING = True
    NAME = 'Parameterized Substitution'

    def __init__(self, max_type_params=3):
        super(ParameterizedSubstitution, self).__init__()
        self._old_class = None
        self._old_class_decl = None
        self._max_type_params = max_type_params
        self._type_constructor_decl = None
        self._type_params = []
        self._type_params_constraints = defaultdict(lambda: None)
        self._parameterized_type = None
        self._in_changed_type_decl = False

        self._namespace = ('global',)
        self.program = None

    def _create_parameterized_type(self):
        type_args = [random.choice(kt.NonNothingTypes)
                     if self._type_params_constraints[tp] is None
                     else self._type_params_constraints[tp]
                     for tp in self._type_params]
        return types.ParameterizedType(self._type_constructor_decl.get_type(),
                                       type_args)

    def get_candidates_classes(self):
        """Get all simple classifiers declarations."""
        return [d for d in self.program.declarations
                if (isinstance(d, ast.ClassDeclaration) and
                isinstance(d.get_type(), types.SimpleClassifier))]

    def result(self):
        return self.program

    def update_type(self, node, attr):
        if getattr(node, attr) == self._old_class:
            setattr(node, attr, self._parameterized_type)
        return node

    def visit_program(self, node):
        """Replace one class declaration with one type constructor and
        initialize type parameters.
        """
        self.program = node
        classes = [d for d in node.declarations
                   if (isinstance(d, ast.ClassDeclaration) and
                       isinstance(d.get_type(), types.SimpleClassifier))]
        if not classes:
            ## There are not user-defined simple classifier declarations.
            return
        index = utils.random.integer(0, len(classes) - 1)
        index = 0
        class_decl = classes[index]
        self._old_class_decl = class_decl
        self._old_class = class_decl.get_type()
        # TODO Maybe we can do something more specific here
        total_type_params = utils.random.integer(1, self._max_type_params)
        self._type_params = create_type_parameters(total_type_params)
        self._type_constructor_decl = create_type_constructor_decl(
            class_decl, self._type_params)
        return super(ParameterizedSubstitution, self).visit_program(self.program)

    def visit_class_decl(self, node):
        if node == self._old_class_decl:
            self._in_changed_type_decl = True
        new_node = super(ParameterizedSubstitution, self).visit_class_decl(node)
        new_node = self._type_constructor_decl
        if self._in_changed_type_decl:
            self._parameterized_type = self._create_parameterized_type()
            self._in_changed_type_decl = False
        return new_node

    def _use_type_parameter(self, t):
        """Change concrete type with type parameter and add the corresponding
        constraints to type parameters.
        """
        if self._in_changed_type_decl:
            # TODO Add randomness
            for tp in self._type_params:
                if self._type_params_constraints[tp] is None:
                    self._type_params_constraints[tp] = t
                    return tp
        return t

    def visit_super_instantiation(self, node):
        new_node = super(ParameterizedSubstitution, self).visit_super_instantiation(node)
        return self.update_type(new_node, 'class_type')

    def visit_new(self, node):
        new_node = super(ParameterizedSubstitution, self).visit_new(node)
        # TODO update args?
        return self.update_type(new_node, 'class_type')

    def visit_param_decl(self, node):
        node.param_type = self._use_type_parameter(node.param_type)
        return self.update_type(node, 'param_type')

    def visit_var_decl(self, node):
        new_node = super(ParameterizedSubstitution, self).visit_var_decl(node)
        return self.update_type(new_node, 'var_type')

    def visit_func_decl(self, node):
        if node.ret_type != kt.Unit:
            node.ret_type = self._use_type_parameter(node.ret_type)
        new_node = super(ParameterizedSubstitution, self).visit_func_decl(node)
        new_node = self.update_type(new_node, 'ret_type')
        return new_node
