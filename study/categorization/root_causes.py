class RootCause():
    name = ""

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.__repr__()


class MissingCase(RootCause):
    name = "Missing Case / Forgotten Step"


class IncorrectComputation(RootCause):
    name = "Incorrect Computation / Wrong Algorithm Used"


class IncorrectCondition(RootCause):
    name = "Incorrect / Missing Condition"


class ExtraneousComputation(RootCause):
    name = "Extraneous Computation / Condition"


class WrongParams(RootCause):
    name = "Incorrect / Insufficient parameters passed"


class InsufficientFunctionality(RootCause):
    name = "Insufficient Functionality"


class IncorrectSequence(RootCause):
    name = "Incorrect sequence of operations"


class IncorrectDataType(RootCause):
    name = "Incorrect Data Type"


class WrongDataReference(RootCause):
    name = "WrongDataReference"


class DesignIssue(RootCause):
    name = "Design Issue"


class ExtremeConditionNeglected(RootCause):
    name = "Extreme Condition Neglected"


class FunctionalSpecificationMismatch(RootCause):
    name = "Functional Specification Mismatch"
