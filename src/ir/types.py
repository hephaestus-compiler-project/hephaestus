# pylint: disable=abstract-method
from __future__ import annotations
from copy import deepcopy
from collections import defaultdict
from typing import List, Dict, Set

from src.ir.node import Node


class Variance(object):
    INVARIANT = 0
    COVARIANT = 1
    CONTRAVARIANT = 2

    def __init__(self, value):
        self.value = value

    def variance_to_str(self):
        if self.value == 1:
            return 'out'
        if self.value == 2:
            return 'in'
        return ''

    def is_covariant(self):
        return self.value == 1

    def is_contravariant(self):
        return self.value == 2

    def is_invariant(self):
        return self.value == 0

    def __hash__(self):
        return hash(str(self.value))

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.value == other.value
        )


Invariant = Variance(Variance.INVARIANT)
Covariant = Variance(Variance.COVARIANT)
Contravariant = Variance(Variance.CONTRAVARIANT)


class Type(Node):
    def __init__(self, name):
        self.name = name
        self.supertypes = []

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return self.__str__()

    def has_type_variables(self):
        raise NotImplementedError("You have to implement has_type_variables()")

    def is_subtype(self, other: Type):
        raise NotImplementedError("You have to implement 'is_subtype()'")

    def to_type_arg(self, variance=Invariant):
        if isinstance(self, TypeArgument):
            return self
        return TypeArgument(self, variance=variance)

    def to_type(self):
        if isinstance(self, TypeArgument):
            return self.concrete_type
        return self

    def is_assignable(self, other: Type):
        """
        Checks of a value of the current type is assignable to 'other' type.

        By default, the current type should be subtype of the other type.
        However, this is not always the case, e.g., in Groovy / Java,
        a value of type Short can be assigned to a value of type Integer,
        but Short is not subtype of Integer.
        """
        return self.is_subtype(other)

    def is_primitive(self):
        raise NotImplementedError("You have to implement 'is_primitive()'")

    def get_supertypes(self):
        """Return self and the transitive closure of the supertypes"""
        stack = [self]
        visited = {self}
        while stack:
            source = stack.pop()
            for supertype in source.supertypes:
                if supertype not in visited:
                    visited.add(supertype)
                    stack.append(supertype)
        return visited

    def not_related(self, other: Type):
        return not(self.is_subtype(other) or other.is_subtype(self))

    def get_name(self):
        return str(self.name)


class AbstractType(Type):
    def is_subtype(self, other):
        raise TypeError("You cannot call 'is_subtype()' in an AbstractType")

    def get_supertypes(self):
        # TODO: revisit
        return super().get_supertypes()

    def has_type_variables(self):
        return True

    def not_related(self, other):
        raise TypeError("You cannot call 'not_related()' in an AbstractType")

    def is_primitive(self):
        return False


