class RootCause():
    name = ""

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.__repr__()


class RootCauseGeneralCategory():
    name = ""


class LogicError(RootCauseGeneralCategory):
    name = "Logic error"


class AlgorithmicError(RootCauseGeneralCategory):
    name = "Algorithmic error"


class ProgrammingError(RootCauseGeneralCategory):
    name = "Programming error"


class DesignError(RootCauseGeneralCategory):
    name = "Design error"


# Logic Errors
class MissingCase(RootCause):
    """
    The type of the bug is a missing case or a forgotten step in the
    implementation.

    Example:
      See the following fix
      https://github.com/jetbrains/kotlin/commit/76845a76b988bd02d3fcbac1711583006b4dc4d8

      The fix above fixes a bug that lies in the category "Missing Case",
      because it introduces a new step ("DataFlow.checkType") that was omitted
      in the current implementation.
    """
    category = LogicError()
    name = "Missing Case / Forgotten Step"


class IncorrectCondition(RootCause):
    """
    The type of the bug is an incorrect/missing condition in e.g., an if
    statement.

    Example:
       See the following fix
       https://github.com/scala/scala/pull/3828/files

       The fix above fixes a bug that lies in the category "Incorrect Condition",
       because it introduces a condition that is necessary, but was omitted
       in the current implementation.
    """
    category = LogicError()
    name = "Incorrect / Missing Condition"


class ExtraneousComputation(RootCause):
    """
    The type of the bug is an extraneous computation / condition.

    Example:
      See the following fix
      https://github.com/scala/scala/pull/2537

      The fix above fixes a bug that belongs to this category. Specifically,
      the bug is introduced because the implementation performs an
      unnesessary computation (checkPackedConforms).
    """
    category = LogicError()
    name = "Extraneous Computation / Condition"


class IncorrectSequence(RootCause):
    """
    The type of the bug is an incorrect sequence of operations.

    Example:
      See the following fix:
      https://github.com/jetbrains/kotlin/commit/d7dc122298245c94d3d81fefe76ace65206b77f9

      The fix above fixes a bug that belongs to this category. The fix
      rearranges operatins in the correct order.
    """
    category = LogicError()
    name = "Incorrect sequence of operations"


class WrongParams(RootCause):
    """
    There is a bug, because the implementation passes incorrect or
    insufficient parameters to a method.

    Example:
      See the following fix:
      https://github.com/jetbrains/kotlin/commit/2ad93a0330420d38f6022cec95eeddeefba6d2ac

      The fix above fixes a bug that belongs to this category.
      The implementation after the fix calls the method "parseDelimitedFrom()",
      by passing the correct number of arguments.
    """
    category = LogicError()
    name = "Incorrect / Insufficient parameters passed"


# Algorithmic
class IncorrectComputation(RootCause):
    """
    The implementation performs an incorerct computation or uses a wrong
    algorithm.

    Example:
      See the fix:
      https://github.com/jetbrains/kotlin/commit/a906be6dd77ac361f5f6ee4cc8ce84d5129e3021

      The implementation is buggy, because it performs a wrong computation.
      Instead of checking whether the expected type has Nothing? as its lower
      bound, it checks whether the expected type is a subtype of Any?.
    """
    category = AlgorithmicError()
    name = "Incorrect Computation / Wrong Algorithm Used"


class InsufficientAlgorithmImplementation(RootCause):
    """
    The implementation is buggy, because the underlying algorithm is
    insufficient.

    Example:
      See the fix:
      https://github.com/jetbrains/kotlin/commit/deea0643ad3fb68f44cfa2c4697cc80e1fe08dac

      The fix above refines the implementation of the algorithm related to
      type argument resolution.
    """
    category = AlgorithmicError()
    name = "Insufficient Algorithm Implementation"


class AlgorithmImproperlyImplemented(RootCause):
    """
    The algorithm is not implemented correctly or efficiently.

    Example:
      See the fix
      https://github.com/lampepfl/dotty/pull/10271/files

      The current implementation of the algorithm (derivesFrom) has exponential
      complexity and causes a significant degradation performance.
    """
    category = AlgorithmicError()
    name = "Algorithm Improperly Implemented"


# Programming Errors
class IncorrectDataType(RootCause):
    """
    A variable/parameter is declared with an incorrect type.

    Example:
      https://github.com/apache/groovy/pull/1175/files
    """
    category = ProgrammingError()
    name = "Incorrect Data Type"


class WrongDataReference(RootCause):
    """
    The implementation refers to wrong or invalid data (e.g.,
    we have an out-of-bounds array access, etc.).

    Example:
      https://github.com/apache/groovy/pull/600/files
    """
    category = ProgrammingError()
    name = "WrongDataReference"


# Design Issues
class DesignIssue(RootCause):
    """
    The bug is associated with an issue in the design rather than the
    implementation.

    Example:
      The bug below is a design issue
      https://youtrack.jetbrains.com/issue/KT-11280

      The intention of the developers was indeed to perform a smart cast
      when encountering a == condition. However this intention causes problems
      when someone overrides the equals() method as described in the test
      case of the issue.
      Note that there was nothing wrong in the implementation, the design
      of smart casts had the problem.

      Therefore, to fix this issue, the developers changed the design of smart
      casts. In particular, the disabled smart casts when someone overrides
      the equals() method.

    """
    category = DesignError()
    name = "Design Issue"


class FunctionalSpecificationMismatch(RootCause):
    """
    The implementation does not follow the specification of the language.

    Example:
      https://github.com/openjdk/jdk16/pull/72
    """
    category = DesignError()
    name = "Functional Specification Mismatch"
