from collections import OrderedDict
from typing import TypeVar, List, Tuple, Dict

import src.ir.types as tp
import src.ir.context as ctx
import src.ir.builtins as bt
from src.ir import ast
from src import utils


TypeVarMap = TypeVar('TypeVarMap', bound=Dict[tp.TypeParameter, tp.Type])
TypeVarMap.__doc__ = """
A dict from TypeParameter to Type. We use this structure for replacing
type parameters when we want to instantiate type constructors and
parameterized functions.
"""

VarianceChoices = TypeVar('VarianceChoices', bound=Dict[tp.TypeParameter,
                          Tuple[bool, bool]])
VarianceChoices.__doc__ = """
A boolean map that specifies if in place of a TypeParameter we can use
use-site variance. The first value is for covariance
and the second for contravariance.
"""


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
        new_targ, type_var_map = instantiate_type_constructor(
            base_targ.t_constructor, types, only_regular=True,
            type_var_map=type_var_map, disable_variance=True
        )
        return new_targ.to_variance_free()

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
                              type_var_map={},
                              ignore_variance=False):

    bound = None
    if t_param.bound:
        # If the bound of the current type parameter contains other type
        # parameters, substitute it based on the current type assignments
        # of those type parameters.
        bound = tp.substitute_type(t_param.bound, type_var_map)

    if bound and bound.is_parameterized():
        # If bound is `parameterized`, we seek for another type argument that
        # is subtype of the the `new` bound.
        base_targ = _replace_type_argument(base_targ, bound, types,
                                           t_param.bound.has_type_variables())
    # If `base_targ` is None, this means that
    # we cannot find candidate type arguments that satisfy the bound of
    # the corresponding type parameter.
    if not base_targ:
        return None

    if t_param.is_invariant() or ignore_variance:
        t_args = [base_targ]
    elif t_param.is_covariant():
        t_args = _find_types(
            base_targ, types,
            get_subtypes, True, bound, concrete_only=True)
    else:
        t_args = _find_types(
            base_targ, types,
            not get_subtypes, True, bound, concrete_only=True)

    if not base_targ.is_wildcard() or ignore_variance:
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


def _construct_related_types(etype: tp.ParameterizedType, types, get_subtypes,
                             ignore_variance=False):
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
                                               type_var_map,
                                               ignore_variance)
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
                concrete_only=False, ignore_variance=False):

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
        t_set.add(_construct_related_types(
            etype, types, get_subtypes,
            ignore_variance=ignore_variance))
    if include_self:
        t_set.add(etype)
    else:
        t_set.discard(etype)

    if not get_subtypes and bound:
        t_set = {st for st in t_set if st.is_subtype(bound)}
    return [to_type(t, types) for t in t_set] if concrete_only else list(t_set)


def find_subtypes(etype, types, include_self=False, bound=None,
                  concrete_only=False,
                  ignore_variance=False):
    return _find_types(etype, types, get_subtypes=True,
                       include_self=include_self, concrete_only=concrete_only,
                       ignore_variance=ignore_variance)


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
        if type_constructor and type_constructor.name == 'Array':
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
    # import it here to prevent circular dependency
    from src.generators.config import cfg
    if variance_choices is None:
        return tp.Invariant
    can_variant, can_contravariant = variance_choices.get(t_param,
                                                          (True, True))
    if cfg.dis.use_site_variance:
        can_variant, can_contravariant = False, False
    covariance = [tp.Covariant] if can_variant else []
    contravariance = (
        [tp.Contravariant]
        if can_contravariant and not cfg.dis.use_site_contravariance
        else []
    )
    if t_param.is_invariant():
        variances = [tp.Invariant] + covariance + contravariance
    elif t_param.is_covariant():
        variances = [tp.Invariant] + covariance
    else:
        variances = [tp.Invariant] + contravariance
    return utils.random.choice(variances)


def update_type_var_bound_rec(t_param: tp.TypeParameter,
                              t: tp.Type, t_args: list, indexes: list,
                              type_var_map: dict):
    """
    This method recursively updates the type assignment associated with the
    bound of a type variable.

    For example, if we have a type constructor as follows

    A<T1, T2: T1, T3: T2> and the type assignments
    T1 -> String
    T2 -> String

    If we want to update the bound of T3 so that this bound is instantiated
    with `Int` instead of `String`, we call this function to also update
    the type assignment related to the bound of bounds.
    """
    if not (t_param.is_type_var() and t_param.bound is not None):
        # Nothing to update. We don't encounter a type variable with an
        # upper bound.
        return
    bound = t_param.bound
    if not bound.is_type_var():
        return
    try:
        current_t = type_var_map[bound]
        if t.is_subtype(current_t):
            # The current assignment for the type variable corresponding to
            # the upper bound of 't_param' is supertype of 't'. So we don't
            # have to update anything.
            return
        t_args[indexes[bound]] = t
        type_var_map[bound] = t
    except KeyError:
        # This KeyError happens only if a given type parameter has bound
        # corresponding to a type variable of a type constructor. In this
        # case the type variable of the type constructor should be already
        # instantiated with a type that cannot be changed.
        assert bound in type_var_map
    update_type_var_bound_rec(bound, t, t_args, indexes, type_var_map)


