class Type(object):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return str(self.name)

    def is_subtype(self, t):
        raise NotImplementedError("You have to implement 'is_subtype()'")

    def supertypes(self):
        """Return all supertypes of a type.
        """
        supertypes = list(self.__class__.mro())
        supertypes.remove(self.__class__)
        supertypes.remove(object)
        return tuple(supertypes)


class Builtin(Type):

    def __str__(self):
        return str(self.name) + "(builtin)"


class Classifier(Type):
    pass


class SimpleClassifier(Classifier):
    def __init__(self, name, supertypes):
        super(SimpleClassifier, self).__init__(name)
        self.supertypes = supertypes

    def __str__(self):
        return self.name + ": " + self.supertypes.join(", ")

    def is_subtype(self, t):
        return any(s.is_subtype(t) for s in self.supertypes)
