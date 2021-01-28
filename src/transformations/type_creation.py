from copy import deepcopy
from collections import defaultdict, OrderedDict

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
        ast.FunctionDeclaration(f.name, deepcopy(f.params),
                                deepcopy(f.get_type()),
                                deepcopy(f.body),
                                ast.FunctionDeclaration.CLASS_METHOD,
                                inferred_type=deepcopy(f.inferred_type),
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
        ast.FunctionDeclaration(f.name, deepcopy(f.params),
                                deepcopy(f.ret_type),
                                deepcopy(f.body),
                                ast.FunctionDeclaration.CLASS_METHOD,
                                inferred_type=deepcopy(f.inferred_type),
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
        # Create an empty interface, i.e., without functions.
        return create_empty_supertype(ast.ClassDeclaration.INTERFACE)
    functions = [
        ast.FunctionDeclaration(f.name, deepcopy(f.params),
                                deepcopy(f.get_type()), None,
                                ast.FunctionDeclaration.CLASS_METHOD,
                                inferred_type=None,
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
        # Create an empty abstract class, i.e., without fields and functions.
        return create_empty_supertype(ast.ClassDeclaration.INTERFACE)
    functions = []
    for func in class_decl.functions:
        # Some functions are randomly made abstract.
        body_f = None if utils.random.bool() else deepcopy(func.body)
        functions.append(
            ast.FunctionDeclaration(func.name,
                                    deepcopy(func.params),
                                    deepcopy(func.get_type()),
                                    body_f,
                                    ast.FunctionDeclaration.CLASS_METHOD,
                                    inferred_type=deepcopy(func.inferred_type),
                                    is_final=False, override=func.override))
    return ast.ClassDeclaration(
        utils.random.word().capitalize(),
        superclasses=[],
        fields=create_non_final_fields(class_decl.fields),
        class_type=ast.ClassDeclaration.ABSTRACT,
        functions=functions, is_final=False,
        type_parameters=class_decl.type_parameters)


def create_regular_class(class_decl, empty):
    if empty:
        # Create an empty class.
        return create_empty_supertype(ast.ClassDeclaration.REGULAR)
    return ast.ClassDeclaration(
        utils.random.word().capitalize(), superclasses=[],
        fields=create_non_final_fields(class_decl.fields),
        functions=create_non_final_functions(class_decl.functions),
        is_final=False,
        type_parameters=class_decl.type_parameters)


class TypeCreation(Transformation):

    CORRECTNESS_PRESERVING = True

    def __init__(self, program, logger=None):
        super().__init__(program, logger)
        self._new_class = None
        self._old_class = None

    def _add_function_vars(self, new_class, old_class, func):
        func_namespace = ast.GLOBAL_NAMESPACE + (new_class.name, func.name,)
        old_namespace = ast.GLOBAL_NAMESPACE + (old_class.name, func.name)
        # Find all declarations in the namespace of the old class.
        n_decls = self.program.context.get_declarations_in(old_namespace)
        for ns, decls in n_decls.items():
            # Find declarations relative to the old namespace
            rel = ns[len(func_namespace):]
            # Construct the new namespace, e.g.,
            # 'global/OldClass/func/var': VariableDecl(...)
            #  =>
            # 'global/NewClass/func/var': VariableDecl(...)
            new_namespace = func_namespace + rel
            for decl_name, decl in decls.items():
                if isinstance(decl, ast.FunctionDeclaration):
                    self.program.context.add_func(new_namespace,
                                                  decl_name, decl)
                else:
                    self.program.context.add_var(new_namespace,
                                                 decl_name, decl)

    def add_class_context(self, new_class, old_class):
        namespace = ast.GLOBAL_NAMESPACE + (new_class.name,)
        for field in new_class.fields:
            # Add class fields to context.
            self.program.context.add_var(namespace, field.name, field)
        for func in new_class.functions:
            # Add functions to context.
            self.program.context.add_func(namespace, func.name, func)
            func_namespace = namespace + (func.name,)
            for param in func.params:
                # Add function params to context.
                self.program.context.add_var(func_namespace, param.name, param)
            if not func.body:
                continue
            if isinstance(self, SupertypeCreation):
                # Add all declarations relative the function of the old
                # class to the namespace corresponding to the function of
                # new class.
                self._add_function_vars(new_class, old_class, func)
        self.program.add_declaration(new_class)
        # At the following lines, we place new class at the right place.
        # For example, if the new class inherits from the old class, we place
        # the new class after the declaration of the old class.
        #
        # Otherwise, if the old class inherits from the new class, we place
        # the new class before the declaration of the old class.
        # This assumption regarding ordering of class declarations is useful
        # for other transformations.
        decls = OrderedDict()
        after_old = new_class.inherits_from(old_class)
        for name, decl in self.program.get_declarations().items():
            if name == old_class.name and after_old:
                decls[name] = decl
                decls[new_class.name] = new_class
            if name == old_class.name and not after_old:
                decls[new_class.name] = new_class
                decls[name] = decl
            if name == new_class.name:
                continue
            decls[name] = decl
        self.program.update_declarations(decls)

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
        # Get all class declarations
        classes = self.get_candidates_classes()
        if not classes:
            # There are not user-defined types.
            return None
        self.is_transformed = True
        class_decl = utils.random.choice(classes)
        self._new_class = self.create_new_class(class_decl)
        self._old_class = self.adapt_old_class(class_decl)
        # Add the newly created class to the program's context.
        new_node = super().visit_program(self.program)
        self.add_class_context(self._new_class, self._old_class)
        # Update the old class.
        node.add_declaration(self._old_class)
        return new_node

    def update_type(self, node, attr):
        new_type = self._old_class.get_type()
        attr_value = getattr(node, attr)
        if not attr_value:
            # Nothing to update.
            return None
        new_type = tu.update_type(attr_value, new_type)
        setattr(node, attr, new_type)
        return node

    def visit_super_instantiation(self, node):
        new_node = super().visit_super_instantiation(node)
        self.update_type(new_node, 'class_type')
        return new_node

    def visit_new(self, node):
        new_node = super().visit_new(node)
        self.update_type(new_node, 'class_type')
        return new_node

    def visit_func_decl(self, node):
        new_node = super().visit_func_decl(node)
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
        new_node = super().visit_var_decl(node)
        self.update_type(new_node, 'var_type')
        self.update_type(new_node, 'inferred_type')
        return new_node

    def visit_type_param(self, node):
        new_node = super().visit_type_param(node)
        self.update_type(new_node, 'bound')
        return new_node


class SubtypeCreation(TypeCreation):

    def __init__(self, program, logger=None):
        super().__init__(program, logger)
        self.generator = Generator(context=self.program.context)
        # This dictionary is used to map type parameters to their
        # type arguments.
        # This used, if we chose to create subtype from a parameterized class.
        # Therefore, before inheriting from this class, we have to instantiate
        # it.
        self._type_params_map = {}

    def _create_super_instantiation(self, class_decl, class_type):
        if class_decl.class_type == ast.ClassDeclaration.INTERFACE:
            return ast.SuperClassInstantiation(
                class_type, args=None)
        args = []
        regular_types = [c for c in self.types
                         if getattr(c, 'class_type', 0) ==
                         ast.ClassDeclaration.REGULAR]
        for field in class_decl.fields:
            subtypes = tu.find_subtypes(
                self._type_params_map.get(field.get_type(), field.get_type()),
                regular_types, concrete_only=True)
            random_type = (
                utils.random.choice(subtypes)
                if subtypes
                else self._type_params_map.get(
                    field.get_type(), field.get_type())
            )
            # FIXME it may crash here in some rare cases
            args.append(self.generator.generate_expr(
                random_type, only_leaves=True))
        return ast.SuperClassInstantiation(class_type, args)

    def _get_class_type(self, class_decl, types):
        if class_decl.is_parameterized():
            # We instantiate type constructor with random type arguments.
            # and then we inherit from the instantiated type.
            class_type, self._type_params_map = (
                tu.instantiate_type_constructor(class_decl.get_type(),
                                                types))
            return class_type
        return class_decl.get_type()

    def create_new_class(self, class_decl):
        # Here the new class corresponds to a subtype from the given
        # `class_decl`.
        class_type = self._get_class_type(class_decl, self.types)
        overriden_fields = utils.random.sample(class_decl.fields)
        new_fields_nu = self.generator.max_fields - len(overriden_fields)
        fields = []
        for field in overriden_fields:
            fields.append(ast.FieldDeclaration(
                field.name,
                deepcopy(self._type_params_map.get(
                    field.field_type, field.field_type)),
                can_override=True,
                override=True,
                is_final=field.is_final))
        for _ in range(utils.random.integer(0, new_fields_nu)):
            fields.append(self.generator.gen_field_decl(
                tu.choose_type(self.types)))
        abstract_functions = [f for f in class_decl.functions
                              if f.body is None]
        functions = []
        # We need to override all abstract function defined in the supertype.
        for func in abstract_functions:
            expr = self.generator.generate_expr(
                self._type_params_map.get(func.get_type(), func.get_type()),
                only_leaves=True)
            if func.get_type() == kt.Unit:
                # We must create a block, if functions returns Unit.
                expr = ast.Block([expr])
            params = [
                ast.ParameterDeclaration(
                    p.name,
                    deepcopy(self._type_params_map.get(
                        p.get_type(), p.get_type()))
                ) for p in func.params]
            functions.append(
                ast.FunctionDeclaration(
                    func.name, params, None,
                    body=expr,
                    func_type=ast.FunctionDeclaration.CLASS_METHOD,
                    inferred_type=deepcopy(func.get_type()),
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

    def __init__(self, program, logger=None):
        super().__init__(program, logger)
        self._defs = defaultdict(bool)
        self._namespace = ('global',)
        self.empty_supertype = False

    def create_new_class(self, class_decl):
        # Randomly choose to create an empty supertype.
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
        def check_return_stmt(node: ast.FunctionDeclaration):
            """Check if return is a New Parameterized node and has
            can_infer_type_args set to True. In that case, we should always set
            ret_type.

            Return true is can_infer_type_args is False
            """
            if (isinstance(node.body, ast.New) and
                    getattr(node.body.class_type, 'can_infer_type_args', None)
                    is True) or (
                    isinstance(node.body, ast.Block) and
                    len(node.body.body) > 0 and
                    isinstance(node.body.body[-1], ast.New) and
                    getattr(node.body.body[-1].class_type,
                            'can_infer_type_args', None) is True):
                return False
            return True
        functions = []
        func_map = {f.name: f for f in class_decl.functions}
        for func in self._new_class.functions:
            sfunc = func_map[func.name]  # selected_func
            ret_type = sfunc.ret_type if check_return_stmt(sfunc) else \
                sfunc.inferred_type
            over_func = ast.FunctionDeclaration(
                sfunc.name, deepcopy(sfunc.params), ret_type,
                sfunc.body, ast.FunctionDeclaration.CLASS_METHOD,
                sfunc.inferred_type,
                is_final=sfunc.is_final, override=True)
            if func.body is None:
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
            super_instantiation = ast.SuperClassInstantiation(
                self._new_class.get_type(),
                args=(None
                      if self._new_class.class_type ==
                      ast.ClassDeclaration.INTERFACE
                      else []))
        else:
            args = (
                None
                if self._new_class.class_type == ast.ClassDeclaration.INTERFACE
                else [ast.Variable(f.name) for f in self._new_class.fields]
            )
            # If we create a supertype that is a type constructor, then
            # instantiate child class as follows:
            # B<T1, T2>: A<T1, T2>()
            #
            # In this, we can safely override fields and methods from the
            # parent class.
            new_class_type = self._new_class.get_type()
            if isinstance(new_class_type, tp.TypeConstructor):
                new_class_type = new_class_type.new(class_decl.type_parameters)
            super_instantiation = ast.SuperClassInstantiation(
                new_class_type, args)
        class_decl.superclasses.append(super_instantiation)
        class_decl.supertypes.append(super_instantiation.class_type)
        if not self.empty_supertype:
            class_decl.fields = create_override_fields(class_decl.fields)
            class_decl.functions = self._get_subtype_functions(class_decl)
        return class_decl

    def get_candidates_classes(self):
        return [d for d in self.program.declarations
                if (isinstance(d, ast.ClassDeclaration) and not
                    d.superclasses)]
