import os
import re

from src.compilers.base import BaseCompiler


class ScalaCompiler(BaseCompiler):
    ERROR_REGEX = re.compile(
        r"-- .*Error: (.*\.scala):\d+:\d+ -+\n((?:[^-]+))", re.MULTILINE)
    CRASH_REGEX = re.compile(r"Exception in thread(.*)")

    def __init__(self, input_name, filter_patterns=None):
        input_name = os.path.join(input_name, '*', '*.scala')
        print(input_name)
        super().__init__(input_name, filter_patterns)

    @classmethod
    def get_compiler_version(cls):
        return ['scalac', '-version']

    def get_compiler_cmd(self):
        return ['scalac', '-color', 'never', '-nowarn', self.input_name]

    def get_filename(self, match):
        return match[0]

    def get_error_msg(self, match):
        return match[1]
