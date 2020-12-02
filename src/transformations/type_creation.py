from collections import defaultdict

from src import utils
from src.ir import ast
from src.ir.visitors import DefaultVisitor
from src.generators import Generator
from src.transformations.base import Transformation



def create_non_final_fields(fields):
    return [
        ast.FieldDeclaration(f.name, f.field_type, is_final=False,
                             override=f.override)
        for f in fields
    ]


def create_non_final_functions(functions):
    return [
        ast.FunctionDeclaration(f.name, f.params, f.ret_type, f.body,
                                f.func_type, is_final=False,
                                override=f.override)
        for f in functions
    ]


def create_override_fields(fields):
    return [
        ast.FieldDeclaration(f.name, f.field_type, is_final=f.is_final,
                             override=True)
        for f in fields
    ]


def create_override_functions(functions):
    return [
        ast.FunctionDeclaration(f.name, f.params, f.ret_type, f.body,
                                f.func_type, is_final=f.is_final,
                                override=True)
        for f in functions
    ]


def create_interface(class_decl):
    functions = [
        ast.FunctionDeclaration(f.name, f.params, f.ret_type, None,
                                f.func_type, is_final=False,
                                override=f.override)
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
        body_f = None if utils.random.bool() else f.body
        functions.append(
            ast.FunctionDeclaration(f.name, f.params, f.ret_type, body_f,
                                    f.func_type, is_final=False,
                                    override=f.override))
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
        self.program = None

    def create_new_class(self, class_decl, node):
        raise NotImplementedError('create_new_class() must be implemented')

    def adapt_old_class(self, class_decl):
        raise NotImplementedError('adapt_old_class() must be implemented')

    def result(self):
        return self.program

    def get_candidates_classes(self, node):
        # Get all class declarations
        return [d for d in node.declarations
                if isinstance(d, ast.ClassDeclaration)]

    def get_updated_classes(self):
        raise NotImplementedError('get_updated_classes() must be implemented')

    def visit_program(self, node):
        # Get all class declarations
        classes = self.get_candidates_classes(node)
        if not classes:
            ## There are not user-defined types.
            return
        index = utils.random.integer(0, len(classes) - 1)
        class_decl = classes[index]
        self._new_class = self.create_new_class(class_decl, node)
        self._old_class = self.adapt_old_class(class_decl)
        node.context.add_class(('global',), self._new_class.name,
                               self._new_class)
        node.context.add_class(('global',), self._old_class.name,
                               self._old_class)
        decls = [d for d in node.declarations if d != class_decl]
        self.program = ast.Program(self.get_updated_classes() + decls,
                                   node.context)
        #super(TypeCreation, self).visit_program(self.program)


class SubtypeCreation(TypeCreation):
    NAME = 'Subtype Creator'

    def __init__(self):
        super(SubtypeCreation, self).__init__()
        self.generator = None

    def _create_super_instantiation(self, class_decl):
        if class_decl.class_type == ast.ClassDeclaration.INTERFACE:
            return ast.SuperClassInstantiation(
                class_decl.get_type(), args=None)
        return ast.SuperClassInstantiation(
            class_decl.get_type(),
            args=[self.generator.generate_expr(f.get_type(), only_leaves=True)
                  for f in class_decl.fields])

    def create_new_class(self, class_decl, node):
        self.generator = Generator(context=node.context)
        # Here the new class corresponds to a subtype from the given
        # `class_decl`.
        decls = [d for d in node.declarations
                 if (d != class_decl and isinstance(d, ast.ClassDeclaration) and
                     d.class_type == ast.ClassDeclaration.REGULAR)]
        types = [d.get_type() for d in decls] + self.generator.BUILTIN_TYPES
        overriden_fields = utils.random.sample(class_decl.fields)
        new_fields_nu = self.generator.max_fields - len(overriden_fields)
        fields = []
        for f in overriden_fields:
            fields.append(ast.FieldDeclaration(
                f.name, f.field_type, is_final=True, override=True))
        for i in range(utils.random.integer(0, new_fields_nu)):
            etype = utils.random.choice(types)
            fields.append(self.generator.gen_field_decl(etype))
        abstract_functions = [f for f in class_decl.functions
                              if f.body is None]
        functions = []
        for f in abstract_functions:
            expr = self.generator.generate_expr(f.ret_type, only_leaves=True)
            functions.append(
                ast.FunctionDeclaration(f.name, f.params, f.ret_type,
                                        body=ast.Block([expr]),
                                        func_type=f.func_type,
                                        is_final=True, override=True)
            )
        return ast.ClassDeclaration(
            utils.random.word().capitalize(),
            [self._create_super_instantiation(class_decl)],
            class_type=ast.ClassDeclaration.REGULAR, fields=fields,
            functions=functions, is_final=True)

    def adapt_old_class(self, class_decl):
        return ast.ClassDeclaration(
            class_decl.name, class_decl.superclasses, class_decl.class_type,
            fields=create_non_final_fields(class_decl.fields),
            functions=create_non_final_functions(class_decl.functions),
            is_final=False, type_parameters=class_decl.type_parameters)

    def get_updated_classes(self):
        return [self._old_class, self._new_class]


class SupertypeCreation(TypeCreation):
    NAME = 'Supertype Creator'

    def __init__(self):
        super(SupertypeCreation, self).__init__()
        self._defs = defaultdict(bool)
        self._namespace = ('global',)

    def create_new_class(self, class_decl, node):
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
                f2.name, f2.params, f2.ret_type,
                f2.body, f2.func_type, is_final=f2.is_final, override=True)
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
        return ast.ClassDeclaration(
            class_decl.name, superclasses=[superInstantiation],
            class_type=class_decl.class_type,
            fields=create_override_fields(class_decl.fields),
            functions=functions, is_final=class_decl.is_final)

    def _replace_subtype_with_supertype(self, decl, setter):
        if decl.get_type().name == self._old_class.get_type().name:
            if utils.random.bool():
                setter(decl, self._new_class.get_type())
            else:
                setter(decl, self._old_class.get_type())

    def get_candidates_classes(self, node):
        return [d for d in node.declarations
                if (isinstance(d, ast.ClassDeclaration) and not
                    d.superclasses)]

    def get_updated_classes(self):
        return [self._new_class, self._old_class]

    def visit_block(self, node):
        # Inside a block we are interested in variable declarations.
        # If there are variable declarations that are not used
        # and their declared type matches the type of the created class,
        # we randomly assign it to this supertype.
        super(SupertypeCreation, self).visit_block(node)
        for e in node.body:
            if not isinstance(e, ast.VariableDeclaration):
                continue
            if self._defs[(self._namespace, e.name)]:
                continue
            self._replace_subtype_with_supertype(
                e, lambda x, y: setattr(x, 'var_type', y))

    def visit_class_decl(self, node):
        initial_namespace = self._namespace
        self._namespace += (node.name,)
        super(SupertypeCreation, self).visit_class_decl(node)
        for f in node.fields:
            if self._defs[(self._namespace, f.name)]:
                continue
            self._replace_subtype_with_supertype(
                f, lambda x, y: setattr(x, 'field_type', y))
        self._namespace = initial_namespace

    def visit_param_decl(self, node):
        self._defs[(self._namespace, node.name)] = False

    def visit_field_decl(self, node):
        self._defs[(self._namespace, node.name)] = False

    def visit_var_decl(self, node):
        super(SupertypeCreation, self).visit_var_decl(node)
        self._defs[(self._namespace, node.name)] = False

    def visit_func_decl(self, node):
        initial_namespace = self._namespace
        self._namespace += (node.name,)
        super(SupertypeCreation, self).visit_func_decl(node)
        for p in node.params:
            if self._defs[(self._namespace, p.name)]:
                continue
            self._replace_subtype_with_supertype(
                p, lambda x, y: setattr(x, 'param_type', y))
        self._namespace = initial_namespace

    def visit_variable(self, node):
        namespace = self._namespace
        while len(namespace) > 0:
            if (namespace, node.name) in self._defs:
                self._defs[(namespace, node.name)] = True
                break
            else:
                namespace = namespace[:-1]
