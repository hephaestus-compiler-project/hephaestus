from collections import defaultdict
import re
import os
from src.compilers.base import BaseCompiler


class TypeScriptCompiler(BaseCompiler):

    ERROR_REGEX = re.compile(
        r'[.\/]+(/[A-Za-z0-9_\-\/]+\.ts).*error.*(TS\d+): (.+)')

    CRASH_REGEX = re.compile(r'(.+)(\n(\s+at .+))+')

    def __init__(self, input_name, filter_patterns=None):
        super().__init__(input_name, filter_patterns)

    @classmethod
    def get_compiler_version(cls):
        return ['tsc', '-v']

    def get_compiler_cmd(self):
        return ['tsc --target es2020 --pretty false', os.path.join(
            self.input_name, '**', '*.ts')]

    def get_filename(self, match):
        return match[0]

    def get_error_msg(self, match):
        return f"{match[1]}{match[2]}"
