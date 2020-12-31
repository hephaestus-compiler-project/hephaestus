import itertools
from typing import List

from src import utils
from src.ir import ast, types as tp


def _construct_related_types(t, types, find_subtypes):
    valid_args = []
    for i, t_param in enumerate(t.t_constructor.type_parameters):
        if t_param.is_invariant():
            t_args = [t.type_args[i]]
        elif t_param.is_covariant():
            t_args = _find_types(t.type_args[i], types,
                                 find_subtypes, True,
                                 t_param.bound, concrete_only=True)
        else:
            t_args = _find_types(t.type_args[i], types,
                                 not find_subtypes, True,
                                 t_param.bound, concrete_only=True)
        valid_args.append(list(t_args))

    return [
        tp.ParameterizedType(t.t_constructor, type_args)
        for type_args in itertools.product(*valid_args)
        if type_args != tuple(t.type_args)
    ]


def _find_types(t, types, find_subtypes, include_self, bound=None,
                concrete_only=False):
    def to_type(t):
        if isinstance(t, tp.TypeConstructor):
            t, _ = instantiate_type_constructor(t, types)
        return t

    # Otherwise, if we want to find the supertypes of a given type, `bound`
    # is interpreted a greatest bound.
    if not find_subtypes:
        # Find supertypes
        t_set = t.get_supertypes()
    else:
        # Find subtypes
        t_set = set()
        for c in types:
            t2 = c.get_type() if hasattr(c, 'get_type') else c
            if t == t2:
                continue
            if t2.is_subtype(t):
                t_set.add(t2)
                continue

    if isinstance(t, tp.ParameterizedType):
        t_set.update(_construct_related_types(t, types, find_subtypes))
    if include_self:
        t_set.add(t)
    else:
        t_set.discard(t)

    if not find_subtypes and bound:
        t_set = {st for st in t_set if st.is_subtype(bound)}
    return [to_type(t) for t in t_set] if concrete_only else list(t_set)


def find_subtypes(t, types, include_self=False, bound=None,
                  concrete_only=False):
    return _find_types(t, types, find_subtypes=True,
                       include_self=include_self, concrete_only=concrete_only)


def find_supertypes(t, types, include_self=False, bound=None,
                    concrete_only=False):
    return _find_types(t, types, find_subtypes=False,
                       include_self=include_self, bound=bound,
                       concrete_only=concrete_only)


def _update_type_constructor(t, new_type):
    assert isinstance(new_type, tp.TypeConstructor)
    if isinstance(t, tp.ParameterizedType):
        t.t_constructor = new_type
        return t
    elif isinstance(t, tp.TypeConstructor):
        return new_type
    else:
        return t


def update_supertypes(t, new_type, test_pred=lambda x, y: x.name == y.name):
    visited = [t]
    while visited:
        source = visited[-1]
        for i, st in enumerate(source.supertypes):
            if st == new_type:
                return
            source.supertypes[i] = update_type(st, new_type, test_pred)

            if st not in visited:
                visited.append(st)
        visited = visited[1:]


def update_type(t, new_type, test_pred=lambda x, y: x.name == y.name):
    if t is None:
        return t
    if isinstance(t, tp.Builtin) or isinstance(new_type, tp.Builtin):
        return t
    # Case 1: The test_pred func of the two types match.
    if test_pred(t, new_type):
        # So if the new type is a type constructor update the the type
        # constructor of 't' (if it is applicable)
        if isinstance(new_type, tp.TypeConstructor):
            return _update_type_constructor(t, new_type)
        # Otherwise replace `t` with `new_type`
        else:
            return new_type

    update_supertypes(t, new_type, test_pred)
    # Case 2: If t is a parameterized type, recursively inspect its type
    # arguments and type constructor for updates.
    if isinstance(t, tp.ParameterizedType):
        t.type_args = [update_type(ta, new_type) for ta in t.type_args]
        t.t_constructor = update_type(t.t_constructor, new_type, test_pred)
        return t
    # Case 3: If t is a type constructor recursively inspect is type
    # parameters for updates.
    if isinstance(t, tp.TypeConstructor):
        t_params = []
        for t_param in t.type_parameters:
            if t_param.bound is not None:
                t_param.bound = update_type(t_param.bound, new_type, test_pred)
            t_params.append(t_param)
        t.type_parameters = t_params
        return t
    return t


def _get_available_types(types, only_regular):
    if not only_regular:
        return types
    available_types = []
    for t in types:
        if isinstance(t, ast.ClassDeclaration) and (
                t.class_type != ast.ClassDeclaration.REGULAR):
            continue
        available_types.append(t)
    return available_types


def instantiate_type_constructor(type_constructor: tp.TypeConstructor,
                                 types: List[tp.Type],
                                 only_regular=True):
    types = _get_available_types(types, only_regular)
    # Instantiate a type constructor with random type arguments.
    t_args = []
    for t_param in type_constructor.type_parameters:
        if t_param.bound:
            # If the type parameter has a bound, then find types that
            # are subtypes to this bound.
            a_types = find_subtypes(t_param.bound, types, True)
        else:
            a_types = types
        c = utils.random.choice(a_types)
        if isinstance(c, ast.ClassDeclaration):
            t = c.get_type()
        else:
            t = c
        if isinstance(t, tp.TypeConstructor):
            # We just selected a parameterized class, so we need to instantiate
            # this too. Remove this class from available types to avoid
            # depthy instantiations.
            types = [t for t in types if t != c]
            t, _ = instantiate_type_constructor(t, types, only_regular)
        t_args.append(t)
    # Also return a map of type parameters and their instantiations.
    params_map = {t_param: t_args[i]
                  for i, t_param in enumerate(type_constructor.type_parameters)}
    return type_constructor.new(t_args), params_map


def choose_type(types: List[tp.Type], only_regular=True):
    # Randomly choose a type from the list of available types.
    types = _get_available_types(types, only_regular)
    c = utils.random.choice(types)
    if isinstance(c, ast.ClassDeclaration):
        t = c.get_type()
    else:
        t = c
    if isinstance(t, tp.TypeConstructor):
        # We just selected a parameterized class, so we need to instantiate
        # it.
        types = [t for t in types if t != c]
        t, _ = instantiate_type_constructor(t, types, only_regular)
    return t
