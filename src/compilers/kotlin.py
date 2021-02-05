from collections import defaultdict
import re

from src.compilers.base import BaseCompiler


class KotlinCompiler(BaseCompiler):
    ERROR_REGEX = re.compile(
        r'([a-zA-Z0-9\/_]+.kt):\d+:\d+:[ ]+error:[ ]+(.*)')
    CRASH_REGEX = re.compile(
        r'(org\.jetbrains\..*)\nFile being compiled: .* in (.*\.kt)',
        re.MULTILINE
    )

    def __init__(self, input_name):
        super().__init__(input_name)

    @classmethod
    def get_compiler_version(cls):
        return ['kotlinc', '-version']

    def get_compiler_cmd(self):
        return ['kotlinc', self.input_name, '-include-runtime', '-d',
                'program.jar']

    @classmethod
    def analyze_compiler_output(cls, output):
        failed = defaultdict(list)
        matches = re.findall(cls.ERROR_REGEX, output)
        for match in matches:
            filename = match[0]
            error_msg = match[1]
            failed[filename].append(error_msg)

        matches = re.findall(cls.CRASH_REGEX, output)
        for match in matches:
            filename = match[1]
            error_msg = match[0]
            failed[filename].append(error_msg)
        return failed