def _compute_type_variable_assignments(
        type_parameters: List[tp.TypeParameter],
        types: List[tp.Type],
        type_var_map=None,
        variance_choices: Dict[tp.TypeParameter, Tuple[bool, bool]] = None,
        for_type_constructor=True):
    t_args = []
    type_var_map = dict(type_var_map or {})
    indexes = {}
    for i, t_param in enumerate(type_parameters):
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

                if is_covariant and not for_type_constructor:
                    t = tp.Nothing
                update_type_var_bound_rec(t_param, t, t_args, indexes,
                                          type_var_map)
        else:
            a_types = []
            for k, v in type_var_map.items():
                if k.bound == t_param:
                    a_types = [v]
            if not a_types:
                if t_param.bound:
                    if not t_param.bound.is_type_var():
                        if t_param.bound.has_type_variables():
                            bound = tp.substitute_type(
                                t_param.bound, type_var_map)
                        else:
                            bound = t_param.bound
                        # If the type parameter has a bound, then find types
                        # that are subtypes to this bound.
                        # Note that at this point we ignore use variance
                        # to prevent creating invalid types, e.g.,
                        #  * bound: Foo<X, X>
                        #  * X is assigned to out Number
                        #  * class Bar<X, T extends Foo<X, X>>
                        #  * Prevent creating Bar<out Number, Foo<Long, Number>>
                        a_types = find_subtypes(bound, types, True,
                                                ignore_variance=True)
                        for i, t in enumerate(a_types):
                            if isinstance(t, tp.ParameterizedType):
                                a_types[i] = t.to_variance_free()
                    else:
                        try:
                            t_bound = type_var_map[t_param.bound]
                        except KeyError:
                            # We should never reach here, but just in case.
                            t_bound = None
                            for k, v in type_var_map.items():
                                if k.name == t_param.bound.name:
                                    t_bound = v
                            assert t_bound is not None, (
                                "Cannot find assignment for the bound of "
                                "type parameter " + str(t_param)
                            )

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
                        elif is_covariant and not for_type_constructor:

                            # Here we handle cases like the following
                            # class A<T> {
                            #  fun <X: T> bar(): X
                            # }
                            # A<out String>().bar<String> // wrong
                            # A<out String>().bar<Nothing> // right
                            t_bound = tp.Nothing
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
                None if variance_choices is None else {},
            )
        variance = _get_type_arg_variance(t_param, variance_choices)
        t_arg = cls_type
        if not variance.is_invariant() and not cls_type.is_wildcard():
            t_arg = tp.WildCardType(cls_type, variance)
        t_args.append(t_arg)
        type_var_map[t_param] = t_arg
    return t_args, type_var_map


def instantiate_type_constructor(
        type_constructor: tp.TypeConstructor,
        types: List[tp.Type],
        only_regular=True,
        type_var_map=None,
        variance_choices: Dict[tp.TypeParameter, Tuple[bool, bool]] = None,
        enable_pecs=True,
        disable_variance_functions=False,
        disable_variance=False):
    """Given a type constructor create a parameterized type.

    Note that this function is used for instantiating type parameters of
    both type constructors and parameterized functions. If the parameter
    `for_type_constructor` is True, then this function is used for
    instantiating type constructors.

    Args:
        type_constructor: The type_constructor to use
        types: List of available types
        only_regular: **deprecated** -- always true
        type_var_map: lookup from type variable to type. You should pass
            a type_var_map if you want to instantiate a Parameterized Type
            with specific type arguments.
        variance_choices: a boolean map that specifies if in place of a
            type parameter we can use use-site variance. The first value
            is for covariance and the second for contravariance.
        enable_pecs: Instantiate Function types with the Producer Extends
            Consumer Super attribute.
        disable_variance_functions: Disable variance for Function Types
        disable_variance: Disable variance, it overrides all previous options.
    Returns:
        A ParameterizedType
    """
    if enable_pecs and type_constructor.name.startswith('Function'):
        # Parameters can only be contravariant and return can only be covariant
        # Set parameters
        variance_choices = {
                tparam: (False, True)
                for tparam in type_constructor.type_parameters[:-1]
        }
        # Set return
        variance_choices[type_constructor.type_parameters[-1]] = (True, False)

    if disable_variance or (disable_variance_functions and
            type_constructor.name.startswith('Function')):
        variance_choices = {
                tparam: (False, False)
                for tparam in type_constructor.type_parameters
        }

    types = _get_available_types(type_constructor,
                                 types, only_regular, primitives=False)
    t_args, type_var_map = _compute_type_variable_assignments(
        type_constructor.type_parameters,
        types, type_var_map=type_var_map, variance_choices=variance_choices,
        for_type_constructor=True
    )
    return type_constructor.new(t_args), type_var_map


