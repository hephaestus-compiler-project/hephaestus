from collections import OrderedDict
from typing import List, Tuple, Dict

import src.ir.ast as ast
import src.ir.types as tp
import src.ir.context as ctx
import src.ir.builtins as bt
from src import utils


def _replace_type_argument(base_targ: tp.Type, bound: tp.Type, types,
                           has_type_variables):
    # If the bound of the corresponding parameter does not contain type
    # variables, then we are unable to seek another matching type argument.
    # So, return the current type argument.
    if not has_type_variables:
        return base_targ
    if base_targ.is_wildcard() and not base_targ.is_invariant():
        base_targ = base_targ.bound
    if not base_targ.is_parameterized():
        return base_targ if base_targ.is_subtype(bound) else None

    if base_targ.name == bound.name:
        # Here we have a case like the following.
        # bound: A<Number, X>
        # current type argument: A<Number, Any>
        # So, we try to unify those types by initially replacing all type
        # arguments of `base_targ` with fresh type variables.
        # If unification succeeds, instantiate the underlying type constructor
        # with the concrete types assigned to each type variable.
        template_t = base_targ.t_constructor.new(
            base_targ.t_constructor.type_parameters)
        type_var_map = unify_types(bound, template_t, None)
        if not type_var_map:
            return None
        new_targ, _ = instantiate_type_constructor(
            base_targ.t_constructor, types, only_regular=True,
            type_var_map=type_var_map, variance_choices=None
        )
        type_var_map = {
            t_param: base_targ.type_args[i]
            for i, t_param in enumerate(
                base_targ.t_constructor.type_parameters)
        }
        return base_targ.to_variance_free(type_var_map)

    # Here, we have a case like the following.
    # bound: A<Number, X>
    # current type argument: B<Any>
    supertypes = base_targ.t_constructor.get_supertypes()
    supertype = None
    for st in supertypes:
        # We first check the type constructor of B has A<Number, X> as one of
        # its supertypes.
        if st.name == bound.name:
            supertype = st
            break
    if not supertype:
        return None
    # If we found matching supertype, we try to unify it with the given bound.
    type_var_map = unify_types(bound, supertype, None)
    if not type_var_map:
        return None
    # If unification succeeds, we try to instantiate the type contructor
    # of `base_targ` with the proper type arguments so that the returned
    # type is a subtype of `bound`.
    type_args = []
    for i, t_param in enumerate(base_targ.t_constructor.type_parameters):
        t_arg = type_var_map.get(t_param, base_targ.type_args[i])
        type_args.append(t_arg)
    return base_targ.t_constructor.new(type_args)


def _find_candidate_type_args(t_param: tp.TypeParameter,
                              base_targ: tp.Type,
                              types,
                              get_subtypes,
                              type_var_map={}):

    bound = None
    if t_param.bound:
        # If the bound of the current type parameter contains other type
        # parameters, substitute it based on the current type assignments
        # of those type parameters.
        bound = tp.substitute_type(t_param.bound, type_var_map)

    if bound and bound.is_parameterized():
        # If bound is `paramterized`, we seek another type argument that
        # is subtype of the the `new` bound.
        base_targ = _replace_type_argument(base_targ, bound, types,
                                           t_param.bound.has_type_variables())
    # If `base_targ` is None, this means that
    # we cannot find candidate type arguments that satisfy the bound of
    # the corresponding type parameter.
    if not base_targ:
        return None

    if t_param.is_invariant():
        t_args = [base_targ]
    elif t_param.is_covariant():
        t_args = _find_types(
            base_targ, types,
            get_subtypes, True, bound, concrete_only=True)
    else:
        t_args = _find_types(
            base_targ, types,
            not get_subtypes, True, bound, concrete_only=True)

    if not base_targ.is_wildcard():
        return t_args
    if base_targ.is_covariant():
        new_types = _find_types(
            base_targ.bound,
            types, get_subtypes, True, bound,
            concrete_only=True)
        new_types.extend([tp.WildCardType(t, tp.Covariant)
                          for t in new_types])
    elif base_targ.is_contravariant():
        new_types = _find_types(
            base_targ.bound, types,
            not get_subtypes, True, bound, concrete_only=True)
    else:
        new_types = []
    t_args.extend(new_types)
    return t_args


