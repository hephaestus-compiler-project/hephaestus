from copy import deepcopy
from typing import List, Set


class Type(object):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return self.__str__()

    def is_subtype(self, t):
        raise NotImplementedError("You have to implement 'is_subtype()'")

    def get_supertypes(self):
        raise NotImplementedError("You have to implement 'get_supertypes()'")

    def not_related(self, t):
        return not(self.is_subtype(t) or t.is_subtype(self))


class Builtin(Type):
    """https://kotlinlang.org/spec/type-system.html#built-in-types
    """

    def __init__(self, name: str):
        super(Builtin, self).__init__(name)
        self.supertypes = []

    def __str__(self):
        return str(self.name) + "(builtin)"

    def __eq__(self, other: Type):
        """Check if two Builtin objects are of the same Type"""
        return self.__class__ == other.__class__

    def __hash__(self):
        """Hash based on the Type"""
        return hash(str(self.__class__))

    def _dfs(self, t: Type, visited: Set[Type]):
        if t not in visited:
            visited.add(t)
            for supertype in t.get_supertypes(visited):
                if supertype not in visited:
                    self._dfs(supertype, visited)

    def get_supertypes(self, supertypes=set()) -> Set[Type]:
        """Return self and the transitive closure of the supertypes"""
        for supertype in self.supertypes:
            self._dfs(supertype, supertypes)
        return supertypes

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

    def __init__(self, name: str, supertypes: List[Type] = []):
        super(SimpleClassifier, self).__init__(name)
        self.supertypes = supertypes
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
        pc = {}  # Parameterized Classifiers
        for s in filter(lambda x: isinstance(x, ConcreteType), self.get_supertypes()):
            pc[s.p_classifier] = pc.get(s.p_classifier, []) + [s]
        for p_class in pc.values():
            #  We are inside a class, we cannot use scoped objects in a comprehension
            for p in p_class:
                assert p.types == p_class[0].types, \
                    "The concrete types of {} do not have the same types".format(
                        p_class[0].p_classifier)

    def _dfs(self, t: Type, visited: Set[Type]):
        if t not in visited:
            visited.add(t)
            for supertype in t.get_supertypes():
                if supertype not in visited:
                    self._dfs(supertype, visited)

    def get_supertypes(self) -> Set[Type]:
        """Return self and the transitive closure of the supertypes"""
        supertypes = set()
        for supertype in self.supertypes:
            self._dfs(supertype, supertypes)
        return supertypes

    def is_subtype(self, t: Type) -> bool:
        return t == self or t in self.get_supertypes()


class TypeParameter(Type):
    INVARIANT = 0
    COVARIANT = 1
    CONTRAVARIANT = 2

    def __init__(self, name: str, variance=None, bound: Type = None):
        super(TypeParameter, self).__init__(name)
        self.variance = variance or self.INVARIANT
        assert not (self.variance == 0 and bound is not None), \
                "Cannot set bound in invariant type parameter"
        self.bound = bound

    def variance_to_string(self):
        if self.variance == 0:
            return ''
        if self.variance == 1:
            return 'out'
        if self.variance == 2:
            return 'in'

    def __str__(self):
        return "{}{}{}".format(
            self.variance_to_string() + ' ' if self.variance != self.INVARIANT else '',
            self.name,
            ' ' + self.bound if self.bound is not None else ''
        )


class ParameterizedClassifier(SimpleClassifier):
    def __init__(self, name: str, type_parameters: List[TypeParameter],
                 supertypes: List[Type] = []):
        assert len(type_parameters) != 0, "type_parameters is empty"
        self.type_parameters = type_parameters
        super(ParameterizedClassifier, self).__init__(name, supertypes)

    def __str__(self):
        return "{}<{}> {} {}".format(
            self.name,
            ', '.join(map(str, self.type_parameters)),
            ':' if self.supertypes else '',
            ', '.join(map(str, self.supertypes)))

    def __eq__(self, other: Type):
        """Check if two Builtin objects are of the same Type"""
        return (self.__class__ == other.__class__ and
                self.name == other.name and
                self.supertypes == other.supertypes and
                str(self.type_parameters) == str(other.type_parameters))

    def __hash__(self):
        """Hash based on the Type"""
        return hash(str(self.__class__) + str(self.name) + str(self.supertypes)
                    + str(self.type_parameters))


class ConcreteType(SimpleClassifier):
    def __init__(self, p_classifier: ParameterizedClassifier, types: List[Type]):
        #  self.p_classifier = p_classifier
        self.p_classifier = deepcopy(p_classifier)
        # TODO check bounds
        self.types = types
        assert len(self.p_classifier.type_parameters) == len(types), \
                "You should provide {} types for {}".format(
                    len(self.p_classifier.type_parameters), self.p_classifier)
        super(ConcreteType, self).__init__(self.p_classifier.name,
                                           self.p_classifier.supertypes)

    def __eq__(self, other: Type):
        """Check if two Builtin objects are of the same Type"""
        return (self.__class__ == other.__class__ and
                self.name == other.name and
                self.supertypes == other.supertypes and
                self.p_classifier.type_parameters ==
                    other.p_classifier.type_parameters and
                self.types == self.types)

    def __hash__(self):
        """Hash based on the Type"""
        return hash(str(self.__class__) + str(self.name) + str(self.supertypes)
                    + str(self.p_classifier.type_parameters) + str(self.types))

    def __str__(self):
        return "{}<{}>".format(self.name,
                                ", ".join(map(str, self.types)))


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
