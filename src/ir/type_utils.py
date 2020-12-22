from src.ir import types as tp


def _find_types(t, types, find_subtypes, include_self):
    lst = []
    for c in types:
        if hasattr(c, 'get_type'):
            t2 = c.get_type()
        else:
            t2 = c
        if isinstance(t2, tp.AbstractType):
            # TODO: revisit
            continue
        if t == t2:
            continue
        if find_subtypes and t2.is_subtype(t):
            lst.append(c)
            continue
        if not find_subtypes and t.is_subtype(t2):
            lst.append(c)
    if include_self:
        lst.append(t)
    return lst


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
        if t.t_constructor is None:
            import pdb; pdb.set_trace()
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
