import itertools
from typing import List, Tuple, Dict

import src.ir.ast as ast
import src.ir.types as tp
import src.ir.context as ctx
import src.ir.builtins as bt
from src import utils


def _construct_related_types(etype, types, get_subtypes):
    valid_args = []
    for i, t_param in enumerate(etype.t_constructor.type_parameters):
        if t_param.is_invariant():
            t_args = [etype.type_args[i]]
        elif t_param.is_covariant():
            t_args = _find_types(etype.type_args[i].concrete_type, types,
                                 get_subtypes, True,
                                 t_param.bound, concrete_only=True)
        else:
            t_args = _find_types(etype.type_args[i].concrete_type, types,
                                 not get_subtypes, True,
                                 t_param.bound, concrete_only=True)
        # Type argument should not be primitives.
        t_args = [t.to_type_arg() for t in t_args if not t.is_primitive()]
        valid_args.append(t_args)

    return [
        etype.t_constructor.new(type_args)
        for type_args in itertools.product(*valid_args)
        if type_args != tuple(etype.type_args)
    ]


def to_type(stype, types):
    if isinstance(stype, tp.TypeConstructor):
        stype, _ = instantiate_type_constructor(stype, types)
    return stype


def _find_types(etype, types, get_subtypes, include_self, bound=None,
                concrete_only=False):

    # Otherwise, if we want to find the supertypes of a given type, `bound`
    # is interpreted a greatest bound.
    if not get_subtypes:
        # Find supertypes
        t_set = etype.get_supertypes()
    else:
        # Find subtypes
        t_set = set()
        for c in types:
            selected_type = c.get_type() if hasattr(c, 'get_type') else c
            if isinstance(selected_type, tp.AbstractType) and (
                    not isinstance(selected_type, tp.TypeConstructor)):
                # TODO: revisit
                continue
            if etype == selected_type:
                continue
            if selected_type.is_subtype(etype):
                t_set.add(selected_type)
                continue

    if isinstance(etype, tp.ParameterizedType):
        t_set.update(_construct_related_types(etype, types, get_subtypes))
    if include_self:
        t_set.add(etype)
    else:
        t_set.discard(etype)

    if not get_subtypes and bound:
        t_set = {st for st in t_set if st.is_subtype(bound)}
    return [to_type(t, types) for t in t_set] if concrete_only else list(t_set)


def find_subtypes(etype, types, include_self=False, bound=None,
                  concrete_only=False):
    return _find_types(etype, types, get_subtypes=True,
                       include_self=include_self, concrete_only=concrete_only)


def find_supertypes(etype, types, include_self=False, bound=None,
                    concrete_only=False):
    return _find_types(etype, types, get_subtypes=False,
                       include_self=include_self, bound=bound,
                       concrete_only=concrete_only)


def get_irrelevant_parameterized_type(etype, types, type_args_map,
                                      factory: bt.BuiltinFactory):
    assert isinstance(etype, tp.TypeConstructor)
    type_args = type_args_map.get(etype.name)

    if type_args is None:
        # We don't have any restriction for the type arguments, so simply
        # instantiate the given type constructor.
        t, _ = instantiate_type_constructor(etype, types)
        return t

    new_type_args = list(type_args)

    for i, t_param in enumerate(etype.type_parameters):
        if t_param.is_invariant():
            type_list = [to_type(t, types)
                         for t in types
                         if t != type_args[i].concrete_type]
            new_type_args[i] = utils.random.choice(type_list).to_type_arg()
        else:
            t = find_irrelevant_type(type_args[i].concrete_type, types,
                                     factory)
            if t is None:
                continue
            new_type_args[i] = t.to_type_arg()

    if new_type_args == type_args:
        return None
    return etype.new(new_type_args)


def find_irrelevant_type(etype: tp.Type, types: List[tp.Type],
                         factory: bt.BuiltinFactory) -> tp.Type:
    """
    Find a type that is irrelevant to the given type.

    This means that there is no subtyping relation between the given type
    and the returned type.
    """

    def _cls2type(cls):
        if hasattr(cls, 'get_type'):
            return cls.get_type()
        return cls

    if etype == factory.get_any_type():
        return None

    if isinstance(etype, tp.TypeParameter):
        if etype.bound is None or etype.bound == factory.get_any_type():
            return choose_type(types, only_regular=True)
        else:
            etype = etype.bound

    types = [_cls2type(t) for t in types]
    supertypes = find_supertypes(etype, types, include_self=True,
                                 concrete_only=True)
    subtypes = find_subtypes(etype, types, include_self=True,
                             concrete_only=True)
    relevant_types = supertypes + subtypes
    # If any type included in the list of relevant types is parameterized,
    # then create a map with their type arguments.
    type_args_map = {
        t.name: t.type_args
        for t in relevant_types
        if isinstance(t, tp.ParameterizedType)
    }
    available_types = [t for t in types if t not in relevant_types]
    if not available_types:
        return None
    t = utils.random.choice(available_types)
    if isinstance(t, tp.TypeConstructor):
        # Must instantiate the given type constrcutor. Also pass the map of
        # type arguments in order to pass type arguments that are irrelevant
        # with any parameterized type created by this type constructor.
        type_list = [t for t in types if t != etype]
        return get_irrelevant_parameterized_type(
                t, type_list, type_args_map, factory)
    return t


