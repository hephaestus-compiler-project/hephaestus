from src import utils
from src.ir import types


class Node(object):

    def accept(self, visitor):
        visitor.visit(self)

    def children(self):
        raise NotImplementedError('children() must be implemented')


class Program(Node):
    def __init__(self, declarations):
        self.declarations = declarations

    def children(self):
        return self.declarations

    def __str__(self):
        return "\n\n".join(map(str, self.declarations))


class Block(Node):
    def __init__(self, body):
        self.body = body

    def children(self):
        return self.body

    def __str__(self):
        return "{{\n  {}\n}}".format("\n  ".join(map(str, self.body)))


class Declaration(Node):
    def get_type(self):
        raise NotImplementedError('get_type() must be implemented')


class VariableDeclaration(Declaration):
    def __init__(self, name, expr, var_type=None):
        self.name = name
        self.expr = expr
        self.var_type = var_type

    def children(self):
        return [self.expr]

    def get_type(self):
        return self.var_type

    def __str__(self):
        if self.var_type is None:
            return "val " + self.name + " = " + str(self.expr)
        else:
            return "val " + self.name + ": " + str(self.var_type) + \
                " = " + str(self.expr)


class FieldDeclaration(Declaration):
    def __init__(self, name, field_type):
        self.name = name
        self.field_type = field_type

    def children(self):
        return []

    def get_type(self):
        return self.field_type

    def __str__(self):
        return str(self.name) + ": " + str(self.field_type)


class ClassDeclaration(Declaration):
    REGULAR = 0
    INTERFACE = 1
    ABSTRACT = 2

    def __init__(self, name, superclasses, class_type=None,
                 fields=[], functions=[]):
        self.name = name
        self.superclasses = superclasses
        self.class_type = class_type or self.REGULAR
        self.fields = fields
        self.functions = functions

    @property
    def attributes(self):
        return self.fields + self.functions

    def children(self):
        return self.fields + self.functions

    def get_type(self):
        return types.SimpleClassifier(self.name, supertypes=self.superclasses)

    def __str__(self):
        if self.class_type == self.REGULAR:
            prefix = "class"
        elif self.class_type == self.INTERFACE:
            prefix = "interface"
        else:
            prefix = "abstract class"
        return "{} {} {{\n  {}\n  {} }}".format(
            prefix, self.name,
            "\n  ".join(map(str, self.fields)),
            "\n  ".join(map(str, self.functions))
        )


class ParameterDeclaration(Declaration):
    def __init__(self, name, param_type, default=None):
        self.name = name
        self.param_type = param_type
        self.default = default

    def children(self):
        return []

    def get_type(self):
        return self.param_type

    def __str__(self):
        if self.default is None:
            return self.name + ": " + str(self.param_type)
        else:
            return self.name + ": " + str(
                self.param_type) + " = " + str(self.expr)


class FunctionDeclaration(Declaration):
    EXPRESSION_FUNC = 0
    BLOCK_FUNC = 1

    def __init__(self, name, params, ret_type, body, body_type=BLOCK_FUNC):
        self.name = name
        self.params = params
        self.ret_type = ret_type
        self.body = body
        self.body_type = body_type

    def children(self):
        return self.params + [self.body]

    def get_type(self):
        return types.Function(
            self.name, [p.get_type() for p in self.params], self.ret_type)

    def __str__(self):
        if self.ret_type is None:
            return "fun {}({}) =\n  {}".format(
                self.name, ",".join(map(str, self.params)), str(self.body))
        else:
            return "fun {}({}): {} =\n  {}".format(
                self.name, ",".join(map(str, self.params)), str(self.ret_type),
                str(self.body))


class Expr(Node):
    pass


class Constant(Expr):
    def __init__(self, literal):
        self.literal = literal

    def children(self):
        return []

    def __str__(self):
        return str(self.literal)


class IntegerConstant(Constant):
    # TODO: Support Hex Integer literals, binary integer literals?
    def __init__(self, literal):
        assert isinstance(literal, int) or isinstance(literal, long), (
            'Integer literal must either int or long')
        super(IntegerConstant, self).__init__(literal)

    def accept(self, visitor):
        visitor.visitIntegerConstant(self)


