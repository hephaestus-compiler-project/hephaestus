from src.ir.visitors import DefaultVisitor


class Transformation(DefaultVisitor):
    CORRECTNESS_PRESERVING = None
    NAME = None

    def __init__(self):
        self.transform = False

    @classmethod
    def get_name(cls):
        return cls.NAME

    @classmethod
    def preserve_correctness(cls):
        return cls.CORRECTNESS_PRESERVING
