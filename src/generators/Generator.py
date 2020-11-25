import os
from random import Random
import string

from src import utils
from src.ir import ast, types
from src.ir import kotlin_types as kt



class Context(object):
    def __init__(self):
        self._context = {}

    def _add_entity(self, namespace, entity, name, value):
        if namespace in self._context:
            self._context[namespace][entity][name] = value
        else:
            self._context[namespace] = {
                'funcs': {},
                'vars': {},
                'classes': {}
            }
            self._context[namespace][entity][name] = value

    def add_func(self, namespace, func_name, func):
        self._add_entity(namespace, 'funcs', func_name, func)

    def add_var(self, namespace, var_name, var):
        self._add_entity(namespace, 'vars', var_name, var)

    def add_class(self, namespace, class_name, cls):
        self._add_entity(namespace, 'classes', class_name, cls)

    def _get_declarations(self, namespace, decl_type, only_current):
        len_namespace = len(namespace)
        assert len_namespace >= 1
        if len_namespace == 1 or only_current:
            return self._context.get(namespace, {}).get(decl_type, {})
        start = (namespace[0],)
        decls = {}
        for n in namespace[1:]:
            decl = self._context.get(start, {}).get(decl_type)
            if decl is not None:
                decls.update(decl)
            start = start + (n,)
        return decls

    def get_funcs(self, namespace, only_current=False):
        return self._get_declarations(namespace, 'funcs', only_current)

    def get_vars(self, namespace, only_current=False):
        return self._get_declarations(namespace, 'vars', only_current)

    def get_classes(self, namespace, only_current=False):
        return self._get_declarations(namespace, 'classes', only_current)


