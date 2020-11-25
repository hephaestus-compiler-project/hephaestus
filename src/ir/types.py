class Type(object):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return str(self.name)

    def is_subtype(self, t):
        raise NotImplementedError("You have to implement 'is_subtype()'")

    def get_supertypes(self):
        raise NotImplementedError("You have to implement 'get_supertypes()'")

    def not_related(self, t):
        return not(self.is_subtype(t) or t.is_subtype(self))


class Builtin(Type):

    def __str__(self):
        return str(self.name) + "(builtin)"

    def is_subtype(self, t):
        return t.__class__ in self.get_supertypes()

    def get_supertypes(self):
        supertypes = list(self.__class__.mro())
        supertypes.remove(object)
        supertypes.remove(Type)
        supertypes.remove(Builtin)
        return tuple(supertypes)


class Classifier(Type):
    pass


class SimpleClassifier(Classifier):
    def __init__(self, name, supertypes):
        super(SimpleClassifier, self).__init__(name)
        self.supertypes = supertypes

    def __str__(self):
        print(self.supertypes)
        return self.name + ": " + ', '.join(map(str, self.supertypes))

    def get_supertypes(self):
        return self.supertypes

    def is_subtype(self, t):
        return any(s.is_subtype(t) for s in self.supertypes)


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
