class Bug:
    language = ""

    def __init__(self, bug_id, characteristics, test_case_correct, symptom,
                 root_cause, category):
        self.bug_id = bug_id
        self.characteristics = characteristics
        self.test_case_correct = test_case_correct
        self.symptom = symptom
        self.root_cause = root_cause
        self.category = category

    def __repr__(self):
        return "Bug: {} (\n\t{}\n\t{}\n\t{}\n\t{}\n\t{}\n)".format(
            self.bug_id,
            "Characteristics: \n\t\t" + "\n\t\t".join([str(c) for c in self.characteristics]),
            "Test Case Correct: " + str(self.test_case_correct),
            "Symptom: " + str(self.symptom),
            "Root Cause: " + str(self.root_cause),
            "Category: " + str(self.category)
        )

    def __str__(self):
        return self.__repr__()


class KotlinBug(Bug):
    language = "Kotlin"


class GroovyBug(Bug):
    language = "Groovy"


class JavaBug(Bug):
    language = "Java"


class ScalaBug(Bug):
    language = "Scala"
    compiler = "scala"


class ScalaDottyBug(ScalaBug):
    compiler = "dotty"

