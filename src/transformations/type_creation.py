from copy import deepcopy
from collections import defaultdict
from typing import List

from src import utils
from src.ir import ast, types as tp, kotlin_types as kt, type_utils as tu
from src.generators import Generator
from src.transformations.base import Transformation


def create_non_final_fields(fields):
    return [
        ast.FieldDeclaration(f.name, f.field_type, can_override=False,
                             override=f.override, is_final=f.is_final)
        for f in fields
    ]


def create_non_final_functions(functions):
    return [
        ast.FunctionDeclaration(f.name, deepcopy(f.params), f.get_type(),
                                deepcopy(f.body),
                                f.func_type, inferred_type=f.inferred_type,
                                is_final=False, override=f.override)
        for f in functions
    ]


def create_override_fields(fields):
    return [
        ast.FieldDeclaration(f.name, f.field_type, can_override=f.can_override,
                             override=True, is_final=f.is_final)
        for f in fields
    ]


def create_override_functions(functions):
    return [
        ast.FunctionDeclaration(f.name, deepcopy(f.params), f.ret_type,
                                deepcopy(f.body), f.func_type,
                                inferred_type=f.inferred_type,
                                is_final=f.is_final, override=True)
        for f in functions
    ]


def create_empty_supertype(class_type):
    return ast.ClassDeclaration(
        utils.random.word().capitalize(), superclasses=[], fields=[],
        class_type=class_type, functions=[], type_parameters=[],
        is_final=False
    )


def create_interface(class_decl, empty):
    if empty:
        return create_empty_supertype(ast.ClassDeclaration.INTERFACE)
    functions = [
        ast.FunctionDeclaration(f.name, deepcopy(f.params), f.get_type(), None,
                                f.func_type, inferred_type=None,
                                is_final=False, override=f.override)
        for f in class_decl.functions
    ]
    return ast.ClassDeclaration(utils.random.word().capitalize(),
                                superclasses=[], fields=[],
                                class_type=ast.ClassDeclaration.INTERFACE,
                                functions=functions,
                                type_parameters=class_decl.type_parameters)


def create_abstract_class(class_decl, empty):
    if empty:
        return create_empty_supertype(ast.ClassDeclaration.INTERFACE)
    functions = []
    for f in class_decl.functions:
        # Some functions are randomly made abstract.
        body_f = None if utils.random.bool() else deepcopy(f.body)
        functions.append(
            ast.FunctionDeclaration(f.name, deepcopy(f.params), f.get_type(),
                                    body_f, f.func_type,
                                    inferred_type=f.inferred_type,
                                    is_final=False, override=f.override))
    return ast.ClassDeclaration(utils.random.word().capitalize(),
                                superclasses=[],
                                fields=create_non_final_fields(class_decl.fields),
                                class_type=ast.ClassDeclaration.ABSTRACT,
                                functions=functions, is_final=False,
                                type_parameters=class_decl.type_parameters)


def create_regular_class(class_decl, empty):
    if empty:
        return create_empty_supertype(ast.ClassDeclaration.REGULAR)
    return ast.ClassDeclaration(
        utils.random.word().capitalize(), superclasses=[],
        fields=create_non_final_fields(class_decl.fields),
        functions=create_non_final_functions(class_decl.functions),
        is_final=False,
        type_parameters=class_decl.type_parameters)


def instantiate_type_constructor(type_constructor: tp.TypeConstructor,
                                 types: List[tp.Type]):
    t_args = []
    for t_param in type_constructor.type_parameters:
        if t_param.bound:
            a_types = tp.find_subtypes(t_param.bound, types, True)
        else:
            a_types = types
        c = utils.random.choice(a_types)
        if isinstance(c, ast.ClassDeclaration):
            t = c.get_type()
        else:
            t = c
        if isinstance(t, tp.TypeConstructor):
            types = [t for t in types if t != c]
            t = instantiate_type_constructor(t, types)
        t_args.append(t)
    return type_constructor.new(t_args)


def choose_type(types: List[tp.Type]):
    c = utils.random.choice(types)
    if isinstance(c, ast.ClassDeclaration):
        t = c.get_type()
    else:
        t = c
    if isinstance(t, tp.TypeConstructor):
        types = [t for t in types if t != c]
        t = instantiate_type_constructor(t, types)
    return t


