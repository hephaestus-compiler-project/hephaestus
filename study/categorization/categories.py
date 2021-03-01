class Category():
    name = ""

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.__repr__()


class Mechanics(Category):
    """
    The bug is related to the mechanics of a compiler other than those
    mentioned above.

    For example:
      The following bug is related to the deserialization of type aliases
      that takes place during the import of members of another package.
      https://youtrack.jetbrains.com/issue/KT-22728o

    """
    name = "Compiler Mechanics"


class Environment(Category):
    """
    This category contains bugs because they are caused by an incorrect
    environment (e.g., scope, typing context). For example, the environment
    has incorrect/missing entities.

    Example:
      The following bug lies in this category, because the context does
      not contain the 'dummy' symbol.

      https://github.com/scala/scala/pull/4043/files
    """
    name = "Environment"


class TypeExpression(Category):
    """
    The bug is related to the type checking / attribution of an expression.

    Example:
      The follow bug lies in this category because it's part of type checking
      of assignments.

      https://github.com/apache/groovy/commit/55cfaa0ed270afcb1c86bf723bc4a6d9da01447e
    """
    name = "Expression Type Checking / Attribution"


class Resolution(Category):
    """
    Bugs of this category are related to the algorithms for resolving methods
    and fields.

    Example:
      https://bugs.openjdk.java.net/browse/JDK-8195598
    """

    name = "Resolution-related"


class TypeComparison(Category):
    """
    Bugs of this category are related to type comparisons (e.g., checking
    whether a type is subtype of another, checking whether a type is assignable
    to another, etc).

    Example:
      https://github.com/scala/scala/pull/7584
    """
    name = "Type Comparisons (subtyping-, bound-related, etc.)."


class Inference(Category):
    """
    A bug related to type inference (e.g., substitution of a type variable
    with a concrete type).

    Example:
      https://youtrack.jetbrains.com/issue/KT-32081

    """

    name = "Inference"


class Approximation(Category):
    """
    A bug related to type approximations / coercions.
    A compiler internally may approximate or convert a given type to another
    type for various reasons.

    Example:
      https://github.com/lampepfl/dotty/pull/5403
    """
    # We have a type (e.g. Union Type) and we convert it to a type that can be
    # used in the program
    name = "Approximation / Coercion"


class OtherSemanticChecking(Category):
    """
    Other semantic checking performed by the compiler.

    Example:
      https://youtrack.jetbrains.com/issue/KT-4334
    """
    name = "Other Semantic Checking"


class Declarations(Category):
    """
    Note this is a sub-category of 'OtherSemanticChecking' and it's dedicated
    to declarations (e.g., checking whether a class declaration is
    semantically correct, i.e., it does not inherit from itself).

    Example:
    https://youtrack.jetbrains.com/issue/KT-1934
    """
    # Note that this category is sub-category of OtherSemanticChecking
    name = "Declaration-related"
