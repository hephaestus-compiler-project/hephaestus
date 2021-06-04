from src.ir import types as tp
from src.ir.visitors import ASTVisitor


class BaseTranslator(ASTVisitor):

    def __init__(self, package=None, options={}):
        self.program = None
        self.package = package

    def result(self) -> str:
        if self.program is None:
            raise Exception('You have to translate the program first')
        return self.program

    def get_type_name(self, t: tp.Type) -> str:
        raise NotImplementedError('get_type_name() must be implemented')
