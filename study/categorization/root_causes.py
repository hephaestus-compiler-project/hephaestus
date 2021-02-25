class RootCause():
    name = ""

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.__repr__()


# Logic Errors
class MissingCase(RootCause):
    name = "Missing Case / Forgotten Step"


class MissingMethod(RootCause):
    name = "Missing Method"


class IncorrectCondition(RootCause):
    name = "Incorrect / Missing Condition"


class ExtraneousComputation(RootCause):
    name = "Extraneous Computation / Condition"


class ExtremeConditionNeglected(RootCause):
    name = "Extreme Condition Neglected"


class IncorrectSequence(RootCause):
    name = "Incorrect sequence of operations"


class WrongParams(RootCause):
    name = "Incorrect / Insufficient parameters passed"


# Algorithmic
class IncorrectComputation(RootCause):
    name = "Incorrect Computation / Wrong Algorithm Used"


class InsufficientFunctionality(RootCause):
    name = "Insufficient Functionality"


class AlgorithmImproperlyImplemented(RootCause):
    name = "Algorithm Improperly Implemented"


# Programming Errors
class IncorrectDataType(RootCause):
    name = "Incorrect Data Type"


class WrongDataReference(RootCause):
    name = "WrongDataReference"


# Design Issues
class DesignIssue(RootCause):
    name = "Design Issue"


class FunctionalSpecificationMismatch(RootCause):
    name = "Functional Specification Mismatch"