def _construct_related_types(etype: tp.ParameterizedType, types, get_subtypes):
    type_var_map = OrderedDict()
    if etype.name == 'Array':
        types = [t for t in types
                 if not t.is_type_var() and
                 not t.is_parameterized() and
                 not t.is_type_constructor()
                 ]
    for i, t_param in enumerate(etype.t_constructor.type_parameters):
        if t_param.bound in type_var_map:
            # Here we are trying to handle cases like the following.
            # class X<T1, T2: T1>
            # Therefore the type assignments for the type variable T2 must keep
            # up with the assignments of the type variable T1.
            # To do so, we track the index of the type variable T1.
            # Later, when instantiating the corresponding type constructor,
            # we replace this index with the type assigned to the type variable
            # T1. In this way, we guarantee that T1 and T2 have compatible
            # types.
            type_arg_bound = type_var_map[t_param.bound]
            base_targ = etype.type_args[i]
            is_same_type_var = (
                base_targ.is_wildcard() and
                base_targ.bound.name == type_arg_bound.name
            )
            is_subtype = (
                base_targ.is_wildcard() and
                base_targ.bound.is_subtype(type_arg_bound)
            )
            is_type_var = type_arg_bound.is_type_var()
            is_contravariant = (
                base_targ.is_wildcard() and base_targ.is_contravariant()
            )
            if is_type_var and not is_same_type_var:
                # OK, if T2 is invariant, then the possible types that T1
                # can have is etype.type_args[i].
                # This prevents us from situtations like the following.
                # A<out T1, T2: T1>
                # A<Double, Double> is not subtype of A<Number, Number>.
                type_var_map[t_param.bound] = base_targ
            elif not is_type_var and not is_contravariant:
                if not is_subtype:
                    # Suppose we have two type parameters X, Y, where Y <: X
                    # If the current type argument of Y is not subtype of
                    # X, then, we must replace the assignment we have done
                    # previously for X with a type that is a subtype of
                    # the current type argument of X.
                    type_var_map[t_param.bound] = base_targ
            elif is_contravariant and not is_type_var:
                # Here we handle case like the following.

                # Foo<out X, Y : X>
                # Foo<A, in A> current type
                # Foo<B, in B> this is not subtype of Foo<A, in A>
                # Therefore, here we replace B with the bound of in A.
                if type_arg_bound.is_subtype(base_targ.bound) and (
                      type_arg_bound.name != base_targ.bound.name):
                    type_var_map[t_param.bound] = base_targ.bound
            type_var_map[t_param] = type_var_map[t_param.bound]
        else:
            t_args = _find_candidate_type_args(t_param, etype.type_args[i],
                                               types, get_subtypes,
                                               type_var_map)
            if not t_args:
                # We were not able to construct a subtype of the given
                # parameterized type. Therefore, we give back the given
                # type.
                return etype
            # Type argument should not be primitives.
            t_args = [t for t in t_args if not t.is_primitive()]
            t_arg = utils.random.choice(t_args)
            type_var_map[t_param] = t_arg
    return etype.t_constructor.new(list(type_var_map.values()))


def to_type(stype, types):
    if stype.is_type_constructor():
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
            if etype == selected_type:
                continue
            if selected_type.is_subtype(etype):
                t_set.add(selected_type)
                continue

    if isinstance(etype, tp.ParameterizedType):
        t_set.add(_construct_related_types(etype, types, get_subtypes))
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
    assert etype.is_type_constructor()
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
                         if t != type_args[i]]
            new_type_args[i] = utils.random.choice(type_list)
        else:
            t = find_irrelevant_type(type_args[i], types, factory)
            if t is None:
                continue
            new_type_args[i] = t

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
    if t.is_type_constructor():
        # Must instantiate the given type constrcutor. Also pass the map of
        # type arguments in order to pass type arguments that are irrelevant
        # with any parameterized type created by this type constructor.
        type_list = [t for t in types if t != etype]
        return get_irrelevant_parameterized_type(
                t, type_list, type_args_map, factory)
    return t


