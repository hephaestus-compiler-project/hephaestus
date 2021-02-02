# pylint: disable=abstract-method
from __future__ import annotations
from copy import deepcopy
from collections import defaultdict
from typing import List

from src.ir.node import Node


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
    pass


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
    INVARIANT = 0
    COVARIANT = 1
    CONTRAVARIANT = 2

    def __init__(self, name: str, variance=None, bound: Type = None):
        super().__init__(name)
        self.variance = variance or self.INVARIANT
        self.bound = bound

    def variance_to_string(self):
        if self.variance == 1:
            return 'out'
        if self.variance == 2:
            return 'in'
        return ''

    def is_covariant(self):
        return self.variance == 1

    def is_contravariant(self):
        return self.variance == 2

    def is_invariant(self):
        return self.variance == 0

    def children(self):
        return []

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
            ' ' if self.variance != self.INVARIANT else '',
            self.name,
            ': ' + self.bound.get_name() if self.bound is not None else ''
        )


def _get_type_substitution(etype, type_map):
    if isinstance(etype, ParameterizedType):
        return substitute_type_args(etype, type_map)
    t = type_map.get(etype)
    if t is None or t.has_type_variables():
        # The type parameter does not correspond to an abstract type
        # so, there is nothing to substitute.
        return etype
    return t


def substitute_type_args(etype, type_map):
    assert isinstance(etype, ParameterizedType)
    type_args = []
    for t_arg in etype.type_args:
        type_args.append(_get_type_substitution(t_arg, type_map))
    new_type_map = {
        tp: type_args[i]
        for i, tp in enumerate(etype.t_constructor.type_parameters)
    }
    type_con = perform_type_substitution(
        etype.t_constructor, new_type_map)
    return ParameterizedType(type_con, type_args)


def perform_type_substitution(etype, type_map):
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

        new_bound = _get_type_substitution(t_param.bound, type_map)
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

    def new(self, type_args: List[Type]):
        type_map = {tp: type_args[i]
                    for i, tp in enumerate(self.type_parameters)}
        type_con = perform_type_substitution(self, type_map)
        return ParameterizedType(type_con, type_args)


class ParameterizedType(SimpleClassifier):
    def __init__(self, t_constructor: TypeConstructor, type_args: List[Type],
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
                    if tp.is_invariant() and sarg != targ:
                        return False
                    if tp.is_covariant() and not sarg.is_subtype(targ):
                        return False
                    if tp.is_contravariant() and not targ.is_subtype(sarg):
                        return False
                return True
        return False


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
