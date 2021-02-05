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
        self.crash_msg = None

    @classmethod
    def get_compiler_version(cls):
        return ['kotlinc', '-version']

    def get_compiler_cmd(self):
        return ['kotlinc', self.input_name, '-include-runtime', '-d',
                'program.jar']

    def analyze_compiler_output(self, output):
        self.crashed = None
        failed = defaultdict(list)
        matches = re.findall(self.ERROR_REGEX, output)
        for match in matches:
            filename = match[0]
            error_msg = match[1]
            failed[filename].append(error_msg)

        match = re.search(self.CRASH_REGEX, output)
        if match:
            self.crash_msg = ':'.join(match.groups())
            return None
        return failed
