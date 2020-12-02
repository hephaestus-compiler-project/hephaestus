from src.ir.visitors import DefaultVisitorUpdate


class Transformation(DefaultVisitorUpdate):
    CORRECTNESS_PRESERVING = None
    NAME = None

    def __init__(self):
        self.transform = False

    def result(self):
        return self.program

    @classmethod
    def get_name(cls):
        return cls.NAME

    @classmethod
    def preserve_correctness(cls):
        return cls.CORRECTNESS_PRESERVING