class RealConstant(Constant):

    def __init__(self, literal):
        suffix = None
        if literal.endswith('f') or literal.endswith('F'):
            literal_nums = literal[:-1]
            suffix = literal[-1]
        else:
            literal_nums = literal
        assert '.' in literal_nums and utils.is_number(literal_nums), (
            'Real literal is not valid')
        self.literal = literal_nums + ('' if suffix is None else suffix)

    def accept(self, visitor):
        visitor.visitRealConstant(self)


class BooleanConstant(Constant):
    def __init__(self, literal):
        assert literal == 'true' or literal == 'false', (
            'Boolean literal is not "true" or "false"')
        super(BooleanConstant, self).__init__(literal)

    def accept(self, visitor):
        visitor.visitBooleanConstant(self)


class CharConstant(Constant):
    def __init__(self, literal):
        assert len(literal) == 1, (
            'Character literal must be a single character')
        super(CharConstant, self).__init__(literal)

    def accept(self, visitor):
        visitor.visitCharConstant(self)

    def __str__(self):
        return "'{}'".format(self.literal)

class StringConstant(Constant):
    def accept(self, visitor):
        visitor.visitStringConstant(self)

    def __str__(self):
        return '"{}"'.format(self.literal)


class Variable(Expr):
    def __init__(self, name):
        self.name = name

    def children(self):
        return []

    def __str__(self):
        return str(self.name)


class Conditional(Expr):
    def __init__(self, cond, true_branch, false_branch):
        self.cond = cond,
        self.true_branch = true_branch
        self.false_branch = false_branch

    def children(self):
        return [self.cond, self.true_branch, self.false_branch]

    def __str__(self):
        return "if ({})\n  {}\nelse\n  {}".format(
            str(self.cond), str(self.true_branch), str(self.false_branch))


class BinaryOp(Expr):
    VALID_OPERATORS = None

    def __init__(self, lexpr, rexpr, operator):
        if self.VALID_OPERATORS is not None:
            assert operator in self.VALID_OPERATORS, (
                'Binary operator ' + operator + ' is not valid')
        self.lexpr = lexpr
        self.rexpr = rexpr
        self.operator = operator

    def children(self):
        return [self.lexpr, self.rexpr]

    def __str__(self):
        return str(self.lexpr) + " " + self.operator + " " + str(self.rexpr)


class LogicalExpr(BinaryOp):
    VALID_OPERATORS = ['&&', '||']


class EqualityExpr(BinaryOp):
    VALID_OPERATORS = ['==', '===', '!=', '!==']


class ComparisonExpr(BinaryOp):
    VALID_OPERATORS = ['>', '>=', '<', '<=']


class ArithExpr(BinaryOp):
    VALID_OPERATORS = ['+', '-', '/', '*']


class New(Expr):
    def __init__(self, class_name, args):
        self.class_name = class_name
        self.args = args

    def children(self):
        return self.args

    def __str__(self):
        return "new " + str(self.class_name) + "(" + \
            ", ".join(map(str, self.args)) + ")"


class FieldAccess(Expr):
    def __init__(self, expr, field):
        self.expr = expr
        self.field = field

    def children(self):
        return [self.expr]

    def __str__(self):
        return str(self.expr) + "." + self.field


class FunctionCall(Expr):
    def __init__(self, func, args, receiver=None):
        self.func = func
        self.args = args
        self.receiver = receiver

    def children(self):
        return self.args

    def __str__(self):
        if self.receiver is None:
            return self.func + "(" + ", ".join(map(str, self.args)) + ")"
        else:
            return str(self.receiver) + ".(" + \
                ", ".join(map(str, self.args)) + ")"


class Assignment(Expr):
    def __init__(self, var_name, expr):
        self.var_name = var_name
        self.expr = expr

    def children(self):
        return [self.expr]

    def __str__(self):
        return str(self.var_name) + " = " + str(self.expr)
