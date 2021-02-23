
class Symptom():
    name = ""

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.__repr__()


class RuntimeSymptom():
    name = ""

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.__repr__()


class VerifyError(RuntimeSymptom):
    name = "VerifyError"


class AbstractMethodError(RuntimeSymptom):
    name = "AbstractMethodError"


class NullPointerException(RuntimeSymptom):
    name = "NullPointerException"


class WrongMethodCalled(RuntimeSymptom):
    name = "Wrong Method Called"


class Runtime(Symptom):
    name = "Runtime"

    def __init__(self, failure=None):
        self.failure = failure

    def __repr__(self):
        if self.failure:
            return self.name + " (" + str(self.failure) + ")"
        return self.name

    def __str__(self):
        return self.__repr__()


class CompileTimeError(Symptom):
    name = "Compile Time Error"


class InternalCompilerError(Symptom):
    name = "Internal Compiler Error"


class MisleadingReport(Symptom):
    name = "Misleading Report"
