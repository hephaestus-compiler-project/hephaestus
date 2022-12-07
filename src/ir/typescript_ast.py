import src.ir.ast as ast
import src.ir.types as types
import src.ir.typescript_types as tst

class TypeAliasDeclaration(ast.Declaration):
    def __init__(self, name: str,
                 alias: types.Type):
        self.name = name
        self.alias = alias

    def children(self):
        return [self.alias]

    def get_type(self):
        return tst.AliasType(self.alias, self.name)

    def update_children(self, children):
        super().update_children(children)
        self.alias = children[0]

    def is_equal(self, other):
        if isinstance(other, TypeAliasDeclaration):
            return (self.name == other.name and
                     self.alias == other.alias)

    def __str__(self):
        return f'{self.name} (TypeAliasDecl<{str(self.alias)}>)'