def instantiate_parameterized_function(
        type_parameters: List[tp.TypeParameter],
        types: List[tp.Type],
        only_regular=True,
        type_var_map=None):
    types = _get_available_types(None, types, only_regular, primitives=False)
    _, type_var_map = _compute_type_variable_assignments(
        type_parameters, types, type_var_map=type_var_map,
        variance_choices=None, for_type_constructor=False,
    )
    return type_var_map


def choose_type(types: List[tp.Type], only_regular=True):
    # Randomly choose a type from the list of available types.
    types = _get_available_types(None, types, only_regular)
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
    types = [c.get_type() for c in classes]
    subtypes = list(find_subtypes(receiver_t, types, include_self=False))
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

    # This list is used to store attribute names and any extra type arguments.
    # These extra type arguments are used if we use an attribute corresponding
    # to a parameterized function. So, we use them to properly instantiate
    # type variables coming from the function's declaration.
    names = []

    def _comp_type(t, name, type_args):
        if t is None:
            return None
        decl = get_decl_from_inheritance(t, name, context)
        if decl is None:
            return None
        decl, rec_t = decl
        if decl.get_type().has_type_variables():
            if rec_t.is_parameterized():
                # Here, the return type can have a type parameter taken
                # from a function.
                type_param_map = rec_t.get_type_variable_assignments()
            else:
                type_param_map = {}
            if isinstance(decl, ast.FunctionDeclaration) and (
                  decl.is_parameterized()):
                type_param_map.update({
                    t_param: type_args[i]
                    for i, t_param in enumerate(decl.type_parameters)
                })
            return tp.substitute_type(decl.get_type(), type_param_map)
        else:
            return decl.get_type()

    def _return_type_hint(t):
        if not names:
            return t
        for name, type_args in reversed(names):
            t = _comp_type(t, name, type_args)
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

        if isinstance(expr, ast.Conditional):
            return _return_type_hint(expr.get_type())

        if isinstance(expr, ast.BottomConstant):
            return _return_type_hint(expr.t)

        if isinstance(expr, ast.FunctionCall):
            if expr.receiver is None:
                funcdecl = ctx.get_decl(context, namespace, expr.func)
                return _return_type_hint(
                    None if funcdecl is None else funcdecl[1].get_type())
            # Beyond function's name, we also pass the type arguments of
            # the function
            names.append((expr.func, expr.type_args or []))
            expr = expr.receiver

        elif isinstance(expr, ast.FunctionReference):
            return expr.signature

        elif isinstance(expr, ast.FieldAccess):
            names.append((expr.field, []))
            expr = expr.expr

        else:
            return factory.get_void_type()


def get_function_reference_type(func_ref, context, namespace,
                                factory, types, smart_casts=[]):
    """Return the signature of a function reference
    """
    func_name = func_ref.func
    receiver = func_ref.receiver
    receiver_type = None
    if receiver:
        receiver_type = get_type_hint(
            receiver, context,
            namespace, factory,
            types, smart_casts=smart_casts
        )
    func_decl = get_func_decl(context, func_name, receiver_type)
    if func_decl:
        function_type = factory.get_function_type(
            len(func_decl.params)
        )
        signature = func_decl.get_signature(function_type)
        if receiver_type:
            type_var_map = get_type_var_map_from_ptype(receiver_type)
            if type_var_map:
                signature = tp.substitute_type(signature, type_var_map)
        return signature
    return None


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


