import re

from src.compilers.base import BaseCompiler


class KotlinCompiler(BaseCompiler):
    ERROR_REGEX = re.compile(
        r'([a-zA-Z0-9\/_]+.kt):\d+:\d+:[ ]+error:[ ]+(.*)')
    CRASH_REGEX = re.compile(
        r'(org\.jetbrains\..*)\n(.*)',
        re.MULTILINE
    )

    def __init__(self, input_name, filter_patterns=None):
        super().__init__(input_name, filter_patterns)

    @classmethod
    def get_compiler_version(cls):
        return ['kotlinc', '-version']

    def get_compiler_cmd(self):
        return ['kotlinc', self.input_name, '-include-runtime', '-d',
                'program.jar']

    def get_filename(self, match):
        return match[0]

    def get_error_msg(self, match):
        return match[1]
