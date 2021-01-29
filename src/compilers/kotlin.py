from collections import defaultdict
import re

from src.compilers.base import BaseCompiler


class KotlinCompiler(BaseCompiler):
    REGEX = re.compile(r'([a-zA-Z\/_]+.kt):\d+:\d: (.*)')

    def __init__(self, input_name, executable):
        super().__init__(input_name, executable)
        self.input_name = input_name
        self.executable = executable

    @classmethod
    def get_compiler_version(cls):
        return ['kotlinc', '-version']

    def get_compiler_cmd(self):
        return ['kotlinc', self.input_name, '-include-runtime', '-d',
                self.executable]

    @classmethod
    def analyze_compiler_output(cls, output):
        failed = defaultdict(list)
        matches = re.findall(cls.REGEX, output)
        for match in matches:
            filename = match[1]
            error_msg = match[2]
            failed[filename].append(error_msg)
        return failed
