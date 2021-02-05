class BaseCompiler():
    def __init__(self, input_name):
        self.input_name = input_name

    @classmethod
    def get_compiler_version(cls):
        raise NotImplementedError('get_compiler_version() must be implemented')

    def get_compiler_cmd(self):
        raise NotImplementedError('get_compiler_cmd() must be implemented')

    def analyze_compiler_output(cls, output):
        raise NotImplementedError(
            'analyze_compiler_output() must be implemented')
