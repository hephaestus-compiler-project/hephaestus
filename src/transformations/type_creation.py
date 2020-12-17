from copy import deepcopy
from collections import defaultdict

from src import utils
from src.ir import ast, kotlin_types as kt
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


def create_interface(class_decl):
    functions = [
        ast.FunctionDeclaration(f.name, deepcopy(f.params), f.get_type(), None,
                                f.func_type, inferred_type=None,
                                is_final=False, override=f.override)
        for f in class_decl.functions
    ]
    return ast.ClassDeclaration(utils.random.word().capitalize(),
                                superclasses=[], fields=[],
                                class_type=ast.ClassDeclaration.INTERFACE,
                                functions=functions)


def create_abstract_class(class_decl):
    functions = []
    for f in class_decl.functions:
        # Some functions are randomly made abstract.
        body_f = None if utils.random.bool() else deepcopy(f.body)
        functions.append(
            ast.FunctionDeclaration(f.name, deepcopy(f.params), f.get_type(), body_f,
                                    f.func_type, inferred_type=f.inferred_type,
                                    is_final=False, override=f.override))
    return ast.ClassDeclaration(utils.random.word().capitalize(),
                                superclasses=[],
                                fields=create_non_final_fields(class_decl.fields),
                                class_type=ast.ClassDeclaration.ABSTRACT,
                                functions=functions, is_final=False)


def create_regular_class(class_decl):
    return ast.ClassDeclaration(
        utils.random.word().capitalize(), superclasses=[],
        fields=create_non_final_fields(class_decl.fields),
        functions=create_non_final_functions(class_decl.functions),
        is_final=False)


class TypeCreation(Transformation):

    CORRECTNESS_PRESERVING = True

    def __init__(self):
        super(TypeCreation, self).__init__()
        self._new_class = None
        self._old_class = None

    def add_class_context(self, new_class):
        namespace = ast.GLOBAL_NAMESPACE + (new_class.name,)
        for f in new_class.fields:
            self.program.context.add_var(namespace, f.name, f)
        for f in new_class.functions:
            self.program.context.add_var(namespace, f.name, f)
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
        self.add_class_context(self._new_class)
        # Update the old class.
        node.add_declaration(self._old_class)
        return new_node

    def update_supertypes(self, t, new_type):
        visited = [t]
        while visited:
            source = visited[-1]
            for i, st in enumerate(source.supertypes):
                if st.name == new_type.name and st == new_type:
                    return
                if st.name == new_type.name:
                    source.supertypes[i] = new_type
                    return
                if st not in visited:
                    visited.append(st)
            visited = visited[1:]

    def update_type(self, node, attr):
        new_type = self._old_class.get_type()
        attr_value = getattr(node, attr)
        if attr_value is not None:
            self.update_supertypes(attr_value, new_type)
        if attr_value and attr_value.name == new_type.name:
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
        return new_node


class SubtypeCreation(TypeCreation):
    NAME = 'Subtype Creator'

    def __init__(self):
        super(SubtypeCreation, self).__init__()
        self.generator = None

    def _create_super_instantiation(self, class_decl):
        if class_decl.class_type == ast.ClassDeclaration.INTERFACE:
            return ast.SuperClassInstantiation(
                class_decl.get_type(), args=None)
        args = []
        for f in class_decl.fields:
            subtypes = self.find_subtypes(f.get_type())
            subtypes = [c for c in subtypes
                        if not (isinstance(c, ast.ClassDeclaration) and
                              c.class_type != ast.ClassDeclaration.REGULAR)]
            t = utils.random.choice(subtypes) if subtypes else f.get_type()
            if isinstance(t, ast.ClassDeclaration):
                t = t.get_type()
            args.append(self.generator.generate_expr(t, only_leaves=True))
        return ast.SuperClassInstantiation(class_decl.get_type(), args)

    def create_new_class(self, class_decl):
        # Here the new class corresponds to a subtype from the given
        # `class_decl`.
        self.generator = Generator(context=self.program.context)
        decls = [d for d in self.program.declarations
                 if (d != class_decl and isinstance(d, ast.ClassDeclaration) and
                     d.class_type == ast.ClassDeclaration.REGULAR)]
        self.types = decls + self.generator.RET_BUILTIN_TYPES
        overriden_fields = utils.random.sample(class_decl.fields)
        new_fields_nu = self.generator.max_fields - len(overriden_fields)
        fields = []
        for f in overriden_fields:
            fields.append(ast.FieldDeclaration(
                f.name, f.field_type, can_override=True, override=True,
                is_final=f.is_final))
        for i in range(utils.random.integer(0, new_fields_nu)):
            etype = utils.random.choice([t for t in self.types
                                         if not class_decl.get_type().is_subtype(t)])
            if isinstance(etype, ast.ClassDeclaration):
                etype = etype.get_type()
            fields.append(self.generator.gen_field_decl(etype))
        abstract_functions = [f for f in class_decl.functions
                              if f.body is None]
        functions = []
        for f in abstract_functions:
            expr = self.generator.generate_expr(f.get_type(), only_leaves=True)
            if f.get_type() == kt.Unit:
                # We must create a block, if functions returns Unit.
                expr = ast.Block([expr])
            functions.append(
                ast.FunctionDeclaration(f.name, deepcopy(f.params), None,
                                        body=expr,
                                        func_type=f.func_type,
                                        inferred_type=f.get_type(),
                                        is_final=True, override=True))
        return ast.ClassDeclaration(
            utils.random.word().capitalize(),
            [self._create_super_instantiation(class_decl)],
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

    def create_new_class(self, class_decl):
        if class_decl.class_type == ast.ClassDeclaration.INTERFACE:
            # An interface cannot inherit from a class.
            return create_interface(class_decl)

        if class_decl.class_type == ast.ClassDeclaration.ABSTRACT:
            return create_abstract_class(class_decl)

        class_types = [
            create_regular_class,
            create_abstract_class,
        ]
        if not class_decl.fields:
            # If the subclass does not contain any fields, then
            # we can safely create a superclass which is an interface.
            class_types.append(create_interface)
        return utils.random.choice(class_types)(class_decl)

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
        args = (
            None
            if self._new_class.class_type == ast.ClassDeclaration.INTERFACE
            else [ast.Variable(f.name) for f in self._new_class.fields]
        )
        superInstantiation = ast.SuperClassInstantiation(
            self._new_class.get_type(), args)
        functions = self._get_subtype_functions(class_decl)
        class_decl.superclasses.append(superInstantiation)
        class_decl.supertypes.append(superInstantiation.class_type)
        class_decl.fields = create_override_fields(class_decl.fields)
        class_decl.functions = functions
        return class_decl

    def get_candidates_classes(self):
        return [d for d in self.program.declarations
                if (isinstance(d, ast.ClassDeclaration) and not
                    d.superclasses)]
