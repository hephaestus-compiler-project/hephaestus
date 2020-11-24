class Type(object):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return str(self.name)

    def is_subtype(self, t):
        raise NotImplementedError("You have to implement 'is_subtype()'")

    def get_supertypes(self):
        raise NotImplementedError("You have to implement 'get_supertypes()'")


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
        return self.name + ": " + self.supertypes.join(", ")

    def get_supertypes(self):
        return self.supertypes

    def is_subtype(self, t):
        return any(s.is_subtype(t) for s in self.supertypes)