def _update_type_constructor(etype, new_type):
    assert isinstance(new_type, tp.TypeConstructor)
    if isinstance(etype, tp.ParameterizedType):
        return new_type.new(etype.type_args)
    if isinstance(etype, tp.TypeConstructor):
        return new_type
    return etype


class TypeUpdater():
    def __init__(self):
        self._cache = {}

    def update_supertypes(self, etype, new_type,
                          test_pred=lambda x, y: x.name == y.name):
        visited = [etype]
        while visited:
            source = visited[-1]
            for i, supert in enumerate(source.supertypes):
                if supert == new_type:
                    return
                source.supertypes[i] = self._update_type(supert, new_type,
                                                         test_pred)

                if supert not in visited:
                    visited.append(supert)
            visited = visited[1:]

    def _update_type(self, etype, new_type,
                     test_pred=lambda x, y: x.name == y.name):
        if isinstance(etype, tp.TypeParameter) or (
            isinstance(etype, tp.TypeArgument)) or (
                isinstance(etype, tp.ParameterizedType)) or (
                    isinstance(etype, tp.TypeConstructor)):
            # We must re-compute parameterized types, as they may involve
            # different type arguments or type constructors.
            return self.update_type(etype, new_type, test_pred)
        key = (
            (etype.name, True)
            if isinstance(etype, tp.TypeConstructor)
            else (etype.name, False)
        )
        updated_type = self._cache.get(key)
        if not updated_type:
            new_type = self.update_type(etype, new_type, test_pred)
            # We do not store builtin types into cache, because we never
            # update builtin types.
            if not isinstance(new_type, (tp.Builtin, tp.TypeArgument)):
                self._cache[key] = new_type
            return new_type
        return updated_type

    def update_type(self, etype, new_type,
                    test_pred=lambda x, y: x.name == y.name):
        if etype is None:
            return etype
        if isinstance(etype, tp.Builtin) or isinstance(new_type, tp.Builtin):
            return etype

        self.update_supertypes(etype, new_type, test_pred)
        is_type_arg = isinstance(etype, tp.TypeArgument)
        # Case 1: The test_pred func of the two types match.
        if test_pred(etype, new_type) and not is_type_arg:
            # So if the new type is a type constructor update the type
            # constructor of 'etype' (if it is applicable)
            if isinstance(new_type, tp.TypeConstructor):
                return _update_type_constructor(etype, new_type)
            # Otherwise replace `etype` with `new_type`
            return new_type

        # Case 2: If etype is a parameterized type, recursively inspect its
        # type arguments and type constructor for updates.
        if isinstance(etype, tp.ParameterizedType):
            new_type_args = [self._update_type(ta, new_type).to_type_arg()
                             for ta in etype.type_args]
            new_t_constructor = self._update_type(
                etype.t_constructor, new_type, test_pred)
            return new_t_constructor.new(new_type_args)
        # Case 3: If etype is a type constructor recursively inspect is type
        # parameters for updates.
        if isinstance(etype, tp.TypeConstructor):
            t_params = []
            for t_param in etype.type_parameters:
                if t_param.bound is not None:
                    t_param.bound = self._update_type(
                        t_param.bound, new_type, test_pred)
                t_params.append(t_param)
            etype.type_parameters = t_params
            return etype

        # Case 4: If etype is a type parameter inspect its bound (if any) for
        # updates
        if isinstance(etype, tp.TypeParameter):
            if etype.bound is not None:
                etype.bound = self._update_type(etype.bound, new_type,
                                                test_pred)

        # Case 5: If etype is a type argument, then update the enclosing type.
        if is_type_arg:
            etype.concrete_type = self._update_type(etype.concrete_type,
                                                    new_type, test_pred)
        return etype


