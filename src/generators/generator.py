# pylint: disable=too-many-instance-attributes,too-many-arguments,dangerous-default-value
import functools
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
from typing import Tuple, List

from src import utils as ut
from src.generators import utils as gu
from src.ir import ast, types as tp, type_utils as tu, kotlin_types as kt
from src.ir.context import Context
from src.ir.builtins import BuiltinFactory
from src.ir import BUILTIN_FACTORIES


def select_class_type(contain_fields):
    # there's higher probability to generate a regular class.
    if ut.random.bool():
        return ast.ClassDeclaration.REGULAR

    candidates = [ast.ClassDeclaration.ABSTRACT]
    if not contain_fields:
        candidates.append(ast.ClassDeclaration.INTERFACE)
    return ut.random.choice(candidates)


def init_variance_choices(type_var_map):
    variance_choices = {}
    for type_var in type_var_map.keys():
        variance_choices[type_var] = (False, False)
        # If disable variance on specific type parameters, then we have to
        # do the same on its bound (if it is another type variable).
        while type_var.bound and type_var.bound.is_type_var():
            type_var = type_var.bound
            variance_choices[type_var] = (False, False)
    return variance_choices


@dataclass
class SuperClassInfo:
    super_cls: ast.ClassDeclaration
    type_var_map: dict
    super_inst: ast.SuperClassInstantiation


