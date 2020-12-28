from src.ir import ast, types
from src.ir.visitors import DefaultVisitorUpdate


def change_namespace(visit):
    def inner(self, node):
        initial_namespace = self._namespace
        self._namespace += (node.name,)
        new_node = visit(self, node)
        self._namespace = initial_namespace
        return new_node
    return inner


class Transformation(DefaultVisitorUpdate):
    CORRECTNESS_PRESERVING = None
    NAME = None

    def __init__(self, logger=None):
        self.transform = False
        self.program = None
        self.types = []
        self.logger = logger
        if self.logger:
            self.logger.log_info()

    def result(self):
        return self.program

    def log(self, msg):
        if self.logger is None:
            print("Warning logger is None")
        else:
            self.logger.log(msg)

    @classmethod
    def get_name(cls):
        return cls.NAME

    @classmethod
    def preserve_correctness(cls):
        return cls.CORRECTNESS_PRESERVING
