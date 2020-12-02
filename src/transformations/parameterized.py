import random
from collections import defaultdict

from src import utils
from src.ir import ast
from src.ir import types
from src.ir import kotlin_types as kt
from src.ir.visitors import DefaultVisitor


class Transformation(DefaultVisitor):
    def __init__(self):
        self.transform = False


def create_type_parameters(total):
    # TODO Add variance and bound
    random_caps = []
    for _ in range(0, total):
        random_caps += utils.random.caps(1, random_caps)
    return [types.TypeParameter(c) for c in random_caps]


def create_type_constructor(class_decl, type_parameters):
    # TODO update body accordingly
    return ast.ClassDeclaration(
        class_decl.name, class_decl.superclasses,
        class_type=class_decl.class_type,
        fields=class_decl.fields,
        functions=class_decl.functions,
        is_final=class_decl.is_final,
        type_parameters=type_parameters
    )

class ParameterizedCreation(Transformation):

    def __init__(self):
        super(ParameterizedCreation, self).__init__()
        self._old_class = None
        self._type_constructor = None
        self._type_parameters = []
        self._parameterized_type = None

        self._namespace = ('global',)
        self.program = None

    def _create_parameterized_type(self):
        # TODO add constraints to select type_args
        type_args = [random.choice(kt.NonNothingTypes)
                     for _ in self._type_parameters]
        return types.ParameterizedType(self._type_constructor.get_type(),
                                       type_args)

    def result(self):
        return self.program

    def visit_program(self, node):
        """Replace one class declaration with one type constructor and
        initialize type parameters.
        """
        classes = [d for d in node.declarations
                   if (isinstance(d, ast.ClassDeclaration) and
                       isinstance(d.get_type(), types.SimpleClassifier))]
        if not classes:
            ## There are not user-defined simple classifier declarations.
            return
        index = utils.random.integer(0, len(classes) - 1)
        class_decl = classes[index]
        self._old_class = class_decl.get_type()
        # TODO Maybe we can do something more specific here
        total_type_params = utils.random.integer(1, 1)
        self._type_parameters = create_type_parameters(total_type_params)
        self._type_constructor = create_type_constructor(
            class_decl, self._type_parameters)
        # TODO maybe we can do it more dynamically
        self._parameterized_type = self._create_parameterized_type()
        decls = [d for d in node.declarations if d != class_decl]
        self.program = ast.Program([self._type_constructor] + decls)
        super(ParameterizedCreation, self).visit_program(self.program)

    def visit_block(self, node):
        # TODO
        super(ParameterizedCreation, self).visit_block(node)
        for e in node.body:
            if not isinstance(e, ast.VariableDeclaration):
                continue

    def visit_class_decl(self, node):
        # TODO
        initial_namespace = self._namespace
        self._namespace += (node.name,)
        super(ParameterizedCreation, self).visit_class_decl(node)
        for f in node.fields:
            pass
        self._namespace = initial_namespace

    def visit_param_decl(self, node):
        if node.param_type == self._old_class:
            node.param_type = self._parameterized_type
            if node.default:
                raise NotImplementedError

    def visit_field_decl(self, node):
        # TODO
        pass

    def visit_var_decl(self, node):
        super(ParameterizedCreation, self).visit_var_decl(node)
        if node.var_type == self._old_class:
            node.var_type = self._parameterized_type

    def visit_func_decl(self, node):
        # TODO
        initial_namespace = self._namespace
        self._namespace += (node.name,)
        super(ParameterizedCreation, self).visit_func_decl(node)
        for p in node.params:
            pass
        self._namespace = initial_namespace

    def visit_variable(self, node):
        # TODO
        pass