class Generator():

    def __init__(self, max_depth=7, max_fields=2, max_funcs=2, max_params=2,
                 max_var_decls=3, max_side_effects=1, max_type_params=3,
                 max_functional_params=3,
                 language=None,
                 options={},
                 logger=None,
                 context=None):
        assert language is not None, "You must specify the language"
        self.language = language
        self.logger = logger
        self.context = context or Context()
        self.bt_factory: BuiltinFactory = BUILTIN_FACTORIES[language]
        self.max_depth = max_depth
        self.max_fields = max_fields
        self.max_funcs = max_funcs
        self.max_params = max_params
        self.max_type_params = max_type_params
        self.max_var_decls = max_var_decls
        self.max_side_effects = max_side_effects
        self.max_functional_params = max_functional_params
        self.disable_inference_in_closures = options.get(
            "disable_inference_in_closures", False)
        self.depth = 1
        self._vars_in_context = defaultdict(lambda: 0)
        self._new_from_class = None
        self.namespace = ('global',)

        # This flag is used for Java lambdas where local variables references
        # must be final.
        self._inside_java_lambda = False

        self.function_type = type(self.bt_factory.get_function_type())
        self.function_types = self.bt_factory.get_function_types(
            max_functional_params)

        self.ret_builtin_types = self.bt_factory.get_non_nothing_types()
        self.builtin_types = self.ret_builtin_types + \
            [self.bt_factory.get_void_type()]

    def get_types(self, ret_types=True, exclude_arrays=False,
                  exclude_covariants=False,
                  exclude_contravariants=False,
                  exclude_type_vars=False,
                  exclude_function_types=False):
        usr_types = [
            c.get_type()
            for c in self.context.get_classes(self.namespace).values()
        ]
        type_params = []
        if not exclude_type_vars:
            for t_param in self.context.get_types(self.namespace).values():
                variance = getattr(t_param, 'variance', None)
                if exclude_covariants and variance == tp.Covariant:
                    continue
                if exclude_contravariants and variance == tp.Contravariant:
                    continue
                type_params.append(t_param)

        if type_params and ut.random.bool():
            return type_params

        builtins = list(self.ret_builtin_types
                        if ret_types
                        else self.builtin_types)
        if exclude_arrays:
            builtins = [
                t for t in builtins
                if t.name != self.bt_factory.get_array_type().name
            ]
        if exclude_function_types:
            return usr_types + builtins
        return usr_types + builtins + self.function_types

    def select_type(self, ret_types=True, exclude_arrays=False,
                    exclude_covariants=False, exclude_contravariants=False,
                    exclude_function_types=False):
        types = self.get_types(ret_types=ret_types,
                               exclude_arrays=exclude_arrays,
                               exclude_covariants=exclude_covariants,
                               exclude_contravariants=exclude_contravariants,
                               exclude_function_types=exclude_function_types)
        t = ut.random.choice(types)
        if t.is_type_constructor():
            exclude_type_vars = t.name == self.bt_factory.get_array_type().name
            t, _ = tu.instantiate_type_constructor(
                t, self.get_types(exclude_arrays=True,
                                  exclude_covariants=True,
                                  exclude_contravariants=True,
                                  exclude_type_vars=exclude_type_vars,
                                  exclude_function_types=exclude_function_types),
                variance_choices={}
            )
        return t

    # pylint: disable=unused-argument
    def gen_equality_expr(self, expr_type=None, only_leaves=False):
        initial_depth = self.depth
        self.depth += 1
        exclude_function_types = self.language == 'java'
        etype = self.select_type(exclude_function_types=exclude_function_types)
        op = ut.random.choice(ast.EqualityExpr.VALID_OPERATORS[self.language])
        e1 = self.generate_expr(etype, only_leaves, subtype=False)
        e2 = self.generate_expr(etype, only_leaves, subtype=False)
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
        if self.language == 'java' and e1_type.name in ('Boolean', 'String'):
            op = ut.random.choice(
                ast.EqualityExpr.VALID_OPERATORS[self.language])
            return ast.EqualityExpr(e1, e2, op)
        return ast.ComparisonExpr(e1, e2, op)

    def gen_field_decl(self, etype=None, class_is_final=True):
        name = gu.gen_identifier('lower')
        can_override = not class_is_final and ut.random.bool()
        is_final = ut.random.bool()
        field_type = etype or self.select_type(exclude_contravariants=True,
                                               exclude_covariants=not is_final)
        return ast.FieldDeclaration(name, field_type, is_final=is_final,
                                    can_override=can_override)

    def gen_param_decl(self, etype=None):
        name = gu.gen_identifier('lower')
        param_type = etype or self.select_type(exclude_covariants=True)
        return ast.ParameterDeclaration(name, param_type)

    def _get_func_ret_type(self, params, etype, not_void=False):
        if etype is not None:
            return etype
        param_types = [p.param_type for p in params
                       if getattr(p.param_type,
                                  'variance', None) != tp.Contravariant]
        if param_types and ut.random.bool():
            return ut.random.choice(param_types)
        return self.select_type(exclude_contravariants=True)

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
        decls = self.context.get_declarations(self.namespace, True).values()
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

    def _gen_func_params_with_default(self):
        has_default = False
        params = []
        for i in range(ut.random.integer(0, self.max_params)):
            param = self.gen_param_decl()
            if not has_default:
                has_default = ut.random.bool()
            if has_default:
                prev = self.namespace
                self.namespace = self.namespace[:-1]
                expr = self.generate_expr(param.get_type(), only_leaves=True)
                self.namespace = prev
                param.default = expr
                params.append(param)
        return params

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

    def _gen_func_body(self, ret_type):
        expr_type = (
            self.select_type(ret_types=False)
            if ret_type == self.bt_factory.get_void_type()
            else ret_type
        )
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
            # If the return value is the bottom constant, then again the
            # return type must be explicit.
            if ret_type != self.bt_factory.get_number_type() and not (
                  expr.is_bottom()):
                ret_type = None
        else:
            inferred_type = None
            exprs, decls = self._gen_side_effects()
            body = ast.Block(decls + exprs + [expr])
        return body, inferred_type

    def gen_func_decl(self, etype=None, not_void=False,
                      class_is_final=False, func_name=None, params=None,
                      abstract=False, is_interface=False,
                      namespace=None):
        func_name = func_name or gu.gen_identifier('lower')
        initial_namespace = self.namespace
        if namespace:
            self.namespace = namespace + (func_name,)
        else:
            self.namespace += (func_name,)
        initial_depth = self.depth
        self.depth += 1
        # Check if this function we want to generate is a class method, by
        # checking the name of the outer namespace. If we are in class then
        # the outer namespace begins with capital letter.
        class_method = self.namespace[-1][0].isupper()
        can_override = abstract or is_interface or (class_method and not
                                    class_is_final and ut.random.bool())
        # Check if this function we want to generate is a nested functions.
        # To do so, we want to find if the function is directly inside the
        # namespace of another function.
        nested_function = (len(self.namespace) > 1 and
                           self.namespace[-2] != 'global' and
                           self.namespace[-2][0].islower())

        prev_inside_java_lamdba = self._inside_java_lambda
        self._inside_java_lambda = nested_function and self.language == "java"
        params = params if params is not None else (
            self._gen_func_params()
            if (
                ut.random.bool(prob=0.25) or
                self.language == 'java' or
                self.language == 'groovy' and is_interface
            )
            else self._gen_func_params_with_default())
        ret_type = self._get_func_ret_type(params, etype, not_void=not_void)
        if is_interface or (abstract and ut.random.bool()):
            body, inferred_type = None, None
        else:
            body, inferred_type = self._gen_func_body(ret_type)
        self._inside_java_lambda = prev_inside_java_lamdba
        self.depth = initial_depth
        self.namespace = initial_namespace
        return ast.FunctionDeclaration(
            func_name, params, ret_type, body,
            func_type=(ast.FunctionDeclaration.CLASS_METHOD
                       if class_method
                       else ast.FunctionDeclaration.FUNCTION),
            is_final=not can_override,
            inferred_type=inferred_type)

    def _add_field_to_class(self, field, fields):
        fields.append(field)
        self.context.add_var(self.namespace, field.name, field)

    def _add_func_to_class(self, func, funcs):
        funcs.append(func)
        self.context.add_func(self.namespace, func.name, func)

    def gen_type_params(self, count=None):
        if not count and ut.random.bool():
            return []
        type_params = []
        type_param_names = []
        variances = [tp.Invariant, tp.Covariant, tp.Contravariant]
        for _ in range(ut.random.integer(count or 1, self.max_type_params)):
            name = ut.random.caps(blacklist=type_param_names)
            type_param_names.append(name)
            variance = None
            if self.language == 'kotlin' and ut.random.bool():
                variance = ut.random.choice(variances)
            bound = None
            if ut.random.bool():
                exclude_covariants = variance == tp.Contravariant
                exclude_contravariants = True
                bound = self.select_type(
                    exclude_arrays=True,
                    exclude_covariants=exclude_covariants,
                    exclude_contravariants=exclude_contravariants
                )
                if bound.is_primitive():
                    bound = bound.box_type()
            type_param = tp.TypeParameter(name, variance=variance, bound=bound)
            # Add type parameter to context.
            self.context.add_type(self.namespace, type_param.name, type_param)
            type_params.append(type_param)
        return type_params

    def _select_superclass(self, only_interfaces):
        class_decls = [
            c for c in self.context.get_classes(self.namespace).values()
            if not c.is_final and (c.is_interface() if only_interfaces else True)
        ]
        if not class_decls:
            return None
        class_decl = ut.random.choice(class_decls)
        if class_decl.is_parameterized():
            cls_type, type_var_map = tu.instantiate_type_constructor(
                class_decl.get_type(),
                self.get_types(exclude_covariants=True,
                               exclude_contravariants=True),
                only_regular=True,
            )
        else:
            cls_type, type_var_map = class_decl.get_type(), {}
        con_args = None if class_decl.is_interface() else []
        for f in class_decl.fields:
            field_type = tp.substitute_type(f.get_type(), type_var_map)
            con_args.append(self.generate_expr(field_type,
                                               only_leaves=True))
        return SuperClassInfo(
            class_decl,
            type_var_map,
            ast.SuperClassInstantiation(cls_type, con_args)
        )

    def gen_class_fields(self, curr_cls, super_cls_info,
                         field_type=None):
        max_fields = self.max_fields - 1 if field_type else self.max_fields
        fields = []
        if field_type:
            self._add_field_to_class(
                self.gen_field_decl(field_type, curr_cls.is_final), fields)
        if not super_cls_info:
            for _ in range(ut.random.integer(0, max_fields)):
                self._add_field_to_class(
                    self.gen_field_decl(class_is_final=curr_cls.is_final),
                    fields)
        else:
            overridable_fields = super_cls_info.super_cls \
                .get_overridable_fields()
            k = ut.random.integer(0, min(max_fields, len(overridable_fields)))
            if overridable_fields:
                chosen_fields = ut.random.sample(overridable_fields, k=k)
                for f in chosen_fields:

                    field_type = tp.substitute_type(
                        f.get_type(), super_cls_info.type_var_map)
                    new_f = self.gen_field_decl(field_type, curr_cls.is_final)
                    new_f.name = f.name
                    new_f.override = True
                    new_f.is_final = f.is_final
                    self._add_field_to_class(new_f, fields)
                max_fields = max_fields - len(chosen_fields)
            if max_fields < 0:
                return fields
            for _ in range(ut.random.integer(0, max_fields)):
                self._add_field_to_class(
                    self.gen_field_decl(class_is_final=curr_cls.is_final),
                    fields)
        return fields

    def _gen_func_from_existing(self, func, type_var_map, class_is_final,
                                is_interface):
        params = []
        for p in func.params:
            new_p = deepcopy(p)
            new_p.param_type = tp.substitute_type(p.get_type(), type_var_map)
            new_p.default = None
            params.append(new_p)
        ret_type = tp.substitute_type(func.get_type(), type_var_map)
        new_func = self.gen_func_decl(func_name=func.name, etype=ret_type,
                                      not_void=False,
                                      class_is_final=class_is_final,
                                      params=params,
                                      is_interface=is_interface)
        if func.body is None:
            new_func.is_final = False
        new_func.override = True
        return new_func

    def gen_class_functions(self, curr_cls, super_cls_info,
                            not_void=False, fret_type=None):
        funcs = []
        max_funcs = self.max_funcs - 1 if fret_type else self.max_funcs
        abstract = not curr_cls.is_regular()
        if fret_type:
            self._add_func_to_class(
                self.gen_func_decl(fret_type, not_void=not_void,
                                   class_is_final=curr_cls.is_final,
                                   abstract=abstract,
                                   is_interface=curr_cls.is_interface()),
                funcs)
        if not super_cls_info:
            for _ in range(ut.random.integer(0, max_funcs)):
                self._add_func_to_class(
                    self.gen_func_decl(not_void=not_void,
                                       class_is_final=curr_cls.is_final,
                                       abstract=abstract,
                                       is_interface=curr_cls.is_interface()),
                    funcs)
        else:
            abstract_funcs = []
            class_decls = self.context.get_classes(self.namespace).values()
            if curr_cls.is_regular():
                abstract_funcs = super_cls_info.super_cls\
                    .get_abstract_functions(class_decls)
                for f in abstract_funcs:
                    self._add_func_to_class(
                        self._gen_func_from_existing(
                            f,
                            super_cls_info.type_var_map,
                            curr_cls.is_final,
                            curr_cls.is_interface()
                        ),
                        funcs
                    )
                max_funcs = max_funcs - len(abstract_funcs)
            overridable_funcs = super_cls_info.super_cls \
                .get_overridable_functions()
            abstract_funcs = {f.name for f in abstract_funcs}
            overridable_funcs = [f for f in overridable_funcs
                                 if f.name not in abstract_funcs]
            len_over_f = len(overridable_funcs)
            if len_over_f > max_funcs:
                return funcs
            k = ut.random.integer(0, min(max_funcs, len_over_f))
            chosen_funcs = (
                []
                if not max_funcs or curr_cls.is_interface()
                else ut.random.sample(overridable_funcs, k=k)
            )
            for f in chosen_funcs:
                self._add_func_to_class(
                    self._gen_func_from_existing(f,
                                                 super_cls_info.type_var_map,
                                                 curr_cls.is_final,
                                                 curr_cls.is_interface()),
                    funcs)
            max_funcs = max_funcs - len(chosen_funcs)
            if max_funcs < 0:
                return funcs
            for _ in range(ut.random.integer(0, max_funcs)):
                self._add_func_to_class(
                    self.gen_func_decl(not_void=not_void,
                                       class_is_final=curr_cls.is_final,
                                       abstract=abstract,
                                       is_interface=curr_cls.is_interface()),
                    funcs)
        return funcs

    def gen_class_decl(self, field_type=None, fret_type=None, not_void=False,
                       type_params=None, class_name=None):
        class_name = class_name or gu.gen_identifier('capitalize')
        initial_namespace = self.namespace
        self.namespace += (class_name,)
        initial_depth = self.depth
        self.depth += 1
        class_type = select_class_type(field_type is not None)
        is_final = ut.random.bool() and class_type == \
            ast.ClassDeclaration.REGULAR
        type_params = type_params or self.gen_type_params()
        super_cls_info = self._select_superclass(
            class_type == ast.ClassDeclaration.INTERFACE)
        cls = ast.ClassDeclaration(
            class_name,
            class_type=class_type,
            superclasses=[super_cls_info.super_inst] if super_cls_info else [],
            type_parameters=type_params,
            is_final=is_final
        )
        fields = (
            self.gen_class_fields(cls, super_cls_info, field_type)
            if not cls.is_interface()
            else []
        )
        funcs = self.gen_class_functions(cls, super_cls_info,
                                         not_void, fret_type)
        self.namespace = initial_namespace
        self.depth = initial_depth
        cls.fields = fields
        cls.functions = funcs
        return cls

    def gen_array_expr(self, expr_type, only_leaves=False, subtype=True):
        arr_len = ut.random.integer(0, 3)
        etype = expr_type.type_args[0]
        exprs = [
            self.generate_expr(etype, only_leaves=only_leaves, subtype=subtype)
            for _ in range(arr_len)
        ]
        return ast.ArrayExpr(expr_type, arr_len, exprs)

    def gen_variable_decl(self, etype=None, only_leaves=False,
                          expr=None):
        var_type = etype if etype else self.select_type()
        initial_depth = self.depth
        self.depth += 1
        expr = expr or self.generate_expr(var_type, only_leaves)
        self.depth = initial_depth
        is_final = ut.random.bool()
        # We never omit type in non-final variables or in variables that
        # correspond to a bottom constant.
        omit_type = (
            ut.random.bool() and
            is_final and
            var_type != self.bt_factory.get_number_type()
        )
        vtype = None if omit_type and not expr.is_bottom() else var_type
        if vtype is not None and vtype.is_wildcard():
            vtype = vtype.get_bound_rec()
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

    def _get_var_type_to_search(self, var_type):
        # We are only interested in variables of class types.
        if tu.is_builtin(var_type, self.bt_factory):
            return None
        if var_type.is_type_var() or var_type.is_wildcard():
            args = [] if var_type.is_wildcard() else [self.bt_factory]
            bound = var_type.get_bound_rec(*args)
            if not bound or tu.is_builtin(bound, self.bt_factory) or (
                  isinstance(bound, tp.TypeParameter)):
                return None
            var_type = bound
        return var_type

    def _get_matching_objects(self, etype, subtype, attr_name) -> \
            List[Tuple[ast.Expr, ast.Declaration]]:
        decls = []
        variables = self.context.get_vars(self.namespace).values()
        if self._inside_java_lambda:
            variables = list(filter(
                lambda v: (getattr(v, 'is_final', False) or (
                    v not in self.context.get_vars(self.namespace[:-1]).values())),
                variables))
        for var in variables:
            var_type = self._get_var_type_to_search(var.get_type())
            if not var_type:
                continue
            if isinstance(getattr(var_type, 't_constructor', None),
                          self.function_type):
                continue
            cls, type_map_var = self._get_class(var_type)
            for attr in getattr(cls, attr_name):  # function or field
                attr_type = tp.substitute_type(
                    attr.get_type(), type_map_var)
                if not attr_type:
                    continue
                if attr_type == self.bt_factory.get_void_type():
                    continue
                cond = (
                    attr_type.is_assignable(etype)
                    if subtype
                    else attr_type == etype
                )
                if not cond:
                    continue
                decls.append((ast.Variable(var.name), type_map_var, attr))
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
                if subtype else func.get_type() == etype
            )
            # The receiver object for this kind of functions is None.
            if not cond:
                continue
            # FIXME: Consider creating a utility class that contains
            # class_type + instantiation_map
            functions.append((None, {}, func))
        return functions + self._get_matching_objects(etype, subtype,
                                                      'functions')

    def _get_matching_class_decls(self, etype, subtype, attr_name):
        class_decls = []
        for c in self.context.get_classes(self.namespace).values():
            for attr in getattr(c, attr_name):  # field or function
                attr_type = attr.get_type()
                if not attr_type:
                    continue
                if attr_type == self.bt_factory.get_void_type():
                    continue
                cond = (
                    attr_type.is_assignable(etype)
                    if subtype else
                    attr_type == etype
                )
                type_var_map = None
                # if the type of the attribute has type variables,
                # then we have to unify it with the expected type so that
                # we can instantiate the corresponding type constructor
                # accordingly
                if not cond or attr_type.has_type_variables():
                    type_var_map = tu.unify_types(etype, attr_type,
                                                  self.bt_factory)
                if not type_var_map and not cond:
                    continue
                # Now here we keep the class and the function that match
                # the given type.
                class_decls.append((c, type_var_map, attr))
        return class_decls


    def _get_matching_class(self, etype, subtype, attr_name) -> \
            Tuple[ast.ClassDeclaration, ast.Declaration]:
        class_decls = self._get_matching_class_decls(etype, subtype, attr_name)
        if not class_decls:
            return None
        cls, type_var_map, attr = ut.random.choice(class_decls)
        if cls.is_parameterized():
            variance_choices = (
                None
                if type_var_map is None
                else init_variance_choices(type_var_map)
            )
            cls_type, params_map = tu.instantiate_type_constructor(
                cls.get_type(), self.get_types(),
                only_regular=True, type_var_map=type_var_map,
                variance_choices=variance_choices
            )
        else:
            cls_type, params_map = cls.get_type(), {}
        return cls_type, params_map, attr

    def _get_matching_classes(self, etype, subtype, attr_name):
        res = []
        class_decls = self._get_matching_class_decls(etype, subtype, attr_name)
        if not class_decls:
            return []
        for cls, type_var_map, attr in class_decls:
            if cls.is_parameterized():
                variance_choices = (
                    None
                    if type_var_map is None
                    else init_variance_choices(type_var_map)
                )
                cls_type, params_map = tu.instantiate_type_constructor(
                    cls.get_type(), self.get_types(),
                    only_regular=True, type_var_map=type_var_map,
                    variance_choices=variance_choices
                )
            else:
                cls_type, params_map = cls.get_type(), {}
            res.append((cls_type, params_map, attr))
        return res

    def _create_type_params_from_etype(self, etype):
        if not etype.has_type_variables():
            return []

        if isinstance(etype, tp.TypeParameter):
            type_params = self.gen_type_params(count=1)
            type_params[0].bound = etype.get_bound_rec(self.bt_factory)
            type_params[0].variance = tp.Invariant
            return type_params, {etype: type_params[0]}, True

        # the given type is parameterized
        assert isinstance(etype, tp.ParameterizedType)
        type_vars = etype.get_type_variables(self.bt_factory)
        type_params = self.gen_type_params(len(type_vars))
        type_var_map = {}
        available_type_params = list(type_params)
        can_wildcard = True
        for type_var, bounds in type_vars.items():
            # The given type 'etype' has type variables.
            # So, it's not safe to instantiate these type variables with
            # wildcard types. In this way we prevent errors like the following.
            #
            # class A<T> {
            #   B<T> foo();
            # }
            # A<? extends Number> x = new A<>();
            # B<Number> = x.foo(); // error: incompatible types
            # TODO: We may support this case in the future.
            can_wildcard = False
            bounds = list(bounds)
            type_param = ut.random.choice(available_type_params)
            available_type_params.remove(type_param)
            if bounds != [None]:
                type_param.bound = functools.reduce(
                    lambda acc, t: t if t.is_subtype(acc) else acc,
                    filter(lambda t: t is not None, bounds), bounds[0])
            else:
                type_param.bound = None
            type_param.variance = tp.Invariant
            type_var_map[type_var] = type_param
        return type_params, type_var_map, can_wildcard

    def _gen_matching_class(self, etype, attr_name, not_void=False) -> \
            Tuple[ast.ClassDeclaration, ast.Declaration]:
        initial_namespace = self.namespace
        class_name = gu.gen_identifier('capitalize')
        type_params = None
        if etype.has_type_variables():
            # We have to create a class that has an attribute whose type
            # is a type parameter. The only way to achieve this is to create
            # a parameterized class, and pass the type parameter 'etype'
            # as a type argument to the corresponding type constructor.
            self.namespace = ast.GLOBAL_NAMESPACE + (class_name,)
            type_params, type_var_map, can_wildcard = \
                self._create_type_params_from_etype(etype)
            etype2 = tp.substitute_type(etype, type_var_map)
        else:
            type_var_map, etype2, can_wildcard = {}, etype, False
        self.namespace = ast.GLOBAL_NAMESPACE
        if attr_name == 'functions':
            kwargs = {'fret_type': etype2}
        else:
            kwargs = {'field_type': etype2}
        cls = self.gen_class_decl(**kwargs, not_void=not_void,
                                  type_params=type_params,
                                  class_name=class_name)
        self.context.add_class(self.namespace, cls.name, cls)
        self.namespace = initial_namespace
        if cls.is_parameterized():
            type_map = {v: k for k, v in type_var_map.items()}
            if etype2.is_primitive() and (
                    etype2.box_type() == self.bt_factory.get_void_type()):
                type_map = None

            if can_wildcard:
                variance_choices = init_variance_choices(type_map)
            else:
                variance_choices = None
            cls_type, params_map = tu.instantiate_type_constructor(
                cls.get_type(),
                self.get_types(),
                type_var_map=type_map,
                variance_choices=variance_choices
            )
        else:
            cls_type, params_map = cls.get_type(), {}
        for attr in getattr(cls, attr_name):
            attr_type = tp.substitute_type(attr.get_type(), params_map)
            if attr_type != etype:
                continue

            return cls_type, params_map, attr
        return None

    def _gen_matching_func(self, etype, not_void=False) -> \
            Tuple[ast.ClassDeclaration, ast.Declaration]:
        # Randomly choose to generate a function or a class method.
        if ut.random.bool():
            initial_namespace = self.namespace
            # If the given type 'etype' is a type parameter, then the
            # function we want to generate should be in the current namespace,
            # so that the type parameter is accessible.
            self.namespace = (
                self.namespace
                if ut.random.bool() or etype.has_type_variables()
                else ast.GLOBAL_NAMESPACE
            )
            # Generate a function
            func = self.gen_func_decl(etype, not_void=not_void)
            self.context.add_func(self.namespace, func.name, func)
            self.namespace = initial_namespace
            return None, {}, func
        # Generate a class containing the requested function
        return self._gen_matching_class(etype, 'functions')

    def _gen_func_call(self, etype, only_leaves=False, subtype=True):
        funcs = self._get_function_declarations(etype, subtype)
        cls_type = None
        if not funcs:
            type_fun = self._get_matching_class(etype, subtype, 'functions')
            if type_fun is None:
                # Here, we generate a function or a class containing a function
                # whose return type is 'etype'.
                type_fun = self._gen_matching_func(etype, not_void=True)
            cls_type, params_map, func = type_fun
            receiver = None if cls_type is None else self.generate_expr(
                cls_type, only_leaves)
            funcs.append((receiver, params_map, func))
        receiver, params_map, func = ut.random.choice(funcs)
        args = []
        initial_depth = self.depth
        self.depth += 1
        for param in func.params:
            expr_type = tp.substitute_type(param.get_type(), params_map)
            gen_bottom = expr_type.is_wildcard() or (
                expr_type.is_parameterized() and expr_type.has_wildcards())
            if not param.vararg:
                arg = self.generate_expr(expr_type, only_leaves,
                                         gen_bottom=gen_bottom)
                if param.default:
                    if self.language == 'kotlin' and ut.random.bool():
                        # Randomly skip some default arguments.
                        args.append(ast.CallArgument(arg, name=param.name))
                else:
                    args.append(ast.CallArgument(arg))

            else:
                # This param is a vararg, so provide a random number of
                # arguments.
                for _ in range(ut.random.integer(0, 3)):
                    args.append(ast.CallArgument(
                        self.generate_expr(
                            expr_type.type_args[0],
                            only_leaves,
                            gen_bottom=gen_bottom)))
        self.depth = initial_depth
        return ast.FunctionCall(func.name, args, receiver)

    def _gen_func_call_ref(self, etype, only_leaves=False, subtype=False):
        # Tuple of signature and name
        refs = []
        variables = self.context.get_vars(self.namespace).values()
        if self._inside_java_lambda:
            variables = list(filter(
                lambda v: (getattr(v, 'is_final', False) or (
                    v not in self.context.get_vars(self.namespace[:-1]).values())),
                variables))
        for var in variables:
            # TODO we should also get func refs with receiver.
            var_type = var.get_type()
            if not getattr(var_type, 'is_function_type', lambda: False)():
                continue
            ret_type = var_type.type_args[-1]
            # NOTE not very frequent (~4%), we could generate a function or
            # an appropriate lambda and use it directly.
            if (subtype and ret_type.is_subtype(etype)) or ret_type == etype:
                refs.append((var_type, var.name))
        if not refs:
            return None
        signature, name = ut.random.choice(refs)

        # Generate arguments
        args = []
        initial_depth = self.depth
        self.depth += 1
        for param_type in signature.type_args[:-1]:
            gen_bottom = param_type.is_wildcard() or (
                param_type.is_parameterized() and param_type.has_wildcards())
            arg = self.generate_expr(param_type, only_leaves,
                                     gen_bottom=gen_bottom)
            args.append(ast.CallArgument(arg))
        self.depth = initial_depth

        return ast.FunctionCall(name, args, receiver=None, is_ref_call=True)

    def gen_func_call(self, etype, only_leaves=False, subtype=True):
        if ut.random.bool():
            ref_call = self._gen_func_call_ref(etype, only_leaves, subtype)
            if ref_call:
                return ref_call
        return self._gen_func_call(etype, only_leaves, subtype)

    def gen_field_access(self, etype, only_leaves=False, subtype=True):
        initial_depth = self.depth
        self.depth += 1
        objs = self._get_matching_objects(etype, subtype, 'fields')
        params_map = {} # Remove
        if not objs:
            type_f = self._get_matching_class(etype, subtype, 'fields')
            if type_f is None:
                type_f = self._gen_matching_class(
                    etype, 'fields', not_void=True,
                )
            type_f, params_map, func = type_f
            receiver = self.generate_expr(type_f, only_leaves)
            objs.append((receiver, None, func))
        objs = [(r, f) for r, _, f in objs]
        receiver, func = ut.random.choice(objs)
        self.depth = initial_depth
        return ast.FieldAccess(receiver, func.name)

    def _get_class(self, etype: tp.Type):
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
                if c.is_parameterized():
                    type_var_map = {
                        t_param: etype.type_args[i]
                        for i, t_param in enumerate(c.type_parameters)
                    }
                else:
                    type_var_map = {}
                return c, type_var_map
        return None

    def _get_subclass(self, etype: tp.Type, subtype=True):
        class_decls = self.context.get_classes(self.namespace).values()
        # Get all classes that are subtype of the given type, and there
        # are regular classes (no interfaces or abstract classes).
        subclasses = []
        for c in class_decls:
            if c.class_type != ast.ClassDeclaration.REGULAR:
                continue
            if c.is_parameterized():
                t_con = getattr(etype, 't_constructor', None)
                if c.get_type() == t_con or (
                        subtype and c.get_type().is_subtype(etype)):
                    subclasses.append(c)
            else:
                if c.get_type() == etype or (
                        subtype and c.get_type().is_subtype(etype)):
                    subclasses.append(c)
        if not subclasses:
            return None
        # FIXME what happens if subclasses is empty?
        # it may happens due to ParameterizedType with TypeParameters as targs
        return ut.random.choice(
            [s for s in subclasses if s.name == etype.name] or subclasses)

    def gen_lambda(self, etype=None, not_void=False,
                   shadow_name=None, params=None):

        shadow_name = shadow_name or gu.gen_identifier('lower')
        initial_namespace = self.namespace
        self.namespace += (shadow_name,)
        initial_depth = self.depth
        self.depth += 1

        prev_inside_java_lamdba = self._inside_java_lambda
        self._inside_java_lambda = self.language == "java"

        params = params if params is not None else self._gen_func_params()
        ret_type = self._get_func_ret_type(params, etype, not_void=not_void)
        body, _ = self._gen_func_body(ret_type)
        param_types = [p.param_type for p in params]
        signature = tp.ParameterizedType(
            self.bt_factory.get_function_type(len(params)),
            param_types + [ret_type])

        res = ast.Lambda(shadow_name, params, ret_type, body, signature)

        self.depth = initial_depth
        self.namespace = initial_namespace
        self._inside_java_lambda = prev_inside_java_lamdba

        self.context.add_lambda(self.namespace, shadow_name, res)

        return res

    def get_func_refs(self, etype):
        refs = []
        # Find all global functions
        for func in self.context.get_funcs(self.namespace, glob=True).values():
            signature = func.get_signature(
                self.bt_factory.get_function_type(len(func.params))
            )
            # TODO handle functions of parameterized classes
            if signature == etype:
                if func.func_type == func.FUNCTION:
                    refs.append(ast.FunctionReference(func.name, None))
                else:
                    receiver = self.generate_expr(etype, subtype=False)
                    refs.append(ast.FunctionReference(func.name, receiver))

        variables = list(self.context.get_vars(self.namespace).values())
        if self._inside_java_lambda:
            variables = list(filter(
                lambda v: (getattr(v, 'is_final', False) or (
                    v not in self.context.get_vars(self.namespace[:-1]).values())),
                variables))
        variables += list(self.context.get_vars(
            ('global',), only_current=True).values())
        for var in variables:
            if var.get_type() == etype:
                refs.append(ast.FunctionReference(var.name, None))
            # TODO check for receivers
        return refs

    def gen_func_ref(self, etype):
        # NOTE to handle the case where a type argument is a type parameter,
        # we can either create a parameterized function or create a method
        # to the current class.
        # In the former, we can use `this` or we can create a new object as
        # a receiver.
        if any(isinstance(targ, tp.TypeParameter) for targ in etype.type_args):
            return None
        params = [self.gen_param_decl(t) for t in etype.type_args[:-1]]
        ret_type = etype.type_args[-1]
        func_decl = self.gen_func_decl(
            etype=ret_type, params=params, namespace=('global',)
        )
        self.context.add_func(('global',), func_decl.name, func_decl)
        return ast.FunctionReference(func_decl.name, None)

    # pylint: disable=unused-argument
    def gen_new(self, etype, only_leaves=False, subtype=True):
        if isinstance(etype, tp.ParameterizedType):
            etype = etype.to_variance_free()
        news = {
            self.bt_factory.get_any_type(): ast.New(
                self.bt_factory.get_any_type(), args=[]),
            self.bt_factory.get_void_type(): ast.New(
                self.bt_factory.get_void_type(), args=[])
        }
        con = news.get(etype)
        if con is not None:
            return con

        if getattr(etype, 'is_function_type', lambda: False)():
            if ut.random.bool():
                func_refs = self.get_func_refs(etype)
                if len(func_refs) == 0:
                    func_ref = self.gen_func_ref(etype)
                    if func_ref:
                        return func_ref
                else:
                    return ut.random.choice(func_refs)
            params = [self.gen_param_decl(et) for et in etype.type_args[:-1]]
            ret_type = etype.type_args[-1]
            return self.gen_lambda(etype=ret_type, params=params)

        class_decl = self._get_subclass(etype, subtype)
        # No class was found corresponding to the given type. Probably,
        # the given type is a type parameter. So, if this type parameter has
        # a bound, generate a value of this bound. Otherwise, generate a bottom
        # value.
        if class_decl is None:
            return ast.BottomConstant(etype)

        if etype.is_type_constructor():
            etype, _ = tu.instantiate_type_constructor(
                etype, self.get_types())
        if class_decl.is_parameterized() and (
              class_decl.get_type().name != etype.name):
            etype, _ = tu.instantiate_type_constructor(
                class_decl.get_type(), self.get_types())
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
            expr_type = tp.substitute_type(field.get_type(), type_param_map)
            # FIXME We set subtype=False to prevent infinite object
            # initialization.
            args.append(self.generate_expr(expr_type, only_leaves,
                                           subtype=False))
        self._new_from_class = prev
        self.depth = initial_depth
        new_type = class_decl.get_type()
        if class_decl.is_parameterized():
            new_type = new_type.new(etype.type_args)
        return ast.New(new_type, args)

    def gen_variable(self, etype, only_leaves=False, subtype=True):
        # Get all variables declared in the current namespace or
        # the outer namespace.
        variables = self.context.get_vars(self.namespace).values()
        # Case where we want only final variables
        # Or variables declared in the nested function
        if self._inside_java_lambda:
            variables = list(filter(
                lambda v: (getattr(v, 'is_final', False) or v not in
                    self.context.get_vars(self.namespace[:-1]).values()),
                variables))
        # If we need to use a variable of a specific types, then filter
        # all variables that match this specific type.
        if subtype:
            fun = lambda v, t: v.get_type().is_assignable(t)
        else:
            fun = lambda v, t: v.get_type() == t
        variables = [v for v in variables if fun(v, etype)]
        if not variables:
            return self.generate_expr(etype, only_leaves=only_leaves,
                                      subtype=subtype, exclude_var=True)
        varia = ut.random.choice([v.name for v in variables])
        return ast.Variable(varia)

    def _get_assignable_vars(self):
        variables = []
        for var in self.context.get_vars(self.namespace).values():
            if self._inside_java_lambda:
                continue
            if not getattr(var, 'is_final', True):
                variables.append((None, var))
                continue
            var_type = self._get_var_type_to_search(var.get_type())
            if not var_type:
                continue
            if isinstance(getattr(var_type, 't_constructor', None),
                          self.function_type):
                continue
            cls, type_var_map = self._get_class(var_type)
            for field in cls.fields:
                # Ok here we create a new field whose type corresponds
                # to the type argument with which the class 'c' is
                # instantiated.
                field_sub = ast.FieldDeclaration(
                    field.name,
                    field_type=tp.substitute_type(field.get_type(),
                                                  type_var_map)
                )
                if not field.is_final:
                    variables.append((ast.Variable(var.name), field_sub))
        return variables

    def _get_classes_with_assignable_fields(self):
        classes = []
        class_decls = self.context.get_classes(self.namespace).values()
        for c in class_decls:
            for field in c.fields:
                if not field.is_final:
                    classes.append((c, field))
        assignable_types = []
        for c, f in classes:
            t, type_var_map = c.get_type(), {}
            if t.is_type_constructor():
                variance_choices = {
                    t_param: (False, True)
                    for t_param in t.type_parameters
                }
                t, type_var_map = tu.instantiate_type_constructor(
                    t, self.get_types(exclude_arrays=True),
                    variance_choices=variance_choices)
                # Ok here we create a new field whose type corresponds
                # to the type argument with which the class 'c' is
                # instantiated.
                f = ast.FieldDeclaration(
                    f.name,
                    field_type=tp.substitute_type(f.get_type(),
                                                  type_var_map)
                )
            assignable_types.append((t, f))

        if not assignable_types:
            return None
        return ut.random.choice(assignable_types)

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
                expr_type, field = res
                variables = [(self.generate_expr(expr_type,
                                                 only_leaves, subtype), field)]
        if not variables:
            # Nothing of the above worked, so generate a 'var' variable,
            # and perform the assignment
            etype = self.select_type(exclude_covariants=True,
                                     exclude_contravariants=True)
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
        gen_bottom = (
            variable.get_type().is_wildcard() or
            (
                variable.get_type().is_parameterized() and
                variable.get_type().has_wildcards()
            )
        )
        return ast.Assignment(variable.name, self.generate_expr(
            variable.get_type(), only_leaves, subtype, gen_bottom=gen_bottom),
                              receiver=receiver,)

    def _filter_subtypes(self, subtypes, initial_type):
        new_subtypes = []
        for t in subtypes:
            if t.is_type_var():
                continue
            if self.language != 'kotlin':
                # We can't check the instance of a parameterized type due
                # to type erasure. The only exception is Kotlin, see below.
                if not t.is_parameterized():
                    new_subtypes.append(t)
                continue

            # In Kotlin, you can smart cast a parameterized type like the
            # following.

            # class A<T>
            # class B<T> extends A<T>
            # fun test(x: A<String>) {
            #   if (x is B) {
            #      // the type of x is B<String> here.
            #   }
            # }
            if t.is_parameterized():
                t_con = t.t_constructor
                if t_con.is_subtype(initial_type):
                    continue
            new_subtypes.append(t)
        return new_subtypes

    def gen_is_expr(self, expr_type, only_leaves=False, subtype=True):
        def _get_extra_decls(namespace):
            return [
                v
                for v in self.context.get_declarations(
                    namespace, only_current=True).values()
                if (isinstance(v, ast.VariableDeclaration) or
                    isinstance(v, ast.FunctionDeclaration))
            ]

        final_vars = [
            v
            for v in self.context.get_vars(self.namespace).values()
            if (
                # We can smart cast variable that are final, have explicit
                # types, and are not overridable.
                getattr(v, 'is_final', True) and
                not v.is_type_inferred and
                not getattr(v, 'can_override', True)
            )
        ]
        if not final_vars:
            return self.generate_expr(expr_type, only_leaves=True,
                                      subtype=subtype)
        prev_depth = self.depth
        self.depth += 3
        var = ut.random.choice(final_vars)
        var_type = var.get_type()
        subtypes = tu.find_subtypes(var_type, self.get_types(),
                                    include_self=False, concrete_only=True)
        subtypes = self._filter_subtypes(subtypes, var_type)
        if not subtypes:
            return self.generate_expr(expr_type, only_leaves=True,
                                      subtype=subtype)

        subtype = ut.random.choice(subtypes)
        initial_decls = _get_extra_decls(self.namespace)
        prev_namespace = self.namespace
        self.namespace += ('true_block',)
        # Here, we create a 'virtual' variable declaration inside the
        # namespace of the block corresponding to the true branch. This
        # variable has the same name with the variable that appears in
        # the left-hand side of the 'is' expression, but its type is the
        # selected subtype.
        self.context.add_var(self.namespace, var.name,
                             ast.VariableDeclaration(
                                 var.name,
                                 ast.BottomConstant(var.get_type()),
                                 var_type=subtype))
        true_expr = self.generate_expr(expr_type)
        # We pop the variable from context. Because it's no longer used.
        self.context.remove_var(self.namespace, var.name)
        extra_decls_true = [v for v in _get_extra_decls(self.namespace)
                            if v not in initial_decls]
        if extra_decls_true:
            true_expr = ast.Block(extra_decls_true + [true_expr],
                                  is_func_block=False)
        self.namespace = prev_namespace + ('false_block',)
        false_expr = self.generate_expr(expr_type, only_leaves=only_leaves,
                                        subtype=subtype)
        extra_decls_false = [v for v in _get_extra_decls(self.namespace)
                             if v not in initial_decls]
        if extra_decls_false:
            false_expr = ast.Block(extra_decls_false + [false_expr],
                                   is_func_block=False)
        self.namespace = prev_namespace
        self.depth = prev_depth
        return ast.Conditional(
            ast.Is(ast.Variable(var.name), subtype),
            true_expr,
            false_expr
        )

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
            lambda x: self.gen_is_expr(x, only_leaves=only_leaves,
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
                      exclude_var=False, gen_bottom=False):
        if gen_bottom:
            return ast.BottomConstant(None)
        find_subtype = (
            expr_type and
            subtype and expr_type != self.bt_factory.get_void_type()
            and ut.random.bool()
        )
        expr_type = expr_type or self.select_type()
        if find_subtype:
            subtypes = tu.find_subtypes(expr_type, self.get_types(),
                                        include_self=True, concrete_only=True)
            expr_type = ut.random.choice(subtypes)
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
