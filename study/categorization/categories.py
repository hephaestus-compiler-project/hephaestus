class Category():
    name = ""

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.__repr__()


class Subcategory():
    name = ""
    category = None

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.__repr__()


class TypeRelatedBugs(Category):
    """Type-Related Bugs

    Subcategories:
        - Incorrect Type Inference & Substitution
        - Incorrect Type Transformation * Coercion
        - Incorrect Type Comparison & Bound Computation
    """
    name = "Type-related Bugs"


class Inference(Subcategory):
    name = "Incorrect Type Inference & Substitution"
    category = TypeRelatedBugs()


class Approximation(Subcategory):
    name = "Incorrect Type Transformation / Coercion"
    category = TypeRelatedBugs()


class TypeComparison(Subcategory):
    name = "Incorrect Type Comparison & Bound Computation"
    category = TypeRelatedBugs()


class SemanticAnalysisBugs(Category):
    """Semantic Analysis Bugs

    Subcategories:
        - Missing Validation Checks
        - Incorrect Analysis Mechanics
    """
    name = "Semantic Analysis Bugs"


class IncorrectAnalysisMechanics(Subcategory):
    name = "Incorrect Analysis Mechanics"
    category =  SemanticAnalysisBugs()


class MissingValiationChecks(Subcategory): # OtherSemanticChecking Declarations
    name = "Missing Validation Checks"
    category =  SemanticAnalysisBugs()


class ResolutionEnvironment(Category):
    """Resolution & Environment Bugs

    Subcategories:
        - Resolution
        - Environment
    """
    name = "Resolution & Environment Bugs"


class Resolution(Subcategory):
    name = "Resolution"
    category = ResolutionEnvironment()


class Environment(Subcategory):
    name = "Environment"
    category = ResolutionEnvironment()



class ErrorReporting(Category):
    name = "Error Handling & Reporting Bugs"


class Transformation(Category):
    name = "AST Transformation Bugs"