def unify_types(t1: tp.Type, t2: tp.Type, factory,
                same_type=True) -> dict:
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
      unify_types(B(), A<T>) = {T: String}

    For the last example, assume that
      class A<T>
      class B : A<String>()
    """
    if t1.is_combound() and not t1.is_parameterized():
        return t1.unify_types(t2, factory, same_type)

    if same_type and type(t1) != type(t2):
        return {}

    if not same_type and t1.name != t2.name and not t2.is_type_var():
        if not t1.supertypes:
            return {}
        supertype = t1.supertypes[0]
        return unify_types(supertype, t2, factory, same_type=same_type)

    is_type_var = isinstance(t1, tp.TypeParameter)
    is_type_var2 = isinstance(t2, tp.TypeParameter)
    if is_type_var and is_type_var2:
        bound1 = t1.get_bound_rec(factory)
        bound2 = t2.get_bound_rec(factory)
        if not bound1 and not bound2:
            return {t2: t1}

        if not bound2 or (bound1 and bound1.is_subtype(bound2)):
            return {t2: t1}
    if is_type_var2:
        bound = t2.get_bound_rec(factory)
        if bound and not t1.is_subtype(bound):
            return {}
        return {t2: t1}

    if not isinstance(t1, tp.ParameterizedType):
        return {}

    if t1.t_constructor != t2.t_constructor:
        return {}

    type_var_map = {}
    for i, t_arg in enumerate(t1.type_args):
        t_arg1 = t_arg
        t_arg2 = t2.type_args[i]

        if t_arg2.is_wildcard() and not t_arg1.is_wildcard():
            return {}

        if t_arg2.is_wildcard():
            t_arg2 = t_arg2.bound
            t_arg1 = t_arg1.bound

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
                is_parameterized = t_var.bound.is_combound()
                is_parameterized2 = t_arg1.is_combound()
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


def split_type_var_map(type_var_map, cls_type_vars, func_type_vars):
    if type_var_map is None:
        return None, None
    func_type_var_map = {}
    cls_type_var_map = {}
    for type_var, t in type_var_map.items():
        if type_var in func_type_vars:
            func_type_var_map[type_var] = t
        else:
            cls_type_var_map[type_var] = t
    return cls_type_var_map, func_type_var_map


def is_sam(context, etype=None, cls_decl=None):
    def check_decl(cls_decl):
        class_decls = context.get_classes(('global',), glob=True).values()
        callable_funcs = cls_decl.get_callable_functions(class_decls)
        abstract_funcs = cls_decl.get_abstract_functions(class_decls)
        if (cls_decl.class_type != cls_decl.INTERFACE or
                cls_decl.fields or
                len(callable_funcs) > 0 or
                len(abstract_funcs) != 1 or
                (abstract_funcs and
                 any(p.default for p in next(iter(abstract_funcs)).params)) or
                 # We can't use a lambda expression for a functional interface,
                 # if the method in the functional interface has type parameters
                 # https://docs.oracle.com/javase/specs/jls/se8/html/jls-15.html#jls-15.27.3
                 # TODO: check if this is the case for Kotlin.
                 next(iter(abstract_funcs)).is_parameterized() or
                not all(is_sam(context, etype=s) for s in cls_decl.supertypes)):
            return False
        return True

    if etype:
        if isinstance(etype, (tp.SimpleClassifier, tp.ParameterizedType)):
            class_decls = context.get_classes(('global',), glob=True)
            cls_decl = class_decls.get(etype.name, None)
            if not cls_decl:
                return False
            return check_decl(cls_decl)
    elif cls_decl:
        return check_decl(cls_decl)
    return False


def find_sam_fun_signature(context, etype, get_function_type, type_var_map={}):
    def replace_targ(targ, type_var_map):
        if isinstance(targ, (tp.TypeParameter, tp.WildCardType)):
            return type_var_map.get(targ, targ)
        if isinstance(targ, tp.ParameterizedType):
            targ.type_args = [replace_targ(t, type_var_map)
                              for t in targ.type_args]
            return targ
        return targ

    if not is_sam(context, etype=etype):
        return None
    cls_decl = context.get_classes(('global',), glob=True)[etype.name]
    if cls_decl.functions:
        nr_func_params = len(cls_decl.functions[0].params)
        sig = cls_decl.functions[0].get_signature(get_function_type(
            nr_func_params)
        )
        if isinstance(sig, tp.ParameterizedType):
            sig.type_args = [replace_targ(targ, type_var_map)
                             for targ in sig.type_args]
        return sig
    if cls_decl.supertypes:
        return find_sam_fun_signature(context, cls_decl.supertypes[0],
                                      get_function_type)
    return None


def get_superclass_decl(super_cls, class_decls):
    class_decl = None
    for c in class_decls:
        if isinstance(super_cls.class_type, tp.ParameterizedType):
            if super_cls.class_type.t_constructor == c.get_type():
                class_decl = c
        else:
            if super_cls.class_type == c.get_type():
                class_decl = c
    return class_decl


def get_superclass_type_var_map(super_cls, class_decl):
    if class_decl.is_parameterized():
        return {
            t_param: super_cls.class_type.type_args[i]
            for i, t_param in enumerate(class_decl.type_parameters)
        }
    return {}


def get_type_var_map_from_ptype(ptype, type_var_map=None):
    """Get the type variable map from a parameterized type.
    """
    type_var_map = {} if type_var_map is None else type_var_map
    if not isinstance(ptype, tp.ParameterizedType):
        return type_var_map
    for tparam, targ in zip(ptype.t_constructor.type_parameters,
                            ptype.type_args):
        # We don't want to override type parameters that already in the lookup
        if tparam not in type_var_map:
            type_var_map[tparam] = targ
    # Now we have to look in the superclass hierarchy
    if ptype.t_constructor.supertypes:
        for stype in ptype.t_constructor.supertypes:
            get_type_var_map_from_ptype(stype, type_var_map)
    return type_var_map


def get_func_decl(context, name: str, receiver: tp.Type=None):
    """Get the correct function declaration.

    We should take into consideration any given receiver due to override and
    inheritance.

    Args:
        context: The context of the program
        name: The name of the function
        receiver_type: The type of the receiver (you can compute it using
            get_type_hint)

    Returns:
        ast.FunctionDeclaration
    """
    # If there isn't a receiver we look into global functions
    if receiver is None:
        return context.get_funcs(('global',)).get(name, None)

    funcs = context.get_namespaces_decls(('global',), name, 'funcs', glob=True)

    if len(funcs) == 0:
        return None

    if len(funcs) == 1:
        func = list(funcs)[0]
        return func[1]

    # Receiver type not in context
    if not hasattr(receiver, 'name'):
        return None

    for func in funcs:
        if func[0][-2] == receiver.name:
            return func[1]

    return None


def build_type_variable_dependencies(t1: tp.Type, t2: tp.Type):
    """
    This function build a graph that shows the type variable dependencies
    between two types. These types need to have parent-child relationships
    so that they have dependent type variables. Otherwise, the types don't
    have any type variable dependency.

    For example:
        class A<T>
        class B<T>: A<T>()

    In this example, the type variable of Foo depends on the type variable of
    Bar, as we pass Bar.T as type argument during the type constructor
    instantiation at B<T>: A<T>().

    So in this example:
        * `build_type_variable_dependencies(B<T>, A<T>)` == {
              "Foo": ["Foo.T"],
              "Bar": ["Bar.T"],
              "Foo.T": ["Bar.T"]
           }

    Note that the order we pass the arguments of this function is important.
    So, `build_type_variable_dependencies(A<T>, B<T>)` == {}, as A<T>
    is not a subtype of B<T>.
    """
    def _get_supertypes(t):
        if t.is_parameterized():
            return t.t_constructor.supertypes
        return t.supertypes

    def _to_type_var_id(type_con, type_var):
        return type_con.name + "." + type_var.name

    # The given types are the same (or they come from the same type
    # constructor), so there is no a type variable dependency.
    if t1.name == t2.name:
        return {}

    # The given types are not parameterized, so there is no any type variable
    # dependency between them.
    if not t1.is_parameterized() and not t2.is_parameterized():
        return {}

    type_deps = {}
    if t1.is_parameterized():
        type_deps = {
            t1.name: [_to_type_var_id(t1, t_param)
                      for t_param in t1.t_constructor.type_parameters]
        }

    if t2.is_parameterized():
        type_deps[t2.name] = [_to_type_var_id(t2, t_param)
                              for t_param in t2.t_constructor.type_parameters]
    supertypes = _get_supertypes(t1)
    parent = t1
    while supertypes:
        st = supertypes[0]
        if st.is_parameterized():
            type_deps.update({
                st.name: [_to_type_var_id(st, t_param)
                          for t_param in st.t_constructor.type_parameters]
            })
            type_var_map = {
                _to_type_var_id(st, t_param): [
                    _to_type_var_id(parent, st.type_args[i])
                ] for i, t_param in enumerate(st.t_constructor.type_parameters)
                if st.type_args[i].is_type_var()
            }
            type_deps.update(type_var_map)
        if st.name == t2.name:
            supertypes = []
        else:
            parent = st
            supertypes = _get_supertypes(st)
    return type_deps
