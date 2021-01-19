import itertools
from typing import List

from src import utils
from src.ir import ast, types as tp


def _construct_related_types(etype, types, get_subtypes):
    valid_args = []
    for i, t_param in enumerate(etype.t_constructor.type_parameters):
        if t_param.is_invariant():
            t_args = [etype.type_args[i]]
        elif t_param.is_covariant():
            t_args = _find_types(etype.type_args[i], types,
                                 get_subtypes, True,
                                 t_param.bound, concrete_only=True)
        else:
            t_args = _find_types(etype.type_args[i], types,
                                 not get_subtypes, True,
                                 t_param.bound, concrete_only=True)
        valid_args.append(list(t_args))

    return [
        tp.ParameterizedType(etype.t_constructor, type_args)
        for type_args in itertools.product(*valid_args)
        if type_args != tuple(etype.type_args)
    ]


# FIXME RecursionError
def _find_types(etype, types, get_subtypes, include_self, bound=None,
                concrete_only=False):
    def to_type(stype):
        if isinstance(stype, tp.TypeConstructor):
            stype, _ = instantiate_type_constructor(stype, types)
        return stype

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
    return [to_type(t) for t in t_set] if concrete_only else list(t_set)


def find_subtypes(etype, types, include_self=False, bound=None,
                  concrete_only=False):
    return _find_types(etype, types, get_subtypes=True,
                       include_self=include_self, concrete_only=concrete_only)


def find_supertypes(etype, types, include_self=False, bound=None,
                    concrete_only=False):
    return _find_types(etype, types, get_subtypes=False,
                       include_self=include_self, bound=bound,
                       concrete_only=concrete_only)


def _update_type_constructor(etype, new_type):
    assert isinstance(new_type, tp.TypeConstructor)
    if isinstance(etype, tp.ParameterizedType):
        etype.t_constructor = new_type
        return etype
    if isinstance(etype, tp.TypeConstructor):
        return new_type
    return etype


def update_supertypes(etype, new_type,
                      test_pred=lambda x, y: x.name == y.name):
    visited = [etype]
    while visited:
        source = visited[-1]
        for i, supert in enumerate(source.supertypes):
            if supert == new_type:
                return
            source.supertypes[i] = update_type(supert, new_type, test_pred)

            if supert not in visited:
                visited.append(supert)
        visited = visited[1:]


def update_type(etype, new_type, test_pred=lambda x, y: x.name == y.name):
    if etype is None:
        return etype
    if isinstance(etype, tp.Builtin) or isinstance(new_type, tp.Builtin):
        return etype
    # Case 1: The test_pred func of the two types match.
    if test_pred(etype, new_type):
        # So if the new type is a type constructor update the type
        # constructor of 'etype' (if it is applicable)
        if isinstance(new_type, tp.TypeConstructor):
            return _update_type_constructor(etype, new_type)
        # Otherwise replace `etype` with `new_type`
        return new_type

    update_supertypes(etype, new_type, test_pred)
    # Case 2: If etype is a parameterized type, recursively inspect its type
    # arguments and type constructor for updates.
    if isinstance(etype, tp.ParameterizedType):
        etype.type_args = [update_type(ta, new_type) for ta in etype.type_args]
        etype.t_constructor = update_type(
            etype.t_constructor, new_type, test_pred)
        return etype
    # Case 3: If etype is a type constructor recursively inspect is type
    # parameters for updates.
    if isinstance(etype, tp.TypeConstructor):
        t_params = []
        for t_param in etype.type_parameters:
            if t_param.bound is not None:
                t_param.bound = update_type(t_param.bound, new_type, test_pred)
            t_params.append(t_param)
        etype.type_parameters = t_params
        return etype
    return etype


def _get_available_types(types, only_regular):
    if not only_regular:
        return types
    available_types = []
    for ptype in types:
        if isinstance(ptype, ast.ClassDeclaration) and (
                ptype.class_type != ast.ClassDeclaration.REGULAR):
            continue
        available_types.append(ptype)
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
            cls_type = c.get_type()
        else:
            cls_type = c
        if isinstance(cls_type, tp.TypeConstructor):
            # We just selected a parameterized class, so we need to instantiate
            # this too. Remove this class from available types to avoid
            # depthy instantiations.
            types = [t for t in types if t != c]
            cls_type, _ = instantiate_type_constructor(
                cls_type, types, only_regular)
        t_args.append(cls_type)
    # Also return a map of type parameters and their instantiations.
    params_map = {t_param: t_args[i]
                  for i, t_param in enumerate(
                      type_constructor.type_parameters)}
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
