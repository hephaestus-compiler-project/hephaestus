from src import utils


class Node(object):

    def accept(self, visitor):
        raise NotImplementedError('accept() must be implemented')


class Declaration(Node):
    pass


class FieldDeclaration(Declaration):
    def __init__(self, name, field_type):
        self.name = name
        self.field_type = field_type

    def accept(self, visitor):
        visitor.visitFieldDeclaration(self)

    def __str__(self):
        return str(self.name) + ": " + str(self.type)


class ClassDeclaration(Declaration):
    def __init__(self, name, superclasses, fields=[], functions=[]):
        self.name = name
        self.superclasses = superclasses
        self.fields = fields
        self.functions = functions

    @property
    def attributes(self):
        return self.fields + self.functions

    def accept(self, visitor):
        visitor.visitClassDeclaration(self)


class Expr(Node):
    pass


class Constant(Expr):
    def __init__(self, literal):
        self.literal = literal

    def __str__(self):
        return str(self.literal)


class IntegerConstant(Constant):
    # TODO: Support Hex Integer literals, binary integer literals?
    def __init__(self, literal):
        assert isinstance(literal, int) or isinstance(literal, long), (
            'Integer literal must either int or long')

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

    def accept(self, visitor):
        visitor.visitCharConstant(self)


class StringConstant(Constant):
    def accept(self, visitor):
        visitor.visitStringConstant(self)


class Identifier(Expr):
    def __init__(self, name):
        self.name = name

    def accept(self, visitor):
        visitor.visitIdentifier(self)

    def __str__(self):
        return str(self.name)


class Conditional(Expr):
    def __init__(self, cond, true_branch, false_branch):
        self.cond = cond,
        self.true_branch = true_branch
        self.false_branch = false_branch

    def accept(self, visitor):
        visitor.visitConditional(self)

    def __str__(self):
        "if ({})\n  {}\nelse\n  {}".format(
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

    def __str__(self):
        return str(self.lexpr) + " " + self.operator + " " + str(self.rexpr)


class BooleanExpr(BinaryOp):
    VALID_OPERATORS = ['&&', '||']

    def accept(self, visitor):
        visitor.visitBooleanExr(self)


class EqualityExpr(BinaryOp):
    VALID_OPERATORS = ['==', '===', '!=', '!==']

    def accept(self, visitor):
        visitor.visitEqualityExr(self)


class ComparisonExpr(BinaryOp):
    VALID_OPERATORS = ['>', '>=', '<', '<=']

    def accept(self, visitor):
        visitor.visitComparisonExr(self)


class ArithExpr(BinaryOp):
    VALID_OPERATORS = ['+', '-', '/', '*']

    def accept(self, visitor):
        visitor.visitArithExr(self)


class New(Expr):
    def __init__(self, class_name, args):
        self.class_name = class_name
        self.args = args

    def accept(self, visitor):
        visitor.visitNew(self)

    def __str__(self):
        return "new " + str(self.class_name) + "(" + self.args.join(",") + ")"


class Statement(Node):
    pass


class Assignment(Statement):
    def __init__(self, var_name, var_type, expr):
        self.var_name = var_name
        self.var_type = var_type
        self.expr = expr

    def accept(self, visitor):
        visitor.visitAssignment(self)


class Program:
    def __init__(self):
        pass
