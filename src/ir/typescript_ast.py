import src.ir.ast as ast
import src.ir.types as types

class TypeAliasDeclaration(ast.Declaration):
    def __init__(self, name: str,
                 alias: types.Type):
        self.name = name
        self.alias = alias

    def children(self):
        return [self.alias]

    def get_type(self):
        return self.alias

    def update_children(self, children):
        super().update_children(children)
        self.alias = children[0]
