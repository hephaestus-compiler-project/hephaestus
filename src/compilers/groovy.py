from collections import defaultdict
import re

from src.compilers.base import BaseCompiler


class GroovyCompiler(BaseCompiler):
    # Match (example.groovy):(error message until empty line)
    REGEX = re.compile(r'([a-zA-Z0-9\\/_]+.groovy):([\s\S]*?(?=\n{2,}))')

    @classmethod
    def get_compiler_version(cls):
        return ['groovyc', '-version']

    def get_compiler_cmd(self):
        return ['groovyc', '--compile-static', self.input_name]

    @classmethod
    def analyze_compiler_output(cls, output):
        failed = defaultdict(list)
        matches = re.findall(cls.REGEX, output)
        for match in matches:
            filename = match[0]
            error_msg = match[1]
            failed[filename].append(error_msg)
        return failed