def _update_type_constructor(etype, new_type):
    if etype.is_parameterized():
        return new_type.new(etype.type_args)
    if etype.is_type_constructor():
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
            isinstance(etype, tp.WildCardType)) or (
                isinstance(etype, tp.ParameterizedType)) or (
                    isinstance(etype, tp.TypeConstructor)):
            # We must re-compute parameterized types, as they may involve
            # different type arguments or type constructors.
            return self.update_type(etype, new_type, test_pred)
        key = (
            (etype.name, True)
            if etype.is_type_constructor()
            else (etype.name, False)
        )
        updated_type = self._cache.get(key)
        if not updated_type:
            new_type = self.update_type(etype, new_type, test_pred)
            # We do not store builtin types into cache, because we never
            # update builtin types.
            if not isinstance(new_type, (tp.Builtin, tp.WildCardType)):
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
        is_wildcard = isinstance(etype, tp.WildCardType)
        # Case 1: The test_pred func of the two types match.
        if test_pred(etype, new_type) and not is_wildcard:
            # So if the new type is a type constructor update the type
            # constructor of 'etype' (if it is applicable)
            if new_type.is_type_constructor():
                return _update_type_constructor(etype, new_type)
            # Otherwise replace `etype` with `new_type`
            return new_type

        # Case 2: If etype is a parameterized type, recursively inspect its
        # type arguments and type constructor for updates.
        if isinstance(etype, tp.ParameterizedType):
            new_type_args = [self._update_type(ta, new_type)
                             for ta in etype.type_args]
            new_t_constructor = self._update_type(
                etype.t_constructor, new_type, test_pred)
            return new_t_constructor.new(new_type_args)
        # Case 3: If etype is a type constructor recursively inspect is type
        # parameters for updates.
        if etype.is_type_constructor():
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

        # Case 5: If etype is a wildcard, then update the enclosing bound.
        if is_wildcard and etype.bound:
            etype.bound = self._update_type(etype.bound, new_type, test_pred)
        return etype


def _get_available_types(type_constructor,
                         types, only_regular, primitives=True):
    if not only_regular:
        return types
    available_types = []
    for ptype in types:
        if type_constructor.name == 'Array':
            forbidden_types = (tp.TypeParameter, tp.ParameterizedType,
                               tp.TypeConstructor)
            if isinstance(ptype, forbidden_types):
                continue
        if isinstance(ptype, ast.ClassDeclaration) and (
                ptype.class_type != ast.ClassDeclaration.REGULAR):
            continue
        if isinstance(ptype, tp.TypeConstructor):
            continue
        if not primitives and hasattr(ptype, 'box_type'):
            ptype = ptype.box_type()
        available_types.append(ptype)
    return available_types


def _get_type_arg_variance(t_param, variance_choices):
    if variance_choices is None:
        return tp.Invariant
    can_variant, can_contravariant = variance_choices.get(t_param,
                                                          (True, True))
    covariance = [tp.Covariant] if can_variant else []
    contravariance = [tp.Contravariant] if can_contravariant else []
    if t_param.is_invariant():
        variances = [tp.Invariant] + covariance + contravariance
    elif t_param.is_covariant():
        variances = [tp.Invariant] + covariance
    else:
        variances = [tp.Invariant] + contravariance
    return utils.random.choice(variances)


