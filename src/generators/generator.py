# pylint: disable=too-many-instance-attributes,too-many-arguments,dangerous-default-value
from collections import defaultdict
from typing import Tuple, List

from src import utils as ut
from src.generators import utils as gu
from src.ir import ast, types, type_utils as tu, kotlin_types as kt
from src.ir.context import Context
from src.ir.builtins import BuiltinFactory
from src.ir import BUILTIN_FACTORIES


class Generator():

    def __init__(self, max_depth=7, max_fields=2, max_funcs=2, max_params=2,
                 max_var_decls=3, max_side_effects=1,
                 language=None,
                 options={},
                 context=None):
        assert language is not None, "You must specify the language"
        self.language = language
        self.context = context or Context()
        self.bt_factory: BuiltinFactory = BUILTIN_FACTORIES[language]
        self.max_depth = max_depth
        self.max_fields = max_fields
        self.max_funcs = max_funcs
        self.max_params = max_params
        self.max_var_decls = max_var_decls
        self.max_side_effects = max_side_effects
        self.disable_inference_in_closures = options.get(
            "disable_inference_in_closures", False)
        self.depth = 1
        self._vars_in_context = defaultdict(lambda: 0)
        self._new_from_class = None
        self.namespace = ('global',)

        self.ret_builtin_types = self.bt_factory.get_non_nothing_types()
        self.builtin_types = self.ret_builtin_types + \
            [self.bt_factory.get_void_type()]

    # pylint: disable=unused-argument
    def gen_equality_expr(self, expr_type=None, only_leaves=False):
        initial_depth = self.depth
        self.depth += 1
        etype = self.gen_type()
        prev = self._new_from_class
        if not tu.is_builtin(etype, self.bt_factory):
            # We need this because if are going to create two
            # 'New' expressions, they must stem from the same
            # constructor.
            class_decl = self._get_subclass(etype)
            self._new_from_class = (etype, class_decl)
        op = ut.random.choice(ast.EqualityExpr.VALID_OPERATORS[self.language])
        e1 = self.generate_expr(etype, only_leaves, subtype=False)
        e2 = self.generate_expr(etype, only_leaves, subtype=False)
        self._new_from_class = prev
        self.depth = initial_depth
        return ast.EqualityExpr(e1, e2, op)

    # pylint: disable=unused-argument
    def gen_logical_expr(self, expr_type=None, only_leaves=False):
        initial_depth = self.depth
        self.depth += 1
        op = ut.random.choice(ast.LogicalExpr.VALID_OPERATORS[self.language])
        e1 = self.generate_expr(self.bt_factory.get_boolean_type(),
                                only_leaves)
        e2 = self.generate_expr(self.bt_factory.get_boolean_type(),
                                only_leaves)
        self.depth = initial_depth
        return ast.LogicalExpr(e1, e2, op)

    # pylint: disable=unused-argument
    def gen_comparison_expr(self, expr_type=None, only_leaves=False):
        valid_types = [
            self.bt_factory.get_string_type(),
            self.bt_factory.get_boolean_type(),
            self.bt_factory.get_double_type(),
            self.bt_factory.get_char_type(),
            self.bt_factory.get_float_type(),
            self.bt_factory.get_integer_type(),
            self.bt_factory.get_byte_type(),
            self.bt_factory.get_short_type(),
            self.bt_factory.get_long_type(),
            self.bt_factory.get_big_decimal_type(),
            self.bt_factory.get_big_integer_type(),
        ]
        number_types = self.bt_factory.get_number_types()
        e2_types = {
            self.bt_factory.get_string_type(): [
                self.bt_factory.get_string_type()
            ],
            self.bt_factory.get_boolean_type(): [
                self.bt_factory.get_boolean_type()
            ],
            self.bt_factory.get_double_type(): number_types,
            self.bt_factory.get_big_decimal_type(): number_types,
            self.bt_factory.get_char_type(): [
                self.bt_factory.get_char_type()
            ],
            self.bt_factory.get_float_type(): number_types,
            self.bt_factory.get_integer_type(): number_types,
            self.bt_factory.get_big_integer_type(): number_types,
            self.bt_factory.get_byte_type(): number_types,
            self.bt_factory.get_short_type(): number_types,
            self.bt_factory.get_long_type(): number_types
        }
        initial_depth = self.depth
        self.depth += 1
        op = ut.random.choice(
            ast.ComparisonExpr.VALID_OPERATORS[self.language])
        e1_type = ut.random.choice(valid_types)
        e2_type = ut.random.choice(e2_types[e1_type])
        e1 = self.generate_expr(e1_type, only_leaves)
        e2 = self.generate_expr(e2_type, only_leaves)
        self.depth = initial_depth
        return ast.ComparisonExpr(e1, e2, op)

    def gen_field_decl(self, etype=None):
        name = gu.gen_identifier('lower')
        field_type = etype or self.gen_type()
        return ast.FieldDeclaration(name, field_type,
                                    is_final=ut.random.bool())

    def gen_param_decl(self, etype=None):
        name = gu.gen_identifier('lower')
        param_type = etype or self.gen_type()
        return ast.ParameterDeclaration(name, param_type)

    def _get_func_ret_type(self, params, etype, not_void=False):
        if etype is not None:
            return etype
        param_types = [p.param_type for p in params]
        if param_types and ut.random.bool():
            return ut.random.choice(param_types)
        return self.gen_type(ret_types=not_void)

    def can_infer_function_ret_type(self, func_expr, decls):
        if not self.disable_inference_in_closures:
            return True

        # We want to disable inference in the following situations
        # fun foo(x: Any) {
        #    if (x is String) {
        #       fun bar() = x
        #       return bar()
        #    } else return ""
        # }
        # This will help us to avoid the repetition of an already discovered
        # bug.
        if not isinstance(func_expr, ast.Variable):
            return True

        return func_expr.name in {d.name for d in decls}

    def _gen_side_effects(self):
        # Generate a number of expressions with side-effects, e.g.,
        # assignment, variable declaration, etc.
        exprs = []
        for _ in range(ut.random.integer(0, self.max_side_effects)):
            expr = self.generate_expr(self.bt_factory.get_void_type())
            if expr:
                exprs.append(expr)
        # These are the new declarations that we created as part of the side-
        # effects.
        decls = list(self.context.get_declarations(self.namespace,
                                                   True).values())
        decls = [d for d in decls
                 if not isinstance(d, ast.ParameterDeclaration)]
        return exprs, decls

    def _can_vararg_param(self, param):
        if self.language == 'kotlin':
            # XXX Can we do this in a better way? without hardcode?
            # Actually in Kotlin, the type of varargs is Array<out T>.
            # So, until we add support for use-site variance, we support
            # varargs for 'primitive' types only which kotlinc treats them
            # as specialized arrays.
            t_constructor = getattr(param.get_type(), 't_constructor', None)
            return isinstance(t_constructor, kt.SpecializedArrayType)
        # A vararg is actually a syntactic sugar for a parameter whose type
        # is an array of something.
        return param.get_type().name == 'Array'

    def _gen_func_params(self):
        params = []
        arr_index = None
        vararg_found = False
        vararg = None
        for i in range(ut.random.integer(0, self.max_params)):
            param = self.gen_param_decl()
            # If the type of the parameter is an array consider make it
            # a vararg.
            if not vararg_found and self._can_vararg_param(param) and (
                    ut.random.bool()):
                param.vararg = True
                arr_index = i
                vararg = param
                vararg_found = True
            params.append(param)
            self.context.add_var(self.namespace, param.name, param)
        len_p = len(params)
        # If one of the parameters is a vararg, then place it to the back.
        if arr_index is not None and arr_index != len_p - 1:
            params[len_p - 1], params[arr_index] = vararg, params[len_p - 1]
        return params

    def gen_func_decl(self, etype=None, not_void=False):
        func_name = gu.gen_identifier('lower')
        initial_namespace = self.namespace
        self.namespace += (func_name,)
        initial_depth = self.depth
        self.depth += 1
        # Check if this function we want to generate is nested, by checking
        # the name of the outer namespace. If we are in class then
        # the outer namespace begins with capital letter.
        class_method = self.namespace[-1][0].isupper()
        params = self._gen_func_params()
        ret_type = self._get_func_ret_type(params, etype, not_void=not_void)
        expr_type = self.gen_type(False) \
            if ret_type == self.bt_factory.get_void_type() else ret_type
        expr = self.generate_expr(expr_type)
        decls = list(self.context.get_declarations(
            self.namespace, True).values())
        var_decls = [d for d in decls
                     if not isinstance(d, ast.ParameterDeclaration)]
        if (not var_decls and
                ret_type != self.bt_factory.get_void_type() and
                self.can_infer_function_ret_type(expr, decls)):
            # The function does not contain any declarations and its return
            # type is not Unit. So, we can create an expression-based function.
            inferred_type = ret_type
            body = expr
            # If the return type is Number, then this must be explicit.
            if ret_type != self.bt_factory.get_number_type():
                ret_type = None
        else:
            inferred_type = None
            exprs, decls = self._gen_side_effects()
            body = ast.Block(decls + exprs + [expr])
        self.depth = initial_depth
        self.namespace = initial_namespace
        return ast.FunctionDeclaration(
            func_name, params, ret_type, body,
            func_type=(ast.FunctionDeclaration.CLASS_METHOD
                       if class_method
                       else ast.FunctionDeclaration.FUNCTION),
            inferred_type=inferred_type)

    def _add_field_to_class(self, field, fields):
        fields.append(field)
        self.context.add_var(self.namespace, field.name, field)

    def _add_func_to_class(self, func, funcs):
        funcs.append(func)
        self.context.add_func(self.namespace, func.name, func)

    def gen_class_decl(self, field_type=None, fret_type=None, not_void=False):
        class_name = gu.gen_identifier('capitalize')
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
        for _ in range(ut.random.integer(0, max_fields)):
            self._add_field_to_class(self.gen_field_decl(), fields)
        funcs = []
        if fret_type:
            self._add_func_to_class(
                self.gen_func_decl(fret_type, not_void=not_void), funcs)
        for _ in range(ut.random.integer(0, max_funcs)):
            self._add_func_to_class(
                self.gen_func_decl(not_void=not_void), funcs)
        self.namespace = initial_namespace
        self.depth = initial_depth
        return ast.ClassDeclaration(
            class_name,
            superclasses=[],
            fields=fields,
            functions=funcs
        )

    def gen_array_expr(self, expr_type, only_leaves=False, subtype=True):
        arr_len = ut.random.integer(0, 3)
        etype = expr_type.type_args[0]
        exprs = [
            self.generate_expr(etype, only_leaves=only_leaves, subtype=subtype)
            for _ in range(arr_len)
        ]
        return ast.ArrayExpr(expr_type, arr_len, exprs)

    def gen_type(self, ret_types=True):
        class_decls = self.context.get_classes(self.namespace)
        # Randomly choose whether we should generate a builtin type or not.
        if not class_decls or ut.random.bool():
            builtins = self.ret_builtin_types if ret_types \
                else self.builtin_types
            etype = ut.random.choice(builtins)
        else:
            etype = ut.random.choice(list(class_decls.values())).get_type()
        if not isinstance(etype, types.TypeConstructor):
            return etype
        # We have to instantiate type constructor with random type arguments.
        t_args = []
        candiate_types = list(self.ret_builtin_types)
        candiate_types.remove(self.bt_factory.get_array_type())
        usr_types = [
            c.get_type()
            for c in self.context.get_classes(self.namespace).values()
        ]
        candiate_types.extend(usr_types)

        for _ in etype.type_parameters:
            t_args.append(ut.random.choice(candiate_types))
        return etype.new(t_args)

    def gen_variable_decl(self, etype=None, only_leaves=False,
                          expr=None):
        var_type = etype if etype else self.gen_type()
        initial_depth = self.depth
        self.depth += 1
        expr = expr or self.generate_expr(var_type, only_leaves)
        self.depth = initial_depth
        is_final = ut.random.bool()
        # We never omit type in non-final variables.
        vtype = (
            var_type
            if ut.random.bool() or
            not is_final or etype == self.bt_factory.get_number_type()
            else None)
        return ast.VariableDeclaration(
            gu.gen_identifier('lower'),
            expr=expr,
            is_final=is_final,
            var_type=vtype,
            inferred_type=var_type)

    def gen_conditional(self, etype, only_leaves=False, subtype=True):
        initial_depth = self.depth
        self.depth += 3
        cond = self.generate_expr(self.bt_factory.get_boolean_type(),
                                  only_leaves)
        true_expr = self.generate_expr(etype, only_leaves, subtype)
        false_expr = self.generate_expr(etype, only_leaves, subtype)
        self.depth = initial_depth
        return ast.Conditional(cond, true_expr, false_expr)

    def _get_matching_objects(self, etype, subtype, attr_name) -> \
            List[Tuple[ast.Expr, ast.Declaration]]:
        decls = []
        for var in self.context.get_vars(self.namespace).values():
            var_type = var.get_type()
            # We are only interested in variables of class types.
            if tu.is_builtin(var_type, self.bt_factory):
                continue
            cls = self._get_class(var_type)
            assert cls is not None
            for attr in getattr(cls, attr_name):  # function or field
                attr_type = attr.get_type()
                if not attr_type:
                    continue
                if attr_type == self.bt_factory.get_void_type():
                    continue
                cond = attr_type.is_assignable(etype) if subtype \
                    else attr_type == etype
                if not cond:
                    continue
                decls.append((ast.Variable(var.name), attr))
        return decls

    def _get_function_declarations(self, etype, subtype) -> \
            List[Tuple[ast.Expr, ast.Declaration]]:
        functions = []
        # First find all top-level functions or methods included
        # in the current class.
        for func in self.context.get_funcs(self.namespace).values():
            cond = (
                func.get_type() != self.bt_factory.get_void_type() and
                func.get_type().is_assignable(etype)
                if subtype else func.get_type() == etype)
            # The receiver object for this kind of functions is None.
            if not cond:
                continue
            functions.append((None, func))
        return functions + self._get_matching_objects(etype, subtype,
                                                      'functions')

    def _get_matching_class(self, etype, subtype, attr_name) -> \
            Tuple[ast.ClassDeclaration, ast.Declaration]:
        class_decls = []
        for c in self.context.get_classes(self.namespace).values():
            for attr in getattr(c, attr_name):  # field or function
                attr_type = attr.get_type()
                if not attr_type:
                    continue
                if attr_type == self.bt_factory.get_void_type():
                    continue
                cond = attr_type.is_assignable(etype) if subtype else \
                    attr_type == etype
                if not cond:
                    continue
                # Now here we keep the class and the function that match
                # the given type.
                class_decls.append((c, attr))
        if not class_decls:
            return None
        return ut.random.choice(class_decls)

    def _gen_matching_class(self, etype, attr_name, not_void=False) -> \
            Tuple[ast.ClassDeclaration, ast.Declaration]:
        initial_namespace = self.namespace
        self.namespace = ast.GLOBAL_NAMESPACE
        if attr_name == 'functions':
            kwargs = {'fret_type': etype}
        else:
            kwargs = {'field_type': etype}
        cls = self.gen_class_decl(**kwargs, not_void=not_void)
        self.context.add_class(self.namespace, cls.name, cls)
        self.namespace = initial_namespace
        for attr in getattr(cls, attr_name):
            if attr.get_type() == etype:
                return cls, attr
        return None

    def _gen_matching_func(self, etype, not_void=False) -> \
            Tuple[ast.ClassDeclaration, ast.Declaration]:
        # Randomly choose to generate a function or a class method.
        if ut.random.bool():
            initial_namespace = self.namespace
            self.namespace = (self.namespace
                              if ut.random.bool() else ast.GLOBAL_NAMESPACE)
            # Generate a function
            func = self.gen_func_decl(etype, not_void=not_void)
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
                cls_fun = self._gen_matching_func(etype, not_void=True)
            cls, func = cls_fun
            receiver = None if cls is None else self.generate_expr(
                cls.get_type(), only_leaves)
            funcs.append((receiver, func))
        receiver, func = ut.random.choice(funcs)
        args = []
        initial_depth = self.depth
        self.depth += 1
        for param in func.params:
            if not param.vararg:
                args.append(self.generate_expr(param.get_type(), only_leaves))
            else:
                # This param is a vararg, so provide a random number of
                # arguments.
                for _ in range(ut.random.integer(0, 3)):
                    args.append(self.generate_expr(
                        param.get_type().type_args[0], only_leaves))
        self.depth = initial_depth
        return ast.FunctionCall(func.name, args, receiver)

    def gen_field_access(self, etype, only_leaves=False, subtype=True):
        objs = self._get_matching_objects(etype, subtype, 'fields')
        if not objs:
            cls_f = self._get_matching_class(etype, subtype, 'fields')
            if cls_f is None:
                cls_f = self._gen_matching_class(
                    etype, 'fields', not_void=True)
            cls, func = cls_f
            receiver = self.generate_expr(cls.get_type(), only_leaves)
            objs.append((receiver, func))
        receiver, func = ut.random.choice(objs)
        return ast.FieldAccess(receiver, func.name)

    def _get_class(self, etype: types.Type):
        # Get class declaration based on the given type.
        class_decls = self.context.get_classes(self.namespace).values()
        for c in class_decls:
            cls_type = c.get_type()
            t_con = getattr(etype, 't_constructor', None)
            # or t == t_con: If etype is a parameterized type (i.e.,
            # getattr(etype, 't_constructor', None) != None), we need to
            # get the class corresponding to its type constructor.
            if ((cls_type.is_assignable(etype) and cls_type.name == etype.name)
                    or cls_type == t_con):
                return c
        return None

    def _get_subclass(self, etype: types.Type):
        class_decls = self.context.get_classes(self.namespace).values()
        # Get all classes that are subtype of the given type, and there
        # are regular classes (no interfaces or abstract classes).
        subclasses = []
        for c in class_decls:
            if c.class_type != ast.ClassDeclaration.REGULAR:
                continue
            if c.is_parameterized():
                t_con = getattr(etype, 't_constructor', None)
                if c.get_type() == t_con or c.get_type().is_subtype(etype):
                    subclasses.append(c)
            else:
                if c.get_type().is_subtype(etype):
                    subclasses.append(c)
        # FIXME what happens if subclasses is empty?
        # it may happens due to ParameterizedType with TypeParameters as targs
        return ut.random.choice(
            [s for s in subclasses if s.name == etype.name] or subclasses)

    # pylint: disable=unused-argument
    def gen_new(self, etype, only_leaves=False, subtype=True):
        news = {
            self.bt_factory.get_any_type(): ast.New(
                self.bt_factory.get_any_type(), args=[]),
            self.bt_factory.get_void_type(): ast.New(
                self.bt_factory.get_void_type(), args=[])
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
        # If the matching class is a parameterized one, we need to create
        # a map mapping the class's type parameters with the corresponding
        # type arguments as given by the `etype` variable.
        type_param_map = (
            {} if not class_decl.is_parameterized()
            else {t_p: etype.type_args[i]
                  for i, t_p in enumerate(class_decl.type_parameters)}
        )
        initial_depth = self.depth
        self.depth += 1
        args = []
        prev = self._new_from_class
        self._new_from_class = None
        for field in class_decl.fields:
            args.append(self.generate_expr(
                type_param_map.get(field.get_type()) or
                field.get_type(), only_leaves))
        self._new_from_class = prev
        self.depth = initial_depth
        new_type = class_decl.get_type()
        if class_decl.is_parameterized():
            new_type = new_type.new(etype.type_args)
        return ast.New(new_type, args)

    def gen_variable(self, etype, only_leaves=False, subtype=True):
        # Get all variables declared in the current namespace or
        # the outer namespace.
        variables = self.context.get_vars(self.namespace)
        # If we need to use a variable of a specific types, then filter
        # all variables that match this specific type.
        if subtype:
            fun = lambda v, t: v.get_type().is_assignable(t)
        else:
            fun = lambda v, t: v.get_type() == t
        variables = [v for v in variables.values() if fun(v, etype)]
        if not variables:
            return self.generate_expr(etype, only_leaves=only_leaves,
                                      subtype=subtype, exclude_var=True)
        varia = ut.random.choice([v.name for v in variables])
        return ast.Variable(varia)

    def _get_assignable_vars(self):
        variables = []
        for var in self.context.get_vars(self.namespace).values():
            if not getattr(var, 'is_final', True):
                variables.append((None, var))
                continue
            var_type = var.get_type()
            if tu.is_builtin(var_type, self.bt_factory):
                continue
            cls = self._get_class(var_type)
            for field in cls.fields:
                if not field.is_final:
                    variables.append((ast.Variable(var.name), field))
        return variables

    def _get_classes_with_assignable_fields(self):
        classes = []
        class_decls = self.context.get_classes(self.namespace).values()
        for c in class_decls:
            for field in c.fields:
                if not field.is_final:
                    classes.append((c, field))
        # Instead of filter out TypeConstructors we can
        # instantiate_type_constructor. To do so, we need to pass types as
        # argument to Generator's constructor.
        classes = [c for c in classes
                   if not isinstance(c[0].get_type(), types.TypeConstructor)]
        if not classes:
            return None
        return ut.random.choice(classes)

    # pylint: disable=unused-argument
    def gen_assignment(self, expr_type, only_leaves=False, subtype=True):
        # Get all all non-final variables for performing the assignment.
        variables = self._get_assignable_vars()
        initial_depth = self.depth
        self.depth += 1
        if not variables:
            # Ok, it's time to find a class with non-final fields,
            # generate an object of this class, and perform the assignment.
            res = self._get_classes_with_assignable_fields()
            if res:
                cls, field = res
                variables = [(self.generate_expr(cls.get_type(),
                                                 only_leaves, subtype), field)]
        if not variables:
            # Nothing of the above worked, so generate a 'var' variable,
            # and perform the assignment
            etype = self.gen_type()
            self._vars_in_context[self.namespace] += 1
            # If there are not variable declarations that match our criteria,
            # we have to create a new variable declaration.
            var_decl = self.gen_variable_decl(etype, only_leaves)
            var_decl.is_final = False
            var_decl.var_type = var_decl.get_type()
            self.context.add_var(self.namespace, var_decl.name, var_decl)
            self.depth = initial_depth
            return ast.Assignment(var_decl.name,
                                  self.generate_expr(var_decl.get_type(),
                                                     only_leaves, subtype))
        receiver, variable = ut.random.choice(variables)
        self.depth = initial_depth
        return ast.Assignment(variable.name, self.generate_expr(
            variable.get_type(), only_leaves, subtype), receiver=receiver)

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
            "main",
            params=[],
            ret_type=self.bt_factory.get_void_type(),
            body=body,
            func_type=ast.FunctionDeclaration.FUNCTION)
        self.namespace = initial_namespace
        return main_func

    def get_generators(self, expr_type, only_leaves, subtype,
                       exclude_var):
        def gen_variable(etype):
            return self.gen_variable(etype, only_leaves, subtype)

        def gen_fun_call(etype):
            return self.gen_func_call(etype, only_leaves=only_leaves,
                                      subtype=subtype)

        leaf_canidates = [
            lambda x: self.gen_new(x, only_leaves, subtype),
        ]
        constant_candidates = {
            self.bt_factory.get_number_type().name: gu.gen_integer_constant,
            self.bt_factory.get_integer_type().name: gu.gen_integer_constant,
            self.bt_factory.get_big_integer_type().name: gu.gen_integer_constant,
            self.bt_factory.get_byte_type().name: gu.gen_integer_constant,
            self.bt_factory.get_short_type().name: gu.gen_integer_constant,
            self.bt_factory.get_long_type().name: gu.gen_integer_constant,
            self.bt_factory.get_float_type().name: gu.gen_real_constant,
            self.bt_factory.get_double_type().name: gu.gen_real_constant,
            self.bt_factory.get_big_decimal_type().name: gu.gen_real_constant,
            self.bt_factory.get_char_type().name: gu.gen_char_constant,
            self.bt_factory.get_string_type().name: gu.gen_string_constant,
            self.bt_factory.get_boolean_type().name: gu.gen_bool_constant,
            self.bt_factory.get_array_type().name: (
                lambda x: self.gen_array_expr(x, only_leaves, subtype=subtype)
            ),
        }
        binary_ops = {
            self.bt_factory.get_boolean_type(): [
                lambda x: self.gen_logical_expr(x, only_leaves),
                lambda x: self.gen_equality_expr(only_leaves),
                lambda x: self.gen_comparison_expr(only_leaves)
            ],
        }
        other_candidates = [
            lambda x: self.gen_field_access(x, only_leaves, subtype),
            lambda x: self.gen_conditional(x, only_leaves=only_leaves,
                                           subtype=subtype),
            gen_fun_call,
            gen_variable
        ]

        if expr_type == self.bt_factory.get_void_type():
            return [gen_fun_call,
                    lambda x: self.gen_assignment(x, only_leaves)]

        if self.depth >= self.max_depth or only_leaves:
            gen_con = constant_candidates.get(expr_type.name)
            if gen_con is not None:
                return [gen_con]
            gen_var = (
                self._vars_in_context.get(
                    self.namespace, 0) < self.max_var_decls and not
                only_leaves and not exclude_var)
            if gen_var:
                # Decide if we can generate a variable.
                # If the maximum numbers of variables in a specific context
                # has been reached, or we have previously declared a variable
                # of a specific type, then we should avoid variable creation.
                leaf_canidates.append(gen_variable)
            return leaf_canidates
        con_candidate = constant_candidates.get(expr_type.name)
        if con_candidate is not None:
            candidates = [con_candidate] + binary_ops.get(expr_type, [])
            if not exclude_var:
                candidates.append(gen_variable)
        else:
            candidates = leaf_canidates
        return other_candidates + candidates

    def generate_expr(self, expr_type=None, only_leaves=False, subtype=True,
                      exclude_var=False):
        expr_type = expr_type or self.gen_type()
        gens = self.get_generators(expr_type, only_leaves, subtype,
                                   exclude_var)
        expr = ut.random.choice(gens)(expr_type)
        # Make a probablistic choice, and assign the generated expr
        # into a variable, and return that variable reference.
        gen_var = (
            not only_leaves and
            expr_type != self.bt_factory.get_void_type() and
            self._vars_in_context[self.namespace] < self.max_var_decls and
            ut.random.bool()
        )
        if gen_var:
            self._vars_in_context[self.namespace] += 1
            var_decl = self.gen_variable_decl(expr_type, only_leaves,
                                              expr=expr)
            self.context.add_var(self.namespace, var_decl.name, var_decl)
            expr = ast.Variable(var_decl.name)
        return expr

    def gen_top_level_declaration(self):
        candidates = [
            (self.gen_variable_decl, self.context.add_var),
            (self.gen_class_decl, self.context.add_class),
            (self.gen_func_decl, self.context.add_func)
        ]
        gen_func, upd_context = ut.random.choice(candidates)
        decl = gen_func()
        upd_context(self.namespace, decl.name, decl)

    def generate(self):
        for _ in range(0, ut.random.integer(0, 10)):
            self.gen_top_level_declaration()
        main_func = self.generate_main_func()
        self.namespace = ('global',)
        self.context.add_func(self.namespace, 'main', main_func)
        return ast.Program(self.context, self.language)