class Builtin(Type):
    """https://kotlinlang.org/spec/type-system.html#built-in-types
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.supertypes = [self]

    def has_type_variables(self):
        return False

    def __str__(self):
        return str(self.name) + "(builtin)"

    def __eq__(self, other: Type):
        """Check if two Builtin objects are of the same Type"""
        return self.__class__ == other.__class__

    def __hash__(self):
        """Hash based on the Type"""
        return hash(str(self.__class__))

    def is_subtype(self, other: Type) -> bool:
        return other == self or other in self.get_supertypes()

    def get_builtin_type(self):
        raise NotImplementedError("You have to implement get_builtin_type")


class Classifier(Type):
    def is_primitive(self):
        return False


class Object(Classifier):

    def __str__(self):
        return "object " + self.name


class SimpleClassifier(Classifier):
    """https://kotlinlang.org/spec/type-system.html#simple-classifier-types
    """

    def __init__(self, name: str, supertypes: List[Type] = None, check=False):
        super().__init__(name)
        self.supertypes = supertypes if supertypes is not None else []
        if check:
            self._check_supertypes()

    def has_type_variables(self):
        return False

    def __str__(self):
        return "{}{}".format(
            self.name,
            '' if not self.supertypes else ": (" +
            ', '.join(map(str, self.supertypes)) + ")"
        )

    def __eq__(self, other: Type):
        """Check if two Builtin objects are of the same Type"""
        return (self.__class__ == other.__class__ and
                self.name == other.name and
                self.supertypes == other.supertypes)

    def __hash__(self):
        """Hash based on the Type"""
        return hash("{}{}{}".format(
            str(self.__class__), str(self.name), str(self.supertypes)))

    def _check_supertypes(self):
        """The transitive closure of supertypes must be consistent, i.e., does
        not contain two parameterized types with different type arguments.
        """
        tconst = defaultdict(list)  # Type Constructors
        for supertype in filter(
                lambda x: isinstance(x, ParameterizedType),
                self.get_supertypes()):
            tconst[supertype.t_constructor] = \
                tconst[supertype.t_constructor] + [supertype]
        for t_class in tconst.values():
            for ptype in t_class:
                assert ptype.type_args == t_class[0].type_args, \
                    "The concrete types of " + \
                    str(t_class[0].t_constructor) + " " + \
                    "do not have the same types"

    def is_subtype(self, other: Type) -> bool:
        supertypes = self.get_supertypes()
        # Since the subtyping relation is transitive, we must also check
        # whether any supertype of the current type is also subtype of the
        # given type.
        return other == self or any(
            st.is_subtype(other) for st in supertypes
            if st != self
        )


class TypeParameter(AbstractType):

    def __init__(self, name: str, variance=None, bound: Type = None):
        super().__init__(name)
        self.variance = variance or Invariant
        self.bound = bound

    def variance_to_string(self):
        return self.variance.variance_to_str()

    def is_covariant(self):
        return self.variance.is_covariant()

    def is_contravariant(self):
        return self.variance.is_contravariant()

    def is_invariant(self):
        return self.variance.is_invariant()

    def children(self):
        return []

    def get_bound_rec(self, factory):
        if not self.bound:
            return None
        t = self.bound
        if isinstance(t, TypeParameter):
            return t.get_bound_rec(factory)
        if not t.has_type_variables():
            return t
        return t.to_type_variable_free(factory)

    def is_subtype(self, other):
        if not self.bound:
            return False
        return self.bound == other

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.name == other.name and
                self.variance == other.variance and
                self.bound == other.bound)

    def __hash__(self):
        return hash(str(self.name) + str(self.variance))

    def __str__(self):
        return "{}{}{}".format(
            self.variance_to_string() +
            ' ' if self.variance != Invariant else '',
            self.name,
            ': ' + self.bound.get_name() if self.bound is not None else ''
        )


def _get_type_substitution(etype, type_map,
                           cond=lambda t: t.has_type_variables()):
    if isinstance(etype, ParameterizedType):
        return substitute_type_args(etype, type_map, cond)
    t = type_map.get(etype)
    if t is None or cond(t):
        # The type parameter does not correspond to an abstract type
        # so, there is nothing to substitute.
        return etype
    return t


def substitute_type_args(etype, type_map,
                         cond=lambda t: t.has_type_variables()):
    assert isinstance(etype, ParameterizedType)
    type_args = []
    for t_arg in etype.type_args:
        type_args.append(_get_type_substitution(
            t_arg.to_type(), type_map, cond).to_type_arg(t_arg.variance))
    new_type_map = {
        tp: type_args[i]
        for i, tp in enumerate(etype.t_constructor.type_parameters)
    }
    print(etype, etype.t_constructor, type_map, new_type_map)
    type_con = perform_type_substitution(
        etype.t_constructor, new_type_map, cond)
    return ParameterizedType(type_con, type_args)


def substitute_type(t, type_map):
    # TODO: revisit argument 'cond'
    return _get_type_substitution(t, type_map, lambda t: False)


def perform_type_substitution(etype, type_map,
                              cond=lambda t: t.has_type_variables()):
    # This function performs the following substitution.
    # Imagine that we have the following case.
    #
    # class Y<T>
    # class X<T>: Y<T>()
    #
    # When, we instantiate the type constructor X with a specific type
    # argument (e.g., String), we must also substitute the type parameter
    # of its supertype (i.e., Y<T>) with the given type argument.
    # For example, the supertype of X<String> is Y<String> and not Y<T>.
    #
    # This also works for nested definitions. For example
    # class X<T> : Y<Z<T>>()
    supertypes = []
    for t in etype.supertypes:
        if isinstance(t, ParameterizedType):
            supertypes.append(substitute_type_args(t, type_map))
        else:
            supertypes.append(t)
    type_params = []
    for t_param in etype.type_parameters:
        if t_param.bound is None:
            type_params.append(t_param)
            continue

        # TODO: revisit
        new_bound = t_param.bound
        t_param = TypeParameter(t_param.name, t_param.variance, new_bound)
        type_params.append(t_param)

    etype = deepcopy(etype)
    etype.type_parameters = type_params
    etype.supertypes = supertypes
    return etype


class TypeConstructor(AbstractType):
    def __init__(self, name: str, type_parameters: List[TypeParameter],
                 supertypes: List[Type] = None):
        super().__init__(name)
        assert len(type_parameters) != 0, "type_parameters is empty"
        self.type_parameters = list(type_parameters)
        self.supertypes = supertypes if supertypes is not None else []

    def __str__(self):
        return "{}<{}> {} {}".format(
            self.name,
            ', '.join(map(str, self.type_parameters)),
            ':' if self.supertypes else '',
            ', '.join(map(str, self.supertypes)))

    def __eq__(self, other: AbstractType):
        return (self.__class__ == other.__class__ and
                self.name == other.name and
                # TODO Revisit self.supertypes == other.supertypes and
                str(self.type_parameters) == str(other.type_parameters))

    def __hash__(self):
        return hash(str(self.__class__) + str(self.name) + str(self.supertypes)
                    + str(self.type_parameters))

    def is_subtype(self, other: Type):
        # TODO revisit
        # from_constructor = isinstance(t, ParameterizedType) and \
        #    t.t_constructor == self
        return other in self.get_supertypes()

    def new(self, type_args: List[TypeArgument]):
        type_map = {tp: type_args[i]
                    for i, tp in enumerate(self.type_parameters)}
        type_con = perform_type_substitution(self, type_map)
        # If any of the provided type arguments is not an instance of
        # TypeArgument class, then implicitly convert to a type argument
        # with the default variance (i.e., invariant).
        new_type_args = [t.to_type_arg() for t in type_args]
        return ParameterizedType(type_con, new_type_args)


class TypeArgument(Classifier):
    def __init__(self, concrete_type: Type, variance=Invariant):
        super().__init__(concrete_type.name)
        assert not isinstance(concrete_type, TypeArgument), (
            "The enclosing type of a type argument cannot be a type argument")
        self.concrete_type = concrete_type
        self.variance = variance

    def has_type_variables(self):
        return self.concrete_type.has_type_variables()

    def is_covariant(self):
        return self.variance.is_covariant()

    def is_contravariant(self):
        return self.variance.is_contravariant()

    def is_invariant(self):
        return self.variance.is_invariant()

    def to_type(self):
        return self.concrete_type

    def _is_subtype_type_arg(self, other: Type):
        if self.is_invariant():
            if other.is_invariant():
                return self.concrete_type == other.concrete_type
            elif other.is_covariant():
                return self.concrete_type.is_subtype(other.concrete_type)
            else:
                return other.concrete_type.is_subtype(self.concrete_type)
        elif self.is_covariant():
            if other.is_invariant() or other.is_contravariant():
                return False
            else:
                return self.concrete_type.is_subtype(other.concrete_type)
        else:
            if other.is_invariant() or other.is_covariant():
                return False
            return other.concrete_type.is_subtype(self.concrete_type)

    def is_subtype(self, other: Type):
        if isinstance(other, TypeArgument):
            return self._is_subtype_type_arg(other)
        if self.is_invariant():
            return self.concrete_type == other
        elif self.is_covariant():
            return self.concrete_type.is_subtype(other)
        else:
            return other.is_subtype(self.concrete_type)

    def __str__(self):
        if self.variance == Invariant:
            return str(self.concrete_type)
        else:
            return self.variance.variance_to_str() + " " + str(
                self.concrete_type)

    def __hash__(self):
        return hash(str(self.concrete_type) + str(self.variance))

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.concrete_type == other.concrete_type and
            self.variance == other.variance
        )


class ParameterizedType(SimpleClassifier):
    def __init__(self, t_constructor: TypeConstructor,
                 type_args: List[TypeArgument],
                 can_infer_type_args=False):
        self.t_constructor = deepcopy(t_constructor)
        # TODO check bounds
        self.type_args = list(type_args)
        assert len(self.t_constructor.type_parameters) == len(type_args), \
            "You should provide {} types for {}".format(
                len(self.t_constructor.type_parameters), self.t_constructor)
        self._can_infer_type_args = can_infer_type_args
        super().__init__(self.t_constructor.name,
                         self.t_constructor.supertypes)

    def has_type_variables(self):
        return any(t_arg.has_type_variables() for t_arg in self.type_args)

    def to_variance_free(self):
        type_args = []
        for t_arg in self.type_args:
            type_args.append(t_arg.to_type().to_type_arg())
        return self.t_constructor.new(type_args)

    def to_type_variable_free(self, factory):
        # We translate a parameterized type that contains
        # type variables into a parameterized type that is
        # type variable free.
        type_args = []
        for t_arg in self.type_args:
            if isinstance(t_arg.to_type(), TypeParameter):
                bound = t_arg.to_type().get_bound_rec(factory)
                if bound is None:
                    # If the type variable has no bound, then create
                    # a variant type argument on the top type.
                    # X<T> => X<? extends Object>
                    type_args.append(
                        factory.get_any_type().to_type_arg(Covariant))
                else:
                    # Get the bound of type variable and create variant type
                    # argument based on its bound, e.g.,
                    # T <: Number, X<T> => X<? extends Number>
                    type_args.append(bound.to_type_arg(Covariant))
            elif isinstance(t_arg.to_type(), ParameterizedType):
                type_args.append(
                    t_arg.to_type().to_type_variable_free(
                        factory).to_type_arg())
            else:
                type_args.append(t_arg)
        return self.t_constructor.new(type_args)

    def get_type_variables(self, factory) -> Dict[TypeParameter, Set[Type]]:
        # This function actually returns a dict of the enclosing type variables
        # along with the set of their bounds.
        type_vars = defaultdict(set)
        for i, t_arg in enumerate(self.type_args):
            t_arg = t_arg.to_type()
            if isinstance(t_arg, TypeParameter):
                type_vars[t_arg].add(
                    t_arg.get_bound_rec(factory))
            elif isinstance(t_arg, ParameterizedType):
                for k, v in t_arg.get_type_variables(factory).items():
                    type_vars[k].update(v)
            else:
                continue
        return type_vars

    @property
    def can_infer_type_args(self):
        return self._can_infer_type_args

    @can_infer_type_args.setter
    def can_infer_type_args(self, value):
        if not isinstance(value, bool):
            raise TypeError("Must be bool")
        self._can_infer_type_args = value

    def __eq__(self, other: Type):
        if not isinstance(other, ParameterizedType):
            return False
        return (self.name == other.name and
                self.supertypes == other.supertypes and
                self.t_constructor.__class__ == other.t_constructor.__class__ and
                self.t_constructor.type_parameters ==
                other.t_constructor.type_parameters and
                self.type_args == other.type_args)

    def __hash__(self):
        return hash(str(self.name) + str(self.supertypes) + str(self.type_args)
                    + str(self.t_constructor.type_parameters))

    def __str__(self):
        return "{}<{}>".format(self.name,
                               ", ".join(map(str, self.type_args)))

    def get_name(self):
        return "{}<{}>".format(self.name, ", ".join([t.get_name()
                                                     for t in self.type_args]))

    def is_subtype(self, other: Type) -> bool:
        if super().is_subtype(other):
            return True
        if isinstance(other, ParameterizedType):
            if self.t_constructor == other.t_constructor:
                for tp, sarg, targ in zip(self.t_constructor.type_parameters,
                                          self.type_args, other.type_args):
                    if tp.is_invariant() and not sarg.is_subtype(targ):
                        return False
                    if tp.is_covariant() and not sarg.concrete_type.is_subtype(
                            targ.concrete_type):
                        return False
                    if tp.is_contravariant() and (
                            not targ.concrete_type.is_subtype(
                                sarg.concrete_type)):
                        return False
                return True
        return False

    def is_assignable(self, other: Type):
        # Import here to prevent circular dependency.
        from src.ir import java_types as jt
        # We should handle Java primitive arrays
        # In Java Byte[] is not assignable to byte[] and vice versa.
        if (self.t_constructor == jt.Array and
                isinstance(other, ParameterizedType) and
                other.t_constructor == jt.Array):
            self_t = self.type_args[0].to_type()
            other_t = other.type_args[0].to_type()
            self_is_primitive = getattr(self_t, 'primitive', False)
            other_is_primitive = getattr(other_t, 'primitive', False)
            if self_is_primitive or other_is_primitive:
                if (self_t == other_t and
                        self_is_primitive and other_is_primitive):
                    return True
                return False
        return self.is_subtype(other)


class Function(Classifier):
    # FIXME: Represent function as a parameterized type
    def __init__(self, name, param_types, ret_type):
        super().__init__(name)
        self.param_types = param_types
        self.ret_type = ret_type

    def __str__(self):
        return self.name + "(" + ','.join(map(str, self.param_types)) +\
            ") -> " + str(self.ret_type)

    def is_subtype(self, other: Type):
        # TODO
        return False


class ParameterizedFunction(Function):
    # FIXME: Represent function as a parameterized type
    def __init__(self, name, type_parameters, param_types, ret_type):
        super().__init__(name, param_types, ret_type)
        self.type_parameters = type_parameters

    def __str__(self):
        return self.name + "<" ','.join(map(str, self.type_parameters)) + \
            ">" + "(" + ','.join(map(str, self.param_types)) + \
            ") -> " + str(self.ret_type)

    def is_subtype(self, other: Type):
        # TODO
        return False