def instantiate_type_constructor(
        type_constructor: tp.TypeConstructor,
        types: List[tp.Type],
        only_regular=True,
        type_var_map=None,
        variance_choices: Dict[tp.TypeParameter, Tuple[bool, bool]] = None):
    types = _get_available_types(type_constructor,
                                 types, only_regular, primitives=False)
    t_args = []
    type_var_map = dict(type_var_map or {})
    indexes = {}
    for i, t_param in enumerate(type_constructor.type_parameters):
        indexes[t_param] = i
        t = type_var_map.get(t_param)
        if t:
            a_types = [t]
            if t_param.bound and t_param.bound.is_type_var():
                # We must assign the same type argument to the bound of the
                # current type parameter. Example:
                # class A<T1, T2: T1>
                # If assigned the type String to type parameter T1,
                # we need to assign the same type String to the type parameter
                # T2, because T2 <: T1.
                if t.is_wildcard() and t.is_contravariant():
                    # See the comment below, regarding wildcard types.
                    t = t.bound
                    if variance_choices is not None:
                        variance_choices[t_param] = (False, False)
                is_covariant = t.is_wildcard() and t.is_covariant()
                if t_param.is_contravariant() and is_covariant:
                    # See the comment below, regarding wildcard types.
                    t = t.bound
                    if variance_choices is not None:
                        variance_choices[t_param] = (False, False)
                t_args[indexes[t_param.bound]] = t
                type_var_map[t_param.bound] = t
        else:
            a_types = []
            for k, v in type_var_map.items():
                if k.bound == t_param:
                    a_types = [v]
            if not a_types:
                if t_param.bound:
                    if not t_param.bound.is_type_var():
                        # If the type parameter has a bound, then find types
                        # that are subtypes to this bound.
                        a_types = find_subtypes(t_param.bound, types, True)
                        for i, t in enumerate(a_types):
                            if isinstance(t, tp.ParameterizedType):
                                tmp_t = tp.substitute_type_args(
                                    t, type_var_map, cond=lambda t: False)
                                a_types[i] = tmp_t.to_variance_free()
                    else:
                        t_bound = type_var_map[t_param.bound]
                        if t_bound.is_wildcard() and t_bound.is_contravariant():
                            # Here we have the following case:
                            # We have two type parameters X, Y where Y <: X
                            # and we have assigned a contravariant wildcard
                            # type to the type parameter X.
                            # Then, a subtype of this wildcard type is its
                            # lower bound.
                            t_bound = t_bound.bound
                            if variance_choices is not None:
                                variance_choices[t_param] = (False, False)
                        is_covariant = (
                            t_bound.is_wildcard() and t_bound.is_covariant())
                        # Here the variance of the type argument clashes with
                        # the variance of the corresponding parameter. So
                        # we assign the bound of the wildcard.
                        if t_param.is_contravariant() and is_covariant:
                            t_bound = t_bound.bound
                            if variance_choices is not None:
                                variance_choices[t_param] = (False, False)
                        a_types = [t_bound]
                else:
                    a_types = types
        c = utils.random.choice(a_types)
        if isinstance(c, ast.ClassDeclaration):
            cls_type = c.get_type()
        else:
            cls_type = c
        if cls_type.is_type_constructor():
            # We just selected a parameterized class, so we need to instantiate
            # this too. Remove this class from available types to avoid
            # depthy instantiations.
            types = [t for t in types if t != c]
            cls_type, _ = instantiate_type_constructor(
                cls_type, types, True, type_var_map,
                None if variance_choices is None else {}
            )
        variance = _get_type_arg_variance(t_param, variance_choices)
        t_arg = cls_type
        if not variance.is_invariant() and not cls_type.is_wildcard():
            t_arg = tp.WildCardType(cls_type, variance)
        t_args.append(t_arg)
        type_var_map[t_param] = t_arg
    return type_constructor.new(t_args), type_var_map


def choose_type(types: List[tp.Type], only_regular=True):
    # Randomly choose a type from the list of available types.
    types = _get_available_types(types, only_regular)
    c = utils.random.choice(types)
    if isinstance(c, ast.ClassDeclaration):
        cls_type = c.get_type()
    else:
        cls_type = c
    if cls_type.is_type_constructor():
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
        t_param: etype.type_args[i]
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

    if type_a.is_parameterized() and type_b.is_parameterized():
        # FIXME: this is heuristic.
        type_a_wild = type_a.has_wildcards()
        type_b_wild = type_b.has_wildcards()
        have_wildcards = type_a_wild or type_b_wild
        if type_a.t_constructor == type_b.t_constructor and have_wildcards:
            return type_a if type_a_wild else type_b

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
        if decl.get_type().has_type_variables():
            assert isinstance(rec_t, tp.ParameterizedType)
            type_param_map = {
                t_param: rec_t.type_args[i]
                for i, t_param in enumerate(
                    rec_t.t_constructor.type_parameters)
            }
            return tp.substitute_type(decl.get_type(), type_param_map)
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

        if isinstance(expr, ast.Lambda):
            return _return_type_hint(expr.signature)

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

        if isinstance(expr, ast.FunctionReference):
            if expr.receiver is None:
                funcdecl = ctx.get_decl(context, namespace, expr.func)
                if funcdecl is None:
                    return _return_type_hint(None)
                functype = factory.get_function_type(len(funcdecl[1].params))
                return _return_type_hint(funcdecl[1].get_signature(functype))
            # NOTE: not tested
            names.append(expr.func)
            expr = expr.receiver

        if isinstance(expr, ast.Conditional):
            expr1 = expr.true_branch
            expr2 = expr.false_branch

            if isinstance(expr.cond, ast.Is):
                # true branch smart cast
                true_namespace = namespace + ('true_block',)
                false_namespace = namespace + ('false_block',)
                if not expr.cond.operator.is_not:
                    smart_casts.append((expr.cond.lexpr, expr.cond.rexpr))
                    e1_type = get_type_hint(expr1, context, true_namespace,
                                            factory, types,
                                            smart_casts=smart_casts)
                    smart_casts.pop()
                    e2_type = get_type_hint(expr2, context, false_namespace,
                                            factory, types,
                                            smart_casts=smart_casts)
                # false branch smart cast
                else:
                    e1_type = get_type_hint(expr1, context, true_namespace,
                                            factory, types,
                                            smart_casts=smart_casts)
                    smart_casts.append((expr.cond.lexpr, expr.cond.rexpr))
                    e2_type = get_type_hint(expr2, context, false_namespace,
                                            factory, types,
                                            smart_casts=smart_casts)
                    smart_casts.pop()
            else:
                e1_type = get_type_hint(expr1, context, namespace, factory,
                                        types, smart_casts=smart_casts)
                e2_type = get_type_hint(expr2, context, namespace, factory,
                                        types, smart_casts=smart_casts)

            return _return_type_hint(find_lub(
                e1_type, e2_type, types, factory.get_any_type()))

        if isinstance(expr, ast.BottomConstant):
            return _return_type_hint(expr.t)

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