def _get_available_types(types, only_regular, primitives=True):
    if not only_regular:
        return types
    available_types = []
    for ptype in types:
        if isinstance(ptype, ast.ClassDeclaration) and (
                ptype.class_type != ast.ClassDeclaration.REGULAR):
            continue
        if isinstance(ptype, tp.TypeConstructor):
            continue
        if not primitives and hasattr(ptype, 'box_type'):
            ptype = ptype.box_type()
        available_types.append(ptype)
    return available_types


def instantiate_type_constructor(type_constructor: tp.TypeConstructor,
                                 types: List[tp.Type],
                                 only_regular=True,
                                 params_map=None):
    types = _get_available_types(types, only_regular, primitives=False)
    # Instantiate a type constructor with random type arguments.
    t_args = []
    params_map = params_map or {}
    for t_param in type_constructor.type_parameters:
        if t_param.bound:
            if not isinstance(t_param.bound, tp.AbstractType):
                # If the type parameter has a bound, then find types that
                # are subtypes to this bound.
                a_types = find_subtypes(t_param.bound, types, True)
                for i, t in enumerate(a_types):
                    if isinstance(t, tp.ParameterizedType):
                        a_types[i] = tp.substitute_type_args(t, params_map)
            else:
                a_types = [params_map[t_param.bound].to_type()]
        else:
            a_types = types
        c = utils.random.choice(a_types)
        if isinstance(c, ast.ClassDeclaration):
            cls_type = c.get_type()
        else:
            cls_type = c
        if isinstance(cls_type, tp.TypeConstructor):
            # We just selected a parameterized class, so we need to instantiate
            # this too. Remove this class from available types to avoid
            # depthy instantiations.
            types = [t for t in types if t != c]
            cls_type, _ = instantiate_type_constructor(
                cls_type, types, only_regular, params_map)
        t_arg = cls_type.to_type_arg()
        t_args.append(t_arg)
        params_map[t_param] = t_arg.to_type()
    # Also return a map of type parameters and their instantiations.
    return type_constructor.new(t_args), params_map


def choose_type(types: List[tp.Type], only_regular=True):
    # Randomly choose a type from the list of available types.
    types = _get_available_types(types, only_regular)
    c = utils.random.choice(types)
    if isinstance(c, ast.ClassDeclaration):
        cls_type = c.get_type()
    else:
        cls_type = c
    if isinstance(cls_type, tp.TypeConstructor):
        # We just selected a parameterized class, so we need to instantiate
        # it.
        types = [t for t in types if t != c]
        cls_type, _ = instantiate_type_constructor(
            cls_type, types, only_regular)
    return cls_type


def get_parameterized_type_instantiation(etype):
    if not isinstance(etype, tp.ParameterizedType):
        return {}
    return {
        t_param: etype.type_args[i].to_type()
        for i, t_param in enumerate(etype.t_constructor.type_parameters)
    }


def find_nearest_supertype(etype, types, pred=lambda x, y: x in y):
    stack = [etype]
    visited = {etype}
    while stack:
        source = stack.pop()
        for supertype in source.supertypes:
            if pred(supertype, types):
                return supertype
            if supertype not in visited:
                visited.add(supertype)
                stack.append(supertype)
    return None


def find_lub(type_a, type_b, types, any_type):
    # We must handle None to not throw run time exceptions
    if type_a is None or type_b is None:
        return None
    # FIXME use a proper algorithm
    if type_a == type_b:
        return type_a
    super_types_a = find_supertypes(type_a, types, include_self=True)
    super_types_b = find_supertypes(type_b, types, include_self=True)
    super_types = list(set(super_types_a) & set(super_types_b))
    res = (any_type, 0)
    for stype in super_types:
        score = len([t for t in super_types if stype.is_subtype(t)])
        if score >= res[1]:
            res = (stype, score)
    return res[0]


def get_decl_from_inheritance(receiver_t: tp.Type,
                              decl_name: str,
                              context: ctx.Context):
    """
    Inspect the inheritance chain until you find a declaration with a certain
    name.
    """
    classes = [
        c
        for c in context.get_classes(ast.GLOBAL_NAMESPACE,
                                     only_current=True).values()
        if not c.is_parameterized()
    ]
    supertypes = list(receiver_t.get_supertypes())
    # We need to traverse also the subtypes due to smart cast.
    # For example, a function may be defined in a child class but in the
    # context, we have the parent class due to smart cast.
    subtypes = list(find_subtypes(receiver_t, classes, include_self=False))
    for st in supertypes + subtypes:
        decl = ctx.get_decl(context, ast.GLOBAL_NAMESPACE + (st.name,),
                            decl_name)
        if decl is not None:
            return decl[1], st
    return None


