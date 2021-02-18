from collections import defaultdict
import re
import os

from src.compilers.base import BaseCompiler


class GroovyCompiler(BaseCompiler):
    # Match (example.groovy):(error message until empty line)
    ERROR_REGEX = re.compile(r'([a-zA-Z0-9\\/_]+.groovy):([\s\S]*?(?=\n{2,}))')

    CRASH_REGEX = re.compile(r'(.*[eE]xception)(.*)')

    def __init__(self, input_name):
        input_name = os.path.join(input_name, '*', '*.groovy')
        super().__init__(input_name)
        self.crash_msg = None

    @classmethod
    def get_compiler_version(cls):
        return ['groovyc', '-version']

    def get_compiler_cmd(self):
        return ['groovyc', '--compile-static', self.input_name]

    def analyze_compiler_output(self, output):
        self.crashed = None
        failed = defaultdict(list)
        matches = re.findall(self.ERROR_REGEX, output)
        for match in matches:
            filename = match[0]
            error_msg = match[1]
            failed[filename].append(error_msg)

        crash_match = re.search(self.CRASH_REGEX, output)
        if crash_match and not matches:
            self.crash_msg = ':'.join(match.groups())
            return None
        return failed
