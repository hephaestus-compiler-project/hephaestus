from src.ir import ast
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

    def __init__(self):
        self.transform = False
        self.program = None
        self.types = []

    def result(self):
        return self.program

    def find_subtypes(self, t, include_self=False):
        return self._find_types(t, find_subtypes=True, include_self=include_self)

    def find_supertypes(self, t, include_self=False):
        return self._find_types(t, find_subtypes=False, include_self=include_self)

    def _find_types(self, t, find_subtypes, include_self):
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
                continue
            if not find_subtypes and t.is_subtype(t2):
                lst.append(c)
        if include_self:
            lst.append(t)
        return lst

    @classmethod
    def get_name(cls):
        return cls.NAME

    @classmethod
    def preserve_correctness(cls):
        return cls.CORRECTNESS_PRESERVING