class TypeCreation(Transformation):

    CORRECTNESS_PRESERVING = True

    def __init__(self):
        super(TypeCreation, self).__init__()
        self._new_class = None
        self._old_class = None

    def add_class_context(self, new_class, old_class):
        namespace = ast.GLOBAL_NAMESPACE + (new_class.name,)
        for f in new_class.fields:
            self.program.context.add_var(namespace, f.name, f)
        for f in new_class.functions:
            self.program.context.add_func(namespace, f.name, f)
            func_namespace = namespace + (f.name,)
            for p in f.params:
                self.program.context.add_var(func_namespace, p.name, p)
            if not f.body:
                continue
            if isinstance(self, SupertypeCreation):
                old_namespace = ast.GLOBAL_NAMESPACE + (old_class.name, f.name)
                n_decls = self.program.context.get_declarations_in(
                    old_namespace)
                for n, decls in n_decls.items():
                    rel = n[len(func_namespace):]
                    new_namespace = func_namespace + rel
                    for decl_name, decl in decls.items():
                        if isinstance(decl, ast.FunctionDeclaration):
                            self.program.context.add_func(new_namespace,
                                                          decl_name, decl)
                        else:
                            self.program.context.add_var(new_namespace,
                                                         decl_name, decl)
        self.program.add_declaration(new_class)

    def create_new_class(self, class_decl):
        raise NotImplementedError('create_new_class() must be implemented')

    def adapt_old_class(self, class_decl):
        raise NotImplementedError('adapt_old_class() must be implemented')

    def get_candidates_classes(self):
        # Get all class declarations
        return [d for d in self.program.declarations
                if isinstance(d, ast.ClassDeclaration)]

    def get_updated_classes(self):
        raise NotImplementedError('get_updated_classes() must be implemented')

    def visit_program(self, node):
        self.program = node
        # Get all class declarations
        classes = self.get_candidates_classes()
        if not classes:
            # There are not user-defined types.
            return
        class_decl = utils.random.choice(classes)
        self._new_class = self.create_new_class(class_decl)
        self._old_class = self.adapt_old_class(class_decl)
        # Add the newly created class to the program's context.
        new_node = super(TypeCreation, self).visit_program(self.program)
        self.add_class_context(self._new_class, self._old_class)
        # Update the old class.
        node.add_declaration(self._old_class)
        return new_node

    def update_type(self, node, attr):
        new_type = self._old_class.get_type()
        attr_value = getattr(node, attr)
        if not attr_value:
            # Nothing to update.
            return
        new_type = tu.update_type(attr_value, new_type)
        setattr(node, attr, new_type)
        return node

    def visit_super_instantiation(self, node):
        new_node = super(TypeCreation, self).visit_super_instantiation(node)
        self.update_type(new_node, 'class_type')
        return new_node

    def visit_new(self, node):
        new_node = super(TypeCreation, self).visit_new(node)
        self.update_type(new_node, 'class_type')
        return new_node

    def visit_func_decl(self, node):
        new_node = super(TypeCreation, self).visit_func_decl(node)
        self.update_type(new_node, 'ret_type')
        self.update_type(new_node, 'inferred_type')
        return new_node

    def visit_field_decl(self, node):
        self.update_type(node, 'field_type')
        return node

    def visit_param_decl(self, node):
        self.update_type(node, 'param_type')
        return node

    def visit_var_decl(self, node):
        new_node = super(TypeCreation, self).visit_var_decl(node)
        self.update_type(new_node, 'var_type')
        self.update_type(new_node, 'inferred_type')
        return new_node


class SubtypeCreation(TypeCreation):
    NAME = 'Subtype Creator'

    def __init__(self):
        super(SubtypeCreation, self).__init__()
        self.generator = None
        self._type_params_map = {}

    def _create_super_instantiation(self, class_decl, class_type):
        if class_decl.class_type == ast.ClassDeclaration.INTERFACE:
            return ast.SuperClassInstantiation(
                class_type, args=None)
        args = []
        for f in class_decl.fields:
            subtypes = tp.find_subtypes(
                self._type_params_map.get(f.get_type(), f.get_type()),
                self.types)
            subtypes = [c for c in subtypes
                        if not (isinstance(c, ast.ClassDeclaration) and
                              c.class_type != ast.ClassDeclaration.REGULAR)]
            t = (
                utils.random.choice(subtypes)
                if subtypes
                else self._type_params_map.get(f.get_type(), f.get_type())
            )
            if isinstance(t, ast.ClassDeclaration):
                t = t.get_type()
            args.append(self.generator.generate_expr(t, only_leaves=True))
        return ast.SuperClassInstantiation(class_type, args)

    def _get_class_type(self, class_decl, types):
        if class_decl.is_parameterized():
            class_type = instantiate_type_constructor(class_decl.get_type(),
                                                      types)
            self._type_params_map = {
                t_param: class_type.type_args[i]
                for i, t_param in enumerate(class_decl.type_parameters)
            }
            return class_type
        return class_decl.get_type()

    def create_new_class(self, class_decl):
        # Here the new class corresponds to a subtype from the given
        # `class_decl`.
        self.generator = Generator(context=self.program.context)
        decls = [d for d in self.program.declarations
                 if (d != class_decl and isinstance(d, ast.ClassDeclaration)
                     and d.class_type == ast.ClassDeclaration.REGULAR)]
        types = decls + self.generator.RET_BUILTIN_TYPES
        class_type = self._get_class_type(class_decl, types)
        overriden_fields = utils.random.sample(class_decl.fields)
        new_fields_nu = self.generator.max_fields - len(overriden_fields)
        fields = []
        for f in overriden_fields:
            fields.append(ast.FieldDeclaration(
                f.name, self._type_params_map.get(f.field_type, f.field_type),
                can_override=True, override=True,
                is_final=f.is_final))
        for i in range(utils.random.integer(0, new_fields_nu)):
            fields.append(self.generator.gen_field_decl(choose_type(types)))
        abstract_functions = [f for f in class_decl.functions
                              if f.body is None]
        functions = []
        for f in abstract_functions:
            expr = self.generator.generate_expr(
                self._type_params_map.get(f.get_type(), f.get_type()),
                only_leaves=True)
            if f.get_type() == kt.Unit:
                # We must create a block, if functions returns Unit.
                expr = ast.Block([expr])
            params = [
                ast.ParameterDeclaration(
                    p.name,
                    self._type_params_map.get(p.get_type(), p.get_type())
                ) for p in f.params]
            functions.append(
                ast.FunctionDeclaration(f.name, params, None,
                                        body=expr,
                                        func_type=f.func_type,
                                        inferred_type=f.get_type(),
                                        is_final=True, override=True))
        return ast.ClassDeclaration(
            utils.random.word().capitalize(),
            [self._create_super_instantiation(class_decl, class_type)],
            class_type=ast.ClassDeclaration.REGULAR, fields=fields,
            functions=functions, is_final=True)

    def adapt_old_class(self, class_decl):
        class_decl.fields = create_non_final_fields(class_decl.fields)
        class_decl.functions = create_non_final_functions(class_decl.functions)
        class_decl.is_final = False
        return class_decl