def _update_type_var_map(type_var_map, key, value):
    v = type_var_map.get(key)
    if v and v != value:
        return False
    type_var_map[key] = value
    return True


def unify_types(t1: tp.Type, t2: tp.Type, factory) -> dict:
    """
    This function performs unification on two types. The second type is
    the type we try to match with the first one, by substituting any
    enclosing type variables.

    If the given types are unifiable, this method returns a dict that
    contains the assignments that we need to make to the type variables
    of the second type so that the first and the second type are
    identical.

    Examples:
      unify_types(A<String>, A<T>) = {T: String}
      unify_types(String, T) = {T: String}
      unify_types(A<String, Y>, A<T1, T2) = {T1: String, T2: Y}
      unify_types(A<String>, A<Int>) = {}
      unify_types(A<String, Long>, A<String, T>) = {T: Long}
      unify_types(A<String, Long>, A<Long, T>) = {}
    """
    if type(t1) != type(t2):
        return {}

    is_type_var = isinstance(t1, tp.TypeParameter)
    is_type_var2 = isinstance(t2, tp.TypeParameter)
    if is_type_var and is_type_var2:
        bound1 = t1.get_bound_rec(factory)
        bound2 = t2.get_bound_rec(factory)
        if not bound1 and not bound2:
            return {t2: t1}

        if not bound2 or (bound1 and bound1.is_subtype(bound2)):
            return {t2: t1}

    if not isinstance(t1, tp.ParameterizedType):
        return {}

    if t1.t_constructor != t2.t_constructor:
        return {}

    type_var_map = {}
    for i, t_arg in enumerate(t1.type_args):
        t_arg1 = t_arg
        t_arg2 = t2.type_args[i]

        is_type_var = t_arg2.has_type_variables()

        if not is_type_var:
            if t_arg1 != t_arg2:
                return {}
        else:
            t_var = (
                t_arg2 if isinstance(t_arg2, tp.TypeParameter)
                else None
            )
            if t_var and t_var.bound is not None:
                if t_arg1.is_subtype(t_var.bound):
                    # This means that we found another mapping for the
                    # same type variable and this mapping does not
                    # correspond to t_arg1.
                    if not _update_type_var_map(type_var_map, t_var, t_arg1):
                        return {}
                    continue
                is_parameterized = isinstance(t_var.bound,
                                              tp.ParameterizedType)
                is_parameterized2 = isinstance(t_arg1,
                                               tp.ParameterizedType)
                if is_parameterized and is_parameterized2:
                    res = unify_types(t_arg1, t_var.bound, factory)
                    if not res or any(
                            not _update_type_var_map(type_var_map, k, v)
                            for k, v in res.items()):
                        return {}
                else:
                    return {}
            elif t_var and t_var.bound is None:
                # The same as the above comment.
                if not _update_type_var_map(type_var_map, t_var, t_arg1):
                    return {}
            elif isinstance(t_arg2, tp.ParameterizedType) and (
                  isinstance(t_arg1, tp.ParameterizedType)):
                res = unify_types(t_arg1, t_arg2, factory)
                if not res or any(
                        not _update_type_var_map(type_var_map, k, v)
                        for k, v in res.items()):
                    return {}
            else:
                return {}
    return type_var_map
