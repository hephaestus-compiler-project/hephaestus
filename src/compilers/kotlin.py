from collections import defaultdict
import re

from src.compilers.base import BaseCompiler


class KotlinCompiler(BaseCompiler):
    REGEX = re.compile(r'([a-zA-Z0-9\/_]+.kt):\d+:\d+:[ ]+error:[ ]+(.*)')

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
        matches = re.findall(cls.REGEX, output)
        for match in matches:
            filename = match[0]
            error_msg = match[1]
            failed[filename].append(error_msg)
        return failed
