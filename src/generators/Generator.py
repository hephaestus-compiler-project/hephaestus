from typing import Tuple, List

from src import utils
from src.ir import ast, types
from src.ir import kotlin_types as kt
from src.ir.context import Context


class Generator(object):

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

    def __init__(self, max_depth=7, max_fields=2, max_funcs=2, max_params=2,
                 max_var_decls=3, context=None):
        self.context = context or Context()
        self.max_depth = max_depth
        self.max_fields = max_fields
        self.max_funcs = max_funcs
        self.max_params = max_params
        self.max_var_decls = max_var_decls
        self.depth = 1
        self._vars_in_context = {}
        self._new_from_class = None
        self._stop_var = False
        self.namespace = ('global',)

    def gen_identifier(self, ident_type=None):
        w = utils.random.word()
        if ident_type is None:
            return w
        if ident_type == 'lower':
            return w.lower()
        return w.capitalize()

    def gen_integer_constant(self, expr_type=None):
        return ast.IntegerConstant(utils.random.integer(-100, 100),
                                   expr_type)

    def gen_real_constant(self, expr_type=None):
        prefix = str(utils.random.integer(0, 100))
        suffix = str(utils.random.integer(0, 1000))
        sign = utils.random.choice(['', '-'])
        if expr_type == kt.Float:
            suffix += "f"
        return ast.RealConstant(sign + prefix + "." + suffix)

    def gen_bool_constant(self, expr_type=None):
        return ast.BooleanConstant(
            utils.random.choice(['true', 'false']))

    def gen_char_constant(self, expr_type=None):
        return ast.CharConstant(utils.random.char())

    def gen_string_constant(self, expr_type=None):
        return ast.StringConstant(self.gen_identifier())

    def gen_equality_expr(self, expr_type=None, only_leaves=False):
        initial_depth = self.depth
        self.depth += 1
        etype = self.gen_type()
        prev = self._new_from_class
        if not isinstance(etype, types.Builtin):
            # We need this because if are going to create two
            # 'New' expressions, they must stem from the same
            # constructor.
            class_decl = self._get_subclass(etype)
            self._new_from_class = (etype, class_decl)
        op = utils.random.choice(ast.EqualityExpr.VALID_OPERATORS)
        e1 = self.generate_expr(etype, only_leaves, subtype=False)
        e2 = self.generate_expr(etype, only_leaves, subtype=False)
        self._new_from_class = prev
        self.depth = initial_depth
        return ast.EqualityExpr(e1, e2, op)

    def gen_logical_expr(self, expr_type=None, only_leaves=False):
        initial_depth = self.depth
        self.depth += 1
        op = utils.random.choice(ast.LogicalExpr.VALID_OPERATORS)
        e1 = self.generate_expr(kt.Boolean, only_leaves)
        e2 = self.generate_expr(kt.Boolean, only_leaves)
        self.depth = initial_depth
        return ast.LogicalExpr(e1, e2, op)

    def gen_comparison_expr(self, expr_type=None, only_leaves=False):
        valid_types = [
            kt.String,
            kt.Boolean,
            kt.Double,
            kt.Char,
            kt.Float,
            kt.Integer,
            kt.Short,
            kt.Long
        ]
        number_types = [
            kt.Short,
            kt.Integer,
            kt.Long,
            kt.Float,
            kt.Double,
        ]
        e2_types = {
            kt.String: [kt.String],
            kt.Boolean: [kt.Boolean],
            kt.Double: number_types,
            kt.Char: [kt.Char],
            kt.Float: number_types,
            kt.Integer: number_types,
            kt.Short: number_types,
            kt.Long: number_types
        }
        initial_depth = self.depth
        self.depth += 1
        op = utils.random.choice(ast.ComparisonExpr.VALID_OPERATORS)
        e1_type = utils.random.choice(valid_types)
        e2_type = utils.random.choice(e2_types[e1_type])
        e1 = self.generate_expr(e1_type, only_leaves)
        e2 = self.generate_expr(e2_type, only_leaves)
        self.depth = initial_depth
        return ast.ComparisonExpr(e1, e2, op)

    def gen_field_decl(self, etype=None):
        name = self.gen_identifier('lower')
        field_type = etype or self.gen_type()
        return ast.FieldDeclaration(name, field_type)

    def gen_param_decl(self, etype=None):
        name = self.gen_identifier('lower')
        param_type = etype or self.gen_type()
        return ast.ParameterDeclaration(name, param_type)

    def _get_func_ret_type(self, params, etype):
        if etype is not None:
            return etype
        param_types = [p.param_type for p in params]
        if param_types and utils.random.bool():
            return utils.random.choice(param_types)
        return self.gen_type()

    def gen_func_decl(self, etype=None):
        func_name = self.gen_identifier('lower')
        initial_namespace = self.namespace
        self.namespace += (func_name,)
        initial_depth = self.depth
        self.depth += 1
        params = []
        for _ in range(utils.random.integer(0, self.max_params)):
            p = self.gen_param_decl()
            params.append(p)
            self.context.add_var(self.namespace, p.name, p)
        ret_type = self._get_func_ret_type(params, etype)
        expr = self.generate_expr(ret_type)
        decls = list(self.context.get_declarations(
            self.namespace, True).values())
        decls = [d for d in decls
                 if not isinstance(d, ast.ParameterDeclaration)]
        body = ast.Block(decls + [expr])
        self.depth = initial_depth
        self.namespace = initial_namespace
        if self.namespace[-1][0].isupper():
            func_type = ast.FunctionDeclaration.CLASS_METHOD
        else:
            func_type = ast.FunctionDeclaration.FUNCTION
        return ast.FunctionDeclaration(
            func_name, params, ret_type, body, func_type=func_type)

    def _add_field_to_class(self, field, fields):
        fields.append(field)
        self.context.add_var(self.namespace, field.name, field)

    def _add_func_to_class(self, func, funcs):
        funcs.append(func)
        self.context.add_func(self.namespace, func.name, func)

    def gen_class_decl(self, field_type=None, fret_type=None):
        class_name = self.gen_identifier('capitalize')
        initial_namespace = self.namespace
        self.namespace += (class_name,)
        initial_depth = self.depth
        self.depth += 1
        fields = []
        max_fields = self.max_fields - 1 if field_type else self.max_fields
        max_funcs = self.max_funcs - 1 if fret_type else self.max_funcs
        if field_type:
            self._add_field_to_class(self.gen_field_decl(field_type),
                                     fields)
        for _ in range(utils.random.integer(0, max_fields)):
            self._add_field_to_class(self.gen_field_decl(), fields)
        funcs = []
        if fret_type:
            self._add_func_to_class(self.gen_func_decl(fret_type), funcs)
        for _ in range(utils.random.integer(0, max_funcs)):
            self._add_func_to_class(self.gen_func_decl(), funcs)
        self.namespace = initial_namespace
        self.depth = initial_depth
        return ast.ClassDeclaration(
            class_name,
            superclasses=[],
            fields=fields,
            functions=funcs
        )

    def gen_type(self):
        # Randomly choose whether we should generate a builtin type or not.
        if utils.random.bool():
            return utils.random.choice(self.BUILTIN_TYPES)
        # Get all class declarations in the current namespace
        class_decls = self.context.get_classes(self.namespace)
        if not class_decls:
            # Not class declaration are available in the current namespace
            # so create a new one.
            initial_namespace = self.namespace
            self.namespace = ('global',)
            decl = self.gen_class_decl()
            self.context.add_class(self.namespace, decl.name, decl)
            self.namespace = initial_namespace
            return decl.get_type()
        return utils.random.choice(list(class_decls.values())).get_type()

    def gen_variable_decl(self, etype=None, only_leaves=False):
        var_type = etype if etype else self.gen_type()
        initial_depth = self.depth
        self.depth += 1
        expr = self.generate_expr(var_type, only_leaves)
        self.depth = initial_depth
        return ast.VariableDeclaration(
            self.gen_identifier('lower'),
            expr=expr,
            var_type=var_type)

    def gen_conditional(self, etype, only_leaves=False, subtype=True):
        initial_depth = self.depth
        self.depth += 1
        cond = self.generate_expr(kt.Boolean, only_leaves)
        true_expr = self.generate_expr(etype, only_leaves, subtype)
        false_expr = self.generate_expr(etype, only_leaves, subtype)
        self.depth = initial_depth
        return ast.Conditional(cond, true_expr, false_expr)

    def _get_matching_objects(self, etype, subtype,
                              attr_name) -> List[Tuple[ast.Expr, ast.Declaration]]:
        decls = []
        for v in self.context.get_vars(self.namespace).values():
            var_type = v.get_type()
            # We are only interested in variables of class types.
            if isinstance(var_type, types.Builtin):
                continue
            cls = self._get_class(var_type)
            assert cls is not None
            for f in getattr(cls, attr_name):
                t = f.get_type()
                if not t:
                    continue
                cond = t.is_subtype(etype) if subtype else t == etype
                if not cond:
                    continue
                decls.append((ast.Variable(v.name), f))
        return decls

    def _get_function_declarations(self, etype,
                                   subtype) -> List[Tuple[ast.Expr, ast.Declaration]]:
        functions = []
        # First find all top-level functions or methods included
        # in the current class.
        for f in self.context.get_funcs(self.namespace).values():
            if not f.ret_type:
                continue
            cond = (
                f.ret_type.is_subtype(etype)
                if subtype else f.ret_type == etype)
            # The receiver object for this kind of functions is None.
            if not cond:
                continue
            functions.append((None, f))
        return functions + self._get_matching_objects(etype, subtype,
                                                      'functions')

    def _get_matching_class(self, etype, subtype,
                            attr_name) -> Tuple[ast.ClassDeclaration, ast.Declaration]:
        class_decls = []
        for c in self.context.get_classes(self.namespace).values():
            for f in getattr(c, attr_name):
                t = f.get_type()
                if not t:
                    continue
                cond = t.is_subtype(etype) if subtype else t == etype
                if not cond:
                    continue
                # Now here we keep the class and the function that match
                # the given type.
                class_decls.append((c, f))
        if not class_decls:
            return None
        return utils.random.choice(class_decls)

    def _gen_matching_class(self, etype,
                            attr_name) -> Tuple[ast.ClassDeclaration, ast.Declaration]:
        initial_namespace = self.namespace
        self.namespace = ast.GLOBAL_NAMESPACE
        if attr_name == 'functions':
            kwargs = {'fret_type': etype}
        else:
            kwargs = {'field_type': etype}
        cls = self.gen_class_decl(**kwargs)
        self.context.add_class(self.namespace, cls.name, cls)
        self.namespace = initial_namespace
        for f in getattr(cls, attr_name):
            if f.get_type() == etype:
                return cls, f

    def _gen_matching_func(self, etype) -> Tuple[ast.ClassDeclaration, ast.Declaration]:
        # Randomly choose to generate a function or a class method.
        if utils.random.bool():
            initial_namespace = self.namespace
            self.namespace = (self.namespace
                              if utils.random.bool() else ast.GLOBAL_NAMESPACE)
            # Generate a function
            func = self.gen_func_decl(etype)
            self.context.add_func(self.namespace, func.name, func)
            self.namespace = initial_namespace
            return None, func
        # Generate a class containing the requested function
        return self._gen_matching_class(etype, 'functions')

    def gen_func_call(self, etype, only_leaves=False, subtype=True):
        funcs = self._get_function_declarations(etype, subtype)
        if not funcs:
            cls_fun = self._get_matching_class(etype, subtype, 'functions')
            if cls_fun is None:
                # Here, we generate a function or a class containing a function
                # whose return type is 'etype'.
                cls_fun = self._gen_matching_func(etype)
            cls, f = cls_fun
            receiver = None if cls is None else self.generate_expr(
                cls.get_type(), only_leaves)
            funcs.append((receiver, f))
        receiver, f = utils.random.choice(funcs)
        args = []
        initial_depth = self.depth
        self.depth += 1
        for p in f.params:
            args.append(self.generate_expr(p.get_type(), only_leaves))
        self.depth = initial_depth
        return ast.FunctionCall(f.name, args, receiver)

    def gen_field_access(self, etype, only_leaves=False, subtype=True):
        objs = self._get_matching_objects(etype, subtype, 'fields')
        if not objs:
            cls_f = self._get_matching_class(etype, subtype, 'fields')
            if cls_f is None:
                cls_f = self._gen_matching_class(etype, 'fields')
            cls, f = cls_f
            receiver = self.generate_expr(cls.get_type(), only_leaves)
            objs.append((receiver, f))
        receiver, f = utils.random.choice(objs)
        return ast.FieldAccess(receiver, f.name)

    def _get_class(self, etype: types.Type):
        # Get class declaration based on the given type.
        class_decls = self.context.get_classes(self.namespace).values()
        for c in class_decls:
            t = c.get_type()
            if t.is_subtype(etype) and t.name == etype.name:
                return c

    def _get_subclass(self, etype: types.Type):
        class_decls = self.context.get_classes(self.namespace).values()
        # Get all classes that are subtype of the given type, and there
        # are regular classes (no interfaces or abstract classes).
        class_decls = [c for c in class_decls
                       if (c.get_type().is_subtype(etype) and
                           c.class_type == ast.ClassDeclaration.REGULAR)]
        return utils.random.choice(
            [s for s in class_decls if s.name == etype.name] or class_decls)

    def gen_new(self, etype, only_leaves=False, subtype=True):
        news = {
            kt.Any: ast.New(kt.Any, args=[]),
            kt.Unit: ast.New(kt.Unit, args=[])
        }
        con = news.get(etype)
        if con is not None:
            return con
        etype2, from_class = (
            self._new_from_class
            if self._new_from_class else (None, None))
        class_decl = (
            from_class
            if etype2 == etype else self._get_subclass(etype))
        initial_depth = self.depth
        self.depth += 1
        args = []
        prev = self._new_from_class
        self._new_from_class = None
        for f in class_decl.fields:
            args.append(self.generate_expr(f.get_type(), only_leaves))
        self._new_from_class = prev
        self.depth = initial_depth
        return ast.New(class_decl.get_type(), args)

    def gen_variable(self, etype, only_leaves=False, subtype=True):
        # Get all variables declared in the current namespace or
        # the outer namespace.
        variables = self.context.get_vars(self.namespace)
        # If we need to use a variable of a specific types, then filter
        # all variables that match this specific type.
        if subtype:
            fun = lambda v, t: v.get_type().is_subtype(t)
        else:
            fun = lambda v, t: v.get_type() == t
        variables = [v for v in variables.values() if fun(v, etype)]
        if not variables:
            if self.namespace in self._vars_in_context:
                self._vars_in_context[self.namespace] += 1
            else:
                self._vars_in_context[self.namespace] = 1
            self._stop_var = True
            # If there are not variable declarations that match our criteria,
            # we have to create a new variable declaration.
            var_decl = self.gen_variable_decl(etype, only_leaves)
            self._stop_var = False
            self.context.add_var(self.namespace, var_decl.name, var_decl)
            return ast.Variable(var_decl.name)
        varia = utils.random.choice([v.name for v in variables])
        return ast.Variable(varia)

    def generate_main_func(self):
        initial_namespace = self.namespace
        self.namespace += ('main', )
        initial_depth = self.depth
        self.depth += 1
        expr = self.generate_expr()
        decls = list(self.context.get_declarations(
            self.namespace, True).values())
        decls = [d for d in decls
                 if not isinstance(d, ast.ParameterDeclaration)]
        body = ast.Block(decls + [expr])
        self.depth = initial_depth
        main_func = ast.FunctionDeclaration(
            "main", params=[], ret_type=kt.Unit, body=body,
            func_type=ast.FunctionDeclaration.FUNCTION)
        self.namespace = initial_namespace
        return main_func

    def generate_expr(self, expr_type=None, only_leaves=False, subtype=True):
        def gen_variable(x):
            return self.gen_variable(x, only_leaves, subtype)

        leaf_canidates = [
            lambda x: self.gen_new(x, only_leaves, subtype),
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
        binary_ops = {
            kt.Boolean: [
                lambda x: self.gen_logical_expr(x, only_leaves),
                lambda x: self.gen_equality_expr(only_leaves),
                lambda x: self.gen_comparison_expr(only_leaves)
            ],
        }
        other_candidates = [
            lambda x: self.gen_field_access(x, only_leaves, subtype),
            lambda x: self.gen_func_call(x, only_leaves=only_leaves,
                                         subtype=subtype),
            lambda x: self.gen_conditional(x, only_leaves=only_leaves,
                                           subtype=subtype),
            gen_variable
        ]
        expr_type = expr_type or self.gen_type()
        if self.depth >= self.max_depth or only_leaves:
            gen_func = constant_candidates.get(expr_type)
            if gen_func:
                return gen_func(expr_type)
            gen_var = self._vars_in_context.get(
                self.namespace, 0) < self.max_var_decls and not (
                    self._stop_var or only_leaves)
            if gen_var:
                # Decide if we can generate a variable.
                # If the maximum numbers of variables in a specific context
                # has been reached, or we have previously declared a variable
                # of a specific type, then we should avoid variable creation.
                leaf_canidates.append(gen_variable)
            return utils.random.choice(leaf_canidates)(expr_type)
        con_candidate = constant_candidates.get(expr_type)
        if con_candidate is not None:
            candidates = [gen_variable, con_candidate] + binary_ops.get(
                expr_type, [])
        else:
            candidates = leaf_canidates
        return utils.random.choice(candidates + other_candidates)(expr_type)

    def gen_top_level_declaration(self):
        candidates = [
            (self.gen_variable_decl, self.context.add_var),
            (self.gen_class_decl, self.context.add_class),
            (self.gen_func_decl, self.context.add_func)
        ]
        gen_func, upd_context = utils.random.choice(candidates)
        decl = gen_func()
        upd_context(self.namespace, decl.name, decl)

    def generate(self):
        for _ in range(0, utils.random.integer(0, 10)):
            self.gen_top_level_declaration()
        main_func = self.generate_main_func()
        self.namespace = ('global',)
        self.context.add_func(self.namespace, 'main', main_func)
        return ast.Program(self.context)
