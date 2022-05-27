import src.utils as ut
from src.ir import ast, types as tp, type_utils as tu
from src.ir.context import get_decl
from src.transformations.base import change_namespace
from src.translators.base import BaseTranslator

class TypeScriptTranslator(BaseTranslator):
    filename = "Main.ts"
    incorrect_filename = "Incorrect.ts"
    executable = "Main.js"
    ident_value = " "

    def __init__(self, package=None, options={}):
        super().__init__(package, options)
        self._children_res = []
        self.ident = 0
        self.context = None
    
    def get_filename(self):
        return self.filename;
    
    def visit_program(self, node):
        return

    def result(self):
        return "";