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
        return hash(self.__class__)

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
        return t in self.get_supertypes()


class Classifier(Type):
    pass


class Object(Classifier):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "object " + self.name


class SimpleClassifier(Classifier):
    def __init__(self, name, supertypes):
        super(SimpleClassifier, self).__init__(name)
        # TODO: the transitive closure of supertypes must be
        # consistent, i.e. does not contain two parameterized types with
        # different type arguments.
        self.supertypes = supertypes

    def __str__(self):
        return "{}{}".format(
            self.name,
            '' if not self.supertypes else ": (" +
            ', '.join(map(str, self.supertypes)) + ")"
        )

    def _dfs(self, t: Type, visited: Set[Type]):
        if t not in visited:
            visited.add(t)
            for supertype in t.get_supertypes(visited):
                if supertype not in visited:
                    self._dfs(supertype, visited)

    def get_supertypes(self, supertypes=set()) -> Set[Type]:
        """Return self and the transitive closure of the supertypes"""
        for supertype in [self] + self.supertypes:
            self._dfs(supertype, supertypes)
        return supertypes

    def is_subtype(self, t: Type) -> bool:
        return t in self.get_supertypes()


class ParameterizedClassifier(SimpleClassifier):
    def __init__(self, name, type_parameters, supertypes):
        assert len(type_parameters) != 0, "type_parameters is empty"
        super(ParameterizedClassifier, self).__init__(name, supertypes)
        self.type_parameters = type_parameters

    def __str__(self):
        return "{}<{}> {} {}".format(
            self.name,
            ', '.join(map(str, self.type_parameters)),
            ':' if self.supertypes else '',
            ', '.join(map(str, self.supertypes)))


class ConcreteType(Type):
    """Usually produce by ParameterizedClassifier
    """
    def __init__(self, name, types):
        super(ConcreteType, self).__init__(name)
        self.types = types

    def __str__(self):
        return "{} <{}>".format(self.name,
                                ", ".join(map(str, self.types)))


class TypeParameter(Type):
    INVARIANT = 0
    COVARIANT = 1
    CONTRAVARIANT = 2

    def __init__(self, name, variance=None, bound=None):
        super(TypeParameter, self).__init__(name)
        self.variance = variance or self.INVARIANT
        assert not (self.variance == 0 and bound is not None), "Cannot set bound in invariant type parameter"
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
