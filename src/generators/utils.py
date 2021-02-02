from src import utils
from src.ir import ast

import src.ir.types as tp
import src.ir.builtins as bt


def gen_identifier(ident_type=None):
    word = utils.random.word()
    if ident_type is None:
        return word
    if ident_type == 'lower':
        return word.lower()
    return word.capitalize()


# pylint: disable=unused-argument
def gen_string_constant(expr_type=None):
    return ast.StringConstant(gen_identifier())


# pylint: disable=unused-argument
def gen_integer_constant(expr_type=None):
    return ast.IntegerConstant(utils.random.integer(-100, 100), expr_type)


def gen_real_constant(expr_type=None):
    prefix = str(utils.random.integer(0, 100))
    suffix = str(utils.random.integer(0, 1000))
    sign = utils.random.choice(['', '-'])
    if (isinstance(expr_type, tp.Builtin) and
            expr_type.get_builtin_type() == bt.Float):
        suffix += "f"
    return ast.RealConstant(sign + prefix + "." + suffix)


# pylint: disable=unused-argument
def gen_bool_constant(expr_type=None):
    return ast.BooleanConstant(utils.random.choice(['true', 'false']))


# pylint: disable=unused-argument
def gen_char_constant(expr_type=None):
    return ast.CharConstant(utils.random.char())