class SupertypeCreation(TypeCreation):
    NAME = 'Supertype Creator'

    def __init__(self):
        super(SupertypeCreation, self).__init__()
        self._defs = defaultdict(bool)
        self._namespace = ('global',)
        self.empty_supertype = False

    def create_new_class(self, class_decl):
        self.empty_supertype = utils.random.bool()
        if class_decl.class_type == ast.ClassDeclaration.INTERFACE:
            # An interface cannot inherit from a class.
            return create_interface(class_decl, self.empty_supertype)

        if class_decl.class_type == ast.ClassDeclaration.ABSTRACT:
            return create_abstract_class(class_decl, self.empty_supertype)

        class_types = [
            create_regular_class,
            create_abstract_class,
        ]
        if not class_decl.fields:
            # If the subclass does not contain any fields, then
            # we can safely create a superclass which is an interface.
            class_types.append(create_interface)
        return utils.random.choice(class_types)(class_decl,
                                                self.empty_supertype)

    def _get_subtype_functions(self, class_decl):
        functions = []
        func_map = {f.name: f for f in class_decl.functions}
        for f in self._new_class.functions:
            f2 = func_map[f.name]
            over_func = ast.FunctionDeclaration(
                f2.name, deepcopy(f2.params), f2.ret_type,
                f2.body, f2.func_type, f2.inferred_type,
                is_final=f2.is_final, override=True)
            if f.body is None:
                # The function of supertype is abstract, so we definetely
                # need to override it.
                functions.append(over_func)
                continue
            if utils.random.bool():
                # Randomly choose to override a function from supertype.
                functions.append(over_func)
        return functions

    def adapt_old_class(self, class_decl):
        if self.empty_supertype:
            superInstantiation = ast.SuperClassInstantiation(
                self._new_class.get_type(),
                args=(None
                      if self._new_class.class_type == ast.ClassDeclaration.INTERFACE
                      else []))
        else:
            args = (
                None
                if self._new_class.class_type == ast.ClassDeclaration.INTERFACE
                else [ast.Variable(f.name) for f in self._new_class.fields]
            )
            # If we create a supertype which is a type constructor, then
            # instantiate child class as follows:
            # B<T1, T2>: A<T1, T2>()
            #
            # In this, we can safely override fields and methods from the
            # parent class.
            new_class_type = self._new_class.get_type()
            if isinstance(new_class_type, tp.TypeConstructor):
                new_class_type = new_class_type.new(class_decl.type_parameters)
            superInstantiation = ast.SuperClassInstantiation(
                new_class_type, args)
        class_decl.superclasses.append(superInstantiation)
        class_decl.supertypes.append(superInstantiation.class_type)
        if not self.empty_supertype:
            class_decl.fields = create_override_fields(class_decl.fields)
            class_decl.functions = self._get_subtype_functions(class_decl)
        return class_decl

    def get_candidates_classes(self):
        return [d for d in self.program.declarations
                if (isinstance(d, ast.ClassDeclaration) and not
                    d.superclasses)]