def get_type_hint(expr, context: ctx.Context, namespace: Tuple[str],
                  factory: bt.BuiltinFactory, types: List[tp.Type],
                  smart_casts=[]) -> tp.Type:
    """
    Get a hint of the type of the expression.

    It's just a hint.

    # NOTE that smart_casts are used in both branches which is incorrect.
    # In the generated programs this works.
    """

    names = []

    def _comp_type(t, name):
        if t is None:
            return None
        decl = get_decl_from_inheritance(t, name, context)
        if decl is None:
            return None
        decl, rec_t = decl
        if isinstance(decl.get_type(), tp.AbstractType):
            assert isinstance(rec_t, tp.ParameterizedType)
            type_param_map = {
                t_param: rec_t.type_args[i].to_type()
                for i, t_param in enumerate(
                    rec_t.t_constructor.type_parameters)
            }
            return type_param_map.get(decl.get_type())
        else:
            return decl.get_type()

    def _return_type_hint(t):
        if not names:
            return t
        for name in reversed(names):
            t = _comp_type(t, name)
            if t is None:
                return None
        return t

    def smart_cast_get(expr):
        return next((e[1] for e in reversed(smart_casts)
                     if e[0].is_equal(expr)), None)

    while True:
        if isinstance(expr, ast.IntegerConstant):
            return _return_type_hint(expr.integer_type or
                                     type(factory.get_integer_type()))

        if isinstance(expr, ast.RealConstant):
            return _return_type_hint(expr.real_type)

        if isinstance(expr, ast.BooleanConstant):
            return _return_type_hint(factory.get_boolean_type())

        if isinstance(expr, ast.CharConstant):
            return _return_type_hint(factory.get_char_type())

        if isinstance(expr, ast.StringConstant):
            return _return_type_hint(factory.get_string_type())

        if isinstance(expr, ast.BinaryOp):
            return _return_type_hint(factory.get_boolean_type())

        if isinstance(expr, ast.New):
            return _return_type_hint(expr.class_type)

        if isinstance(expr, ast.ArrayExpr):
            return _return_type_hint(expr.array_type)

        if isinstance(expr, ast.Block):
            return _return_type_hint(get_type_hint(
                expr.body[-1], context, namespace, factory, types,
                smart_casts=smart_casts))

        if isinstance(expr, ast.Variable):
            smart_type = smart_cast_get(expr)
            if smart_type:
                vardecl = ctx.get_decl(context, namespace, expr.name)
                return _return_type_hint(smart_type)
            vardecl = ctx.get_decl(context, namespace, expr.name)
            return _return_type_hint(
                None if vardecl is None else vardecl[1].get_type())

        if isinstance(expr, ast.Conditional):
            expr1 = expr.true_branch
            expr2 = expr.false_branch


            if isinstance(expr.cond, ast.Is):
                # true branch smart cast
                if not expr.cond.operator.is_not:
                    smart_casts.append((expr.cond.lexpr, expr.cond.rexpr))
                    e1_type = get_type_hint(expr1, context, namespace, factory,
                                            types, smart_casts=smart_casts)
                    smart_casts.pop()
                    e2_type = get_type_hint(expr2, context, namespace, factory,
                                            types, smart_casts=smart_casts)
                # false branch smart cast
                else:
                    e1_type = get_type_hint(expr1, context, namespace, factory,
                                            types, smart_casts=smart_casts)
                    smart_casts.append((expr.cond.lexpr, expr.cond.rexpr))
                    e2_type = get_type_hint(expr2, context, namespace, factory,
                                            types, smart_casts=smart_casts)
                    smart_casts.pop()
            else:
                e1_type = get_type_hint(expr1, context, namespace, factory,
                                        types, smart_casts=smart_casts)
                e2_type = get_type_hint(expr2, context, namespace, factory,
                                        types, smart_casts=smart_casts)

            return _return_type_hint(find_lub(
                e1_type, e2_type, types, factory.get_any_type()))

        if isinstance(expr, ast.FunctionCall):
            if expr.receiver is None:
                funcdecl = ctx.get_decl(context, namespace, expr.func)
                return _return_type_hint(
                    None if funcdecl is None else funcdecl[1].get_type())
            names.append(expr.func)
            expr = expr.receiver

        elif isinstance(expr, ast.FieldAccess):
            names.append(expr.field)
            expr = expr.expr

        else:
            return factory.get_void_type()


def node_in_expr(node, expr):
    """Check if node is expr or is inside expr
    """
    to_visit = [expr]

    while len(to_visit) > 0:
        expression = to_visit.pop()
        if node.is_equal(expression):
            return True
        to_visit.extend(expression.children())
    return False


def is_builtin(t, builtin_factory):
    return isinstance(t, tp.Builtin) or (
        t.name == builtin_factory.get_array_type().name
    )
