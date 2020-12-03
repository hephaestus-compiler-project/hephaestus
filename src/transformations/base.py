from src.ir import ast
from src.ir.visitors import DefaultVisitorUpdate


class Transformation(DefaultVisitorUpdate):
    CORRECTNESS_PRESERVING = None
    NAME = None

    def __init__(self):
        self.transform = False
        self.types = []

    def result(self):
        return self.program

    def find_subtypes(self, t):
        return self._find_types(t, find_subtypes=True)

    def find_supertypes(self, t):
        return self._find_types(t, find_subtypes=False)

    def _find_types(self, t, find_subtypes):
        lst = []
        for c in self.types:
            if isinstance(c, ast.ClassDeclaration):
                t2 = c.get_type()
            else:
                t2 = c
            if t == t2:
                continue
            if find_subtypes and t2.is_subtype(t):
                lst.append(c)
            if not find_subtypes and t.is_subtype(t2):
                lst.append(c)
        return lst

    @classmethod
    def get_name(cls):
        return cls.NAME

    @classmethod
    def preserve_correctness(cls):
        return cls.CORRECTNESS_PRESERVING
