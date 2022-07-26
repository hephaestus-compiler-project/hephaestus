from collections import defaultdict
import re
import os
from src.compilers.base import BaseCompiler

class TypeScriptCompiler(BaseCompiler):

    ERROR_REGEX = re.compile(r'([A-Za-z0-9_\-\/]+\.ts):\d+:\d+ - error (TS\d+): (.+)')

    CRASH_REGEX = re.compile("123")

    def __init__(self, input_name):
        super().__init__(input_name)
        self.crash_msg = None

    @classmethod
    def get_compiler_version(cls):
        return ['tsc', '-v']

    def get_compiler_cmd(self):
        return ['tsc --target es2020', self.input_name]

    def analyze_compiler_output(self, output):
        self.crashed = None
        failed = defaultdict(list)
        matches = re.findall(self.ERROR_REGEX, output)
        for match in matches:
            filename = match[0]
            error_msg = match[2]
            failed[filename].append(error_msg)
        

        crash_match = re.search(self.CRASH_REGEX, output)
        if crash_match and not matches:
            self.crash_msg = output
            return None
        return failed