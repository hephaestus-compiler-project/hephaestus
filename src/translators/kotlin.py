import random


class Kotlin:

    filename = "program.kt"
    executable = "program.jar"

    def __init__(self):
        pass

    def concretize(self, program):
        pass

    def dummy_concretize(self, program=None):
        return """fun main() {
    println("Hello World!")
}"""

    def dummy_concretize_fault(self, program=None):
        return """fun main() {
    println("Hello World!"
}"""

    def dummy_concretize_random(self, program=None):
        if random.randrange(2):
            return self.dummy_concretize()
        return self.dummy_concretize_fault()

    @staticmethod
    def get_filename():
        return Kotlin.filename

    @staticmethod
    def get_executable():
        return Kotlin.executable

    @staticmethod
    def get_cmd_build(filename, executable):
        return ['kotlinc', filename, '-include-runtime', '-d', executable]

    @staticmethod
    def get_cmd_exec(executable):
        return ['java', '-jar', executable]
