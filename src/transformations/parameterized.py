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

    def __init__(self):
        super(ParameterizedSubstitution, self).__init__()
        self._old_class = None
        self._old_class_decl = None
        self._type_constructor_decl = None
        self._type_parameters = []
        self._parameterized_type = None

        self._namespace = ('global',)
        self.program = None

    def _create_parameterized_type(self):
        # TODO add constraints to select type_args
        type_args = [random.choice(kt.NonNothingTypes)
                     for _ in self._type_parameters]
        return types.ParameterizedType(self._type_constructor_decl.get_type(),
                                       type_args)

    def get_candidates_classes(self):
        """Get all simple classifiers declarations."""
        return [d for d in self.program.declarations
                if (isinstance(d, ast.ClassDeclaration) and
                isinstance(d.get_type(), types.SimpleClassifier))]

    def result(self):
        return self.program

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
        class_decl = classes[index]
        self._old_class_decl = class_decl
        self._old_class = class_decl.get_type()
        # TODO Maybe we can do something more specific here
        total_type_params = utils.random.integer(1, 1)
        self._type_parameters = create_type_parameters(total_type_params)
        self._type_constructor_decl = create_type_constructor_decl(
            class_decl, self._type_parameters)
        # TODO maybe we can do it more dynamically
        self._parameterized_type = self._create_parameterized_type()
        return super(ParameterizedSubstitution, self).visit_program(self.program)

    def visit_class_decl(self, node):
        new_node = super(ParameterizedSubstitution, self).visit_class_decl(node)
        if new_node == self._old_class_decl:
            new_node = self._type_constructor_decl
        #  for f in node.fields:
            #  pass
        return new_node

    def visit_param_decl(self, node):
        if node.param_type == self._old_class:
            node.param_type = self._parameterized_type
            if node.default:
                raise NotImplementedError
        return node

    def visit_var_decl(self, node):
        new_node = super(ParameterizedSubstitution, self).visit_var_decl(node)
        if new_node.var_type == self._old_class:
            new_node.var_type = self._parameterized_type
        return new_node

    def visit_func_decl(self, node):
        new_node = super(ParameterizedSubstitution, self).visit_func_decl(node)
        #  for p in node.params:
            #  pass
        return new_node
