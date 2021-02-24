class Category():
    name = ""

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.__repr__()


class Misc(Category):
    name = "Misc"


class TypeExpression(Category):
    name = "Expression Type Checking / Attribution"


class Resolution(Category):
    name = "Resolution-related"


class SubtypingRelated(Category):
    name = "Subtyping-related"


class Inference(Category):
    name = "Inference"


class Approximation(Category):
    # We have a type (e.g. Union Type) and we convert it to a type that can be
    # used in the program
    name = "Approximation / Coercion"


class OtherSemanticChecking(Category):
    name = "Other Semantic Checking"


class Declarations(Category):
    # Note that this category is sub-category of OtherSemanticChecking
    name = "Declaration-related"
