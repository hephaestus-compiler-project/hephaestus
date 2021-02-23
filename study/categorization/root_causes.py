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


class WrongParams(RootCause):
    name = "Incorrect / Insufficient parameters passed"


class InsufficientFunctionality(RootCause):
    name = "Insufficient Functionality"


class DesignIssue(RootCause):
    name = "Design Issue"
