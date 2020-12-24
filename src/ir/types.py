from copy import deepcopy
from collections import defaultdict
from typing import List, Set

from src.ir.node import Node


class Type(Node):
    def __init__(self, name):
        self.name = name
        self.supertypes = []

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return self.__str__()

    def is_subtype(self, t):
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

    def not_related(self, t):
        return not(self.is_subtype(t) or t.is_subtype(self))

    def get_name(self):
        return str(self.name)


class AbstractType(Type):
    def is_subtype(self, t):
        raise TypeError("You cannot call 'is_subtype()' in an AbstractType")

    def get_supertypes(self):
        # raise TypeError("You cannot call 'get_supertypes()' in an AbstractType")
        # TODO: revisit
        return super(AbstractType, self).get_supertypes()

    def not_related(self, t):
        raise TypeError("You cannot call 'not_related()' in an AbstractType")


class Builtin(Type):
    """https://kotlinlang.org/spec/type-system.html#built-in-types
    """

    def __init__(self, name: str):
        super(Builtin, self).__init__(name)
        self.supertypes = [self]

    def __str__(self):
        return str(self.name) + "(builtin)"

    def __eq__(self, other: Type):
        """Check if two Builtin objects are of the same Type"""
        return self.__class__ == other.__class__

    def __hash__(self):
        """Hash based on the Type"""
        return hash(str(self.__class__))

    def is_subtype(self, t: Type) -> bool:
        return t == self or t in self.get_supertypes()


class Classifier(Type):
    pass


class Object(Classifier):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "object " + self.name


class SimpleClassifier(Classifier):
    """https://kotlinlang.org/spec/type-system.html#simple-classifier-types
    """

    def __init__(self, name: str, supertypes: List[Type] = [], check=False):
        super(SimpleClassifier, self).__init__(name)
        self.supertypes = supertypes
        if check:
            self._check_supertypes()

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
        return hash(str(self.__class__) + str(self.name) + str(self.supertypes))

    def _check_supertypes(self):
        """The transitive closure of supertypes must be consistent, i.e., does
        not contain two parameterized types with different type arguments.
        """
        tc = defaultdict(list)  # Type Constructors
        for s in filter(lambda x: isinstance(x, ParameterizedType), self.get_supertypes()):
            tc[s.t_constructor] = tc[s.t_constructor] + [s]
        print(tc)
        for t_class in tc.values():
            for p in t_class:
                assert p.type_args == t_class[0].type_args, \
                    "The concrete types of {} do not have the same types".format(
                        t_class[0].t_constructor)

    def is_subtype(self, t: Type) -> bool:
        return t == self or t in self.get_supertypes()


class TypeParameter(AbstractType):
    INVARIANT = 0
    COVARIANT = 1
    CONTRAVARIANT = 2

    def __init__(self, name: str, variance=None, bound: Type = None):
        super(TypeParameter, self).__init__(name)
        self.variance = variance or self.INVARIANT
        self.bound = bound

    def variance_to_string(self):
        if self.variance == 0:
            return ''
        if self.variance == 1:
            return 'out'
        if self.variance == 2:
            return 'in'

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
        return hash(str(self.name) + str(self.variance) + str(self.bound))

    def __str__(self):
        return "{}{}{}".format(
            self.variance_to_string() + ' ' if self.variance != self.INVARIANT else '',
            self.name,
            ': ' + self.bound.get_name() if self.bound is not None else ''
        )


class TypeConstructor(AbstractType):
    def __init__(self, name: str, type_parameters: List[TypeParameter],
                 supertypes: List[Type] = []):
        super(TypeConstructor, self).__init__(name)
        assert len(type_parameters) != 0, "type_parameters is empty"
        self.type_parameters = list(type_parameters)
        self.supertypes = supertypes

    def __str__(self):
        return "{}<{}> {} {}".format(
            self.name,
            ', '.join(map(str, self.type_parameters)),
            ':' if self.supertypes else '',
            ', '.join(map(str, self.supertypes)))

    def __eq__(self, other: AbstractType):
        return (self.__class__ == other.__class__ and
                self.name == other.name and
                self.supertypes == other.supertypes and
                str(self.type_parameters) == str(other.type_parameters))

    def __hash__(self):
        return hash(str(self.__class__) + str(self.name) + str(self.supertypes)
                    + str(self.type_parameters))

    def is_subtype(self, t):
        # TODO revisit
        # from_constructor = isinstance(t, ParameterizedType) and \
        #    t.t_constructor == self
        return t in self.get_supertypes()

    def new(self, type_args: List[Type]):
        return ParameterizedType(self, type_args)


class ParameterizedType(SimpleClassifier):
    def __init__(self, t_constructor: TypeConstructor, type_args: List[Type]):
        self.t_constructor = deepcopy(t_constructor)
        # TODO check bounds
        self.type_args = list(type_args)
        assert len(self.t_constructor.type_parameters) == len(type_args), \
            "You should provide {} types for {}".format(
                len(self.t_constructor.type_parameters), self.t_constructor)
        super(ParameterizedType, self).__init__(self.t_constructor.name,
                                                self.t_constructor.supertypes)

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

    def is_subtype(self, t: Type) -> bool:
        if super(ParameterizedType, self).is_subtype(t):
            return True
        if isinstance(t, ParameterizedType):
            if self.t_constructor == t.t_constructor:
                for tp, sarg, targ in zip(self.t_constructor.type_parameters,
                                          self.type_args, t.type_args):
                    if tp.is_invariant() and sarg != targ:
                        return False
                    elif tp.is_covariant() and not sarg.is_subtype(targ):
                        return False
                    elif tp.is_contravariant() and not targ.is_subtype(sarg):
                        return False
                return True
        return False


class Function(Classifier):
    # FIXME: Represent function as a parameterized type
    def __init__(self, name, param_types, ret_type):
        super(Function, self).__init__(name)
        self.param_types = param_types
        self.ret_type = ret_type

    def __str__(self):
        return self.name + "(" + ','.join(map(str, self.param_types)) +\
            ") -> " + str(self.ret_type)

    def is_subtype(self, t):
        # TODO
        return False

class ParameterizedFunction(Function):
    # FIXME: Represent function as a parameterized type
    def __init__(self, name, type_parameters, param_types, ret_type):
        super(ParameterizedFunction, self).__init__(name, param_types, ret_type)
        self.type_parameters = type_parameters

    def __str__(self):
        return self.name + "<" ','.join(map(str, self.type_parameters)) + ">" + \
            "(" + ','.join(map(str, self.param_types)) +\
            ") -> " + str(self.ret_type)

    def is_subtype(self, t):
        # TODO
        return False
