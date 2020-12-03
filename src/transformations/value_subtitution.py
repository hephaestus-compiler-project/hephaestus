from copy import deepcopy
from collections import defaultdict

from src import utils
from src.ir import ast
from src.ir import kotlin_types as kt
from src.generators import Generator
from src.transformations.base import Transformation


class ValueSubtitution(Transformation):

    CORRECTNESS_PRESERVING = True
    NAME = 'Value Subtitution'

    def __init__(self):
        super(ValueSubtitution, self).__init__()
        self.program = None
        self.generator = None
        self.types = []

    def visit_program(self, node):
        self.generator = Generator(context=node.context)
        usr_types = [d for d in node.declarations
                     if isinstance(d, ast.ClassDeclaration)] + \
            self.generator.BUILTIN_TYPES
        self.types = usr_types
        usr_types.remove(kt.Any)
        new_node = super(ValueSubtitution, self).visit_program(node)
        if self.transform:
            self.program = new_node
        return new_node

    def generate_new(self, class_decl):
        return ast.New(
            class_decl.get_type(),
            args=[self.generator.generate_expr(f.field_type, only_leaves=True)
                  for f in class_decl.fields])

    def _find_subclasses(self, node):
        con_type = node.class_type
        subclasses = []
        for sub_c in self.types:
            if isinstance(sub_c, ast.ClassDeclaration):
                sub_t = sub_c.get_type()
            else:
                sub_t = sub_c
            if sub_t == con_type:
                continue
            if sub_t.is_subtype(con_type):
                subclasses.append(sub_c)
        return subclasses

    def visit_new(self, node):
        # If this node has children then randomly decide if we
        # gonna subtitute one of its children or the current node.
        if node.children() and utils.random.bool():
            return super(ValueSubtitution, self).visit_new(node)
        subclasses = self._find_subclasses(node)
        if not subclasses:
            return node
        self.transform = True
        sub_c = utils.random.choice(subclasses)
        generators = {
            kt.Boolean: self.generator.gen_bool_constant,
            kt.Char: self.generator.gen_char_constant,
            kt.String: self.generator.gen_string_constant,
            kt.Integer: self.generator.gen_integer_constant,
            kt.Short: self.generator.gen_integer_constant,
            kt.Long: self.generator.gen_integer_constant,
            kt.Float: lambda: self.generator.gen_real_constant(kt.Float),
            kt.Double: self.generator.gen_real_constant,
        }
        generate = generators.get(sub_c, lambda: self.generate_new(sub_c))
        return generate()

class TypeSubtitution(Transformation):
    CORRECTNESS_PRESERVING = True
    NAME = 'Type Subtitution (Widening/Narrowing)'


    def __init__(self):
        super(TypeSubtitution, self).__init__()
        self.program = None
        self.generator = None
        self.types = []
        self._defs = defaultdict(bool)
        self._namespace = ('global',)
        self._current_function = None

    def _find_superclasses(self, etype):
        superclasses = []
        for sub_c in self.types:
            if isinstance(sub_c, ast.ClassDeclaration):
                sub_t = sub_c.get_type()
            else:
                sub_t = sub_c
            if sub_t == etype:
                continue
            if etype.is_subtype(sub_t):
                superclasses.append(sub_c)
        return superclasses

    def _type_widening(self, decl, setter):
        superclasses = self._find_superclasses(decl.get_type())
        if not superclasses:
            return False
        sup_t = utils.random.choice(superclasses)
        if isinstance(sup_t, ast.ClassDeclaration):
            sup_t = sup_t.get_type()
        self.transform = True
        setter(decl, sup_t)
        return True

    def visit_program(self, node):
        self.generator = Generator(context=node.context)
        usr_types = [d for d in node.declarations
                     if isinstance(d, ast.ClassDeclaration)] + \
            self.generator.BUILTIN_TYPES
        self.types = usr_types
        new_node = super(TypeSubtitution, self).visit_program(node)
        if self.transform:
            self.program = new_node
        return new_node

    def _create_function_block(self, function, is_expr, var_decl,
                               declared=False):
        if not declared:
            if_cond = ast.Conditional(is_expr, deepcopy(function.body),
                                      ast.Variable(var_decl.name))
            return ast.Block([var_decl, if_cond])
        if_cond = ast.Conditional(is_expr, deepcopy(function.body[1:]),
                                  ast.Variable(var_decl.name))
        return ast.Block([function.body[0] + if_cond])

    def visit_class_decl(self, node):
        initial_namespace = self._namespace
        self._namespace += (node.name,)
        new_node = super(TypeSubtitution, self).visit_class_decl(node)
        functions = {}
        # Perform type widening on class fields.
        # and find where these fields are used.
        # If necessary modify the body of the functions where these fields
        # are used (for details about function modification,
        # see `visit_func_decl()`).
        for f in new_node.fields:
            old_type = f.field_type
            transform = self._type_widening(
                f, lambda x, y: setattr(x, 'field_type', y))
            if not self._defs[(self._namespace, f.name)] or not transform:
                continue
            fun = self._defs[(self._namespace, f.name)]
            var_decl = functions.get(fun.name)
            is_declared = False
            if var_decl is None:
                # It's the first time to declare the variable for the false
                # branch of the if (x is T) condition.
                var_decl = self.generate_variable_declaration(
                    "field_ret", fun.ret_type)
                functions[fun.name] = var_decl
            else:
                # We have already declared the variable for the else branch.
                is_declared = True
            fun.body = self._create_function_block(
                fun, ast.Is(ast.Variable(f.name), old_type), var_decl,
                is_declared)
        self._namespace = initial_namespace
        return new_node

    def visit_param_decl(self, node):
        self._defs[(self._namespace, node.name)] = False
        return node

    def visit_field_decl(self, node):
        self._defs[(self._namespace, node.name)] = False
        return node

    def generate_variable_declaration(self, name, etype):
        expr = self.generator.generate_expr(etype, only_leaves=True)
        return ast.VariableDeclaration(name, expr, var_type=etype)

    def visit_func_decl(self, node):
        initial_namespace = self._namespace
        self._namespace += (node.name,)
        self._current_function = node
        new_node = super(TypeSubtitution, self).visit_func_decl(node)
        var_decl = self.generate_variable_declaration("ret", node.ret_type)
        is_declared = False
        for p in new_node.params:
            # Perform type widening on this function's parameters.
            old_type = p.param_type
            transform = self._type_widening(
                p, lambda x, y: setattr(x, 'param_type', y))
            if not self._defs[(self._namespace, p.name)] or not transform:
                # If the parameter is not used in the function's body or
                # the type widening operation was not applied,
                # then we are done.
                continue

            # Otherwise, replace the function body as follows
            # fun (x: T1): R = ...
            # =>
            # fun (x: T2): R = {
            #   val ret : R = ...
            #   if (x is T1) ... else ret
            # }
            new_node.body = self._create_function_block(
                new_node, ast.Is(ast.Variable(p.name), old_type), var_decl,
                is_declared)
            is_declared = True
        self._namespace = initial_namespace
        self._current_function = None
        return new_node

    def visit_variable(self, node):
        namespace = self._namespace
        while len(namespace) > 0:
            if (namespace, node.name) in self._defs:
                # Specify the namespace where this variable is used.
                self._defs[(namespace, node.name)] = self._current_function
                break
            else:
                namespace = namespace[:-1]
        return node
