import itertools

from src.ir import types as tp


def _construct_related_types(t, types, find_subtypes):
    valid_args = []
    for i, t_param in enumerate(t.t_constructor.type_parameters):
        if t_param.is_invariant():
            t_args = [t.type_args[i]]
        elif t_param.is_covariant():
            t_args = _find_types(t.type_args[i], types,
                                 find_subtypes, True)
        else:
            t_args = _find_types(t.type_args[i], types,
                                 not find_subtypes, True)
        valid_args.append(t_args)

    return [
        tp.ParameterizedType(t.t_constructor, type_args)
        for type_args in itertools.product(*valid_args)
        if type_args != tuple(t.type_args)
    ]


def _find_types(t, types, find_subtypes, include_self):
    t_set = set()
    for c in types:
        if hasattr(c, 'get_type'):
            t2 = c.get_type()
        else:
            t2 = c
        if isinstance(t2, tp.AbstractType) and (
                not isinstance(t2, tp.TypeConstructor)):
            # TODO: revisit
            continue
        if t == t2:
            continue
        if find_subtypes and t2.is_subtype(t):
            t_set.add(c)
            continue
        if not find_subtypes and t.is_subtype(t2):
            t_set.add(c)
        if isinstance(t, tp.ParameterizedType):
            t_set.update(_construct_related_types(t, types, find_subtypes))
    if include_self:
        t_set.add(t)
    return t_set


def find_subtypes(t, types, include_self=False):
    return _find_types(t, types, find_subtypes=True, include_self=include_self)


def find_supertypes(t, types, include_self=False):
    return _find_types(t, find_subtypes=False, include_self=include_self)


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
