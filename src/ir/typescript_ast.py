from src.ir import ast
import src.ir.types as types

class TypeAliasDeclaration(ast.Declaration):
    def __init__(self, name: str,
                type_descr: types.Type,
                expr: ast.Expr,):
        self.name = name
        self.type_descr = type_descr
        self.expr = expr

    def children(self):
        return [self.expr]

    def get_type(self):
        return self.type_descr

    def update_children(self, children):
        super().update_children(children)
        self.expr = children[0]