class Generator(object):

    resource_path = os.path.join(os.path.split(__file__)[0], "resources")

    WORDS = utils.read_lines(os.path.join(resource_path, 'words'))

    BUILTIN_TYPES = [
        kt.Any,
        kt.Integer,
        kt.Short,
        kt.Long,
        kt.Char,
        kt.Float,
        kt.Double,
        kt.Boolean,
        kt.String
    ]

    def __init__(self, max_depth=5, max_fields=3, max_funcs=3, max_params=5):
        self.context = Context()
        self.max_depth = max_depth
        self.max_fields = max_fields
        self.max_funcs = max_funcs
        self.max_params = max_params
        self.depth = 0
        self.r = Random()
        self.namespace = ('global',)

    def gen_identifier(self, ident_type=None):
        w = self.r.choice(self.WORDS)
        if ident_type is None:
            return w
        if ident_type == 'lower':
            return w.lower()
        return w.capitalize()

    def gen_integer_constant(self, expr_type=None):
        return ast.IntegerConstant(self.r.randint(-100, 100))

    def gen_real_constant(self, expr_type=None):
        prefix = str(self.r.randint(0, 100))
        suffix = str(self.r.randint(0, 1000))
        sign = self.r.choice(['', '-'])
        return ast.RealConstant(sign + prefix + "." + suffix)

    def gen_bool_constant(self, expr_type=None):
        return ast.BooleanConstant(self.r.choice(['true', 'false']))

    def gen_char_constant(self, expr_type=None):
        return ast.CharConstant(self.r.choice(
            string.ascii_letters + string.digits))

    def gen_string_constant(self, expr_type=None):
        return ast.StringConstant(self.gen_identifier())

    def gen_field_decl(self):
        name = self.gen_identifier('lower')
        field_type = self.gen_type()
        return ast.FieldDeclaration(name, field_type)

    def gen_param_decl(self):
        name = self.gen_identifier('lower')
        param_type = self.gen_type()
        return ast.ParameterDeclaration(name, param_type)

    def gen_func_decl(self, etype=None):
        func_name = self.gen_identifier('lower')
        initial_namespace = self.namespace
        self.namespace += (func_name,)
        self.depth += 1
        params = []
        for _ in range(self.r.randint(0, self.max_params)):
            p = self.gen_param_decl()
            params.append(p)
            self.context.add_var(self.namespace, p.name, p)
        ret_type = etype or self.gen_type()
        expr = self.generate_expr(ret_type)
        decls = list(self.context.get_vars(self.namespace, True).values()) + \
            list(self.context.get_classes(self.namespace, True).values()) + \
            list(self.context.get_funcs(self.namespace, True).values())
        decls = [d for d in decls
                 if not isinstance(d, ast.ParameterDeclaration)]
        body = ast.Block(decls + [expr])
        self.depth -= 1
        self.namespace = initial_namespace
        return ast.FunctionDeclaration(func_name, params, ret_type, body)

    def gen_class_decl(self):
        class_name = self.gen_identifier('capitalize')
        initial_namespace = self.namespace
        self.namespace += (class_name,)
        self.depth += 1
        fields = []
        for _ in range(self.r.randint(0, self.max_fields)):
            f = self.gen_field_decl()
            fields.append(f)
            self.context.add_var(self.namespace, f.name, f)
        funcs = []
        for _ in range(self.r.randint(0, self.max_funcs)):
            f = self.gen_func_decl()
            funcs.append(f)
            self.context.add_func(('global',), f.name, f)
        self.namespace = initial_namespace
        self.depth -= 1
        return ast.ClassDeclaration(
            class_name,
            superclasses=[],
            fields=fields,
            functions=funcs
        )

    def gen_type(self):
        # Randomly choose whether we should generate a builtin type or not.
        if self.r.choice([True, False]):
            return self.r.choice(self.BUILTIN_TYPES)
        # Get all class declarations in the current namespace
        class_decls = self.context.get_classes(self.namespace)
        if not class_decls:
            # Not class declaration are available in the current namespace
            # so create a new one.
            decl = self.gen_class_decl()
            self.context.add_class(('global',), decl.name, decl)
            return decl.get_type()
        return self.r.choice(list(class_decls.values())).get_type()

    def gen_variable_decl(self, etype=None):
        var_type = etype if etype is not None else self.gen_type()
        self.depth += 1
        expr = self.generate_expr(var_type)
        self.depth -= 1
        return ast.VariableDeclaration(
            self.gen_identifier('lower'),
            expr=expr,
            var_type=var_type)

    def gen_conditional(self, etype):
        self.depth += 1
        cond = self.generate_expr(kt.Boolean)
        true_expr = self.generate_expr(etype)
        false_expr = self.generate_expr(etype)
        self.depth -= 1
        return ast.Conditional(cond, true_expr, false_expr)

    def gen_func_call(self, etype):
        funcs = self.context.get_funcs(self.namespace).values()
        funcs = [f for f in funcs if f.get_type().is_subtype(etype)]
        if not funcs:
            func = self.gen_func_decl(etype)
            self.context.add_func(('global',), func.name, func)
            funcs.append(func)
        f = self.r.choice(funcs)
        args = []
        self.depth += 1
        for p in f.params:
            args.append(self.generate_expr(p.get_type()))
        self.depth -= 1
        return ast.FunctionCall(f.name, args)

    def gen_new(self, etype):
        news = {
            kt.Any: ast.New('Any', args=[]),
            kt.Unit: ast.New('Unit', args=[])
        }
        con = news.get(etype)
        if con is not None:
            return con
        class_decl = self.context.get_classes(self.namespace).get(etype.name)
        self.depth += 1
        args = []
        for f in class_decl.fields:
            args.append(self.generate_expr(f.get_type()))
        self.depth -= 1
        return ast.New(class_decl.name, args)

    def gen_variable(self, etype):
        # Get all variables declared in the current namespace or
        # the outer namespace.
        variables = self.context.get_vars(self.namespace)
        if etype is not None:
            # If we need to use a variable of a specific types, then filter
            # all variables that match this specific type.
            variables = [v for v in variables.values()
                         if v.get_type().is_subtype(etype)]
        if not variables:
            # If there are not variable declarations that match our criteria,
            # we have to create a new variable declaration.
            var_decl = self.gen_variable_decl(etype)
            self.context.add_var(self.namespace, var_decl.name, var_decl)
            return ast.Variable(var_decl.name)
        return ast.Variable(self.r.choice([v.name for v in variables]))

    def generate_main_func(self):
        initial_namespace = self.namespace
        self.namespace += ('main', )
        self.depth += 1
        expr = self.generate_expr()
        self.depth -= 1
        main_func = ast.FunctionDeclaration(
            "main", params=[], ret_type=kt.Unit, body=ast.Block([expr]))
        self.namespace = initial_namespace
        return main_func

    def generate_expr(self, expr_type=None):
        leaf_canidates = [
            self.gen_new,
            self.gen_variable
        ]
        constant_candidates = {
            kt.Integer: self.gen_integer_constant,
            kt.Short: self.gen_integer_constant,
            kt.Long: self.gen_integer_constant,
            kt.Float: self.gen_real_constant,
            kt.Double: self.gen_real_constant,
            kt.Char: self.gen_char_constant,
            kt.String: self.gen_string_constant,
            kt.Boolean: self.gen_bool_constant
        }
        other_candidates = [
            self.gen_func_call,
            self.gen_conditional
        ]
        expr_type = expr_type or self.gen_type()
        if self.depth >= self.max_depth:
            gen_func = constant_candidates.get(expr_type)
            if gen_func:
                return gen_func()
            return self.r.choice(leaf_canidates)(expr_type)
        self.depth += 1
        con_candidate = constant_candidates.get(expr_type)
        if con_candidate is not None:
            candidates = [self.gen_variable, con_candidate]
        else:
            candidates = leaf_canidates
        return self.r.choice(candidates + other_candidates)(expr_type)

    def gen_top_level_declaration(self):
        candidates = [
            (self.gen_variable_decl, self.context.add_var),
            (self.gen_class_decl, self.context.add_class),
            (self.gen_func_decl, self.context.add_func)
        ]
        gen_func, upd_context = self.r.choice(candidates)
        decl = gen_func()
        upd_context(self.namespace, decl.name, decl)

    def generate(self):
        for _ in range(0, self.r.randint(0, 10)):
            self.gen_top_level_declaration()
        main_func = self.generate_main_func()
        decls = sum([
            list(self.context.get_vars(self.namespace, True).values()),
            list(self.context.get_funcs(self.namespace, True).values()),
            list(self.context.get_classes(self.namespace, True).values())
        ], [])
        decls.append(main_func)
        return ast.Program(decls)
