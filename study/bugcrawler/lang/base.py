
class LangBase():
    def __init__(self, filters):
        self.filters = filters

    def get(self, *args, **kwargs):
        raise NotImplementedError("get not implemented in child class")

    def transform_bugs(self, bugs):
        raise NotImplementedError('transform_bugs() must be implemented')
