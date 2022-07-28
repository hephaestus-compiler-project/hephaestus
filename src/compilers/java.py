import re
import os

from src.compilers.base import BaseCompiler


class JavaCompiler(BaseCompiler):
    # Match (example.groovy):(error message until empty line)
    ERROR_REGEX = re.compile(
        r'([a-zA-Z0-9\/_]+.java):(\d+:[ ]+error:[ ]+.*)(.*?(?=\n{1,}))')

    CRASH_REGEX = re.compile(r'(java\.lang.*)\n(.*)')

    def __init__(self, input_name, filter_patterns=None):
        input_name = os.path.join(input_name, '*', '*.java')
        super().__init__(input_name, filter_patterns)

    @classmethod
    def get_compiler_version(cls):
        return ['javac', '-version']

    def get_compiler_cmd(self):
        return ['javac', '-nowarn', self.input_name]

    def get_filename(self, match):
        return match[0]

    def get_error_msg(self, match):
        return match[1]
