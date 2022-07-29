from collections import defaultdict
import re


class BaseCompiler():
    ERROR_REGEX = None
    CRASH_REGEX = None

    def __init__(self, input_name, filter_patterns=None):
        self.input_name = input_name
        self.filter_patterns = filter_patterns or []
        self.crash_msg = None

    @classmethod
    def get_compiler_version(cls):
        raise NotImplementedError('get_compiler_version() must be implemented')

    def get_compiler_cmd(self):
        raise NotImplementedError('get_compiler_cmd() must be implemented')

    def get_filename(self, match):
        raise NotImplementedError('get_filename() must be implemented')

    def get_error_msg(self, match):
        raise NotImplementedError('get_error_msg() must be implemented')

    def analyze_compiler_output(self, output):
        failed = defaultdict(list)
        filtered_output = output
        for p in self.filter_patterns:
            filtered_output = re.sub(p, '', filtered_output)
        matches = re.findall(self.ERROR_REGEX, filtered_output)
        for match in matches:
            filename = self.get_filename(match)
            error_msg = self.get_error_msg(match)
            failed[filename].append(error_msg)

        crash_match = re.search(self.CRASH_REGEX, output)
        if crash_match and not matches:
            self.crash_msg = output
            return None, matches
        return failed, matches
