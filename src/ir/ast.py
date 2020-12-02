from src import utils
from src.ir import types


class Node(object):

    def accept(self, visitor):
        visitor.visit(self)

    def children(self):
        raise NotImplementedError('children() must be implemented')


class Program(Node):
    def __init__(self, declarations, context):
        self.declarations = declarations
        self.context = context

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
    def __init__(self, name, field_type, is_final=True, override=False):
        self.name = name
        self.field_type = field_type
        self.is_final = is_final
        self.override = override

    def children(self):
        return []

    def get_type(self):
        return self.field_type

    def __str__(self):
        return str(self.name) + ": " + str(self.field_type)


class ObjectDecleration(Declaration):
    def __init__(self, name):
        self.name = name

    def get_type(self):
        return types.Object(self.name)

    def __str__(self):
        return "object " + self.name


class SuperClassInstantiation(Node):
    def __init__(self, class_type, args=[]):
        self.class_type = class_type
        self.args = args

    def children(self):
        return self.args or []

    def __str__(self):
        if self.args is None:
            return self.class_type.name
        else:
            return self.class_type.name + "(" + ", ".join(map(str, self.args)) + ")"


class ClassDeclaration(Declaration):
    REGULAR = 0
    INTERFACE = 1
    ABSTRACT = 2

    def __init__(self, name, superclasses, class_type=None,
                 fields=[], functions=[], is_final=True, type_parameters=[]):
        self.name = name
        self.superclasses = superclasses
        self.class_type = class_type or self.REGULAR
        self.fields = fields
        self.functions = functions
        self.is_final = is_final
        self.type_parameters = type_parameters

    @property
    def attributes(self):
        return self.fields + self.functions

    def children(self):
        return self.fields + self.superclasses + self.functions

    def get_type(self):
        if self.type_parameters:
            return types.TypeConstructor(
                self.name, self.type_parameters,
                [s.class_type for s in self.superclasses])
        return types.SimpleClassifier(
            self.name, [s.class_type for s in self.superclasses])

    def get_class_prefix(self):
        if self.class_type == self.REGULAR:
            return "class"
        if self.class_type == self.INTERFACE:
            return "interface"
        return "abstract class"

    def __str__(self):
        superclasses = " : " + ", ".join(map(str, self.superclasses)) \
            if len(self.superclasses) > 0 else ""
        if self.type_parameters:
            return "{} {}<{}>{} {{\n  {}\n  {} }}".format(
                self.get_class_prefix(), self.name,
                ", ".join(map(str, self.type_parameters)),
                superclasses,
                "\n  ".join(map(str, self.fields)),
                "\n  ".join(map(str, self.functions))
            )
        return "{} {}{} {{\n  {}\n  {} }}".format(
            self.get_class_prefix(), self.name,
            superclasses,
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
    CLASS_METHOD = 0
    FUNCTION = 1

    def __init__(self, name, params, ret_type, body, func_type,
                 is_final=True, override=False):
        self.name = name
        self.params = params
        self.ret_type = ret_type
        self.body = body
        self.func_type = func_type
        self.is_final = is_final
        self.override = override

    def children(self):
        if self.body is None:
            return self.params
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

class ParameterizedFunctionDeclaration(FunctionDeclaration):
    CLASS_METHOD = 0
    FUNCTION = 1

    def __init__(self, name, type_parameters, params, ret_type, body,
                 func_type, is_final=True, override=False):
        super(ParameterizedFunctionDeclaration, self).__init__(name, params,
              ret_type, body, func_type, is_final, override)
        self.type_parameters = type_parameters

    def get_type(self):
        return types.ParameterizedFunction(
            self.name, type_parameters,
            [p.get_type() for p in self.params], self.ret_type)

    def __str__(self):
        keywords = ""
        if len(keywords) > 0:
            keywords = " ".join(map(lambda x: x.name, self.keywords))
        if self.ret_type is None:
            return "{}fun<{}> {}({}) =\n  {}".format(
                keywords, ",".join(map(str, self.type_parameters)),
                self.name, ",".join(map(str, self.params)), str(self.body))
        else:
            return "{}fun<{}> {}({}): {} =\n  {}".format(
                keywords, ",".join(map(str, self.type_parameters)),
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


class BooleanConstant(Constant):
    def __init__(self, literal):
        assert literal == 'true' or literal == 'false', (
            'Boolean literal is not "true" or "false"')
        super(BooleanConstant, self).__init__(literal)


class CharConstant(Constant):
    def __init__(self, literal):
        assert len(literal) == 1, (
            'Character literal must be a single character')
        super(CharConstant, self).__init__(literal)

    def __str__(self):
        return "'{}'".format(self.literal)


class StringConstant(Constant):

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
        self.cond = cond
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
    def __init__(self, class_type: types.Type, args, type_args=[]):
        self.class_type = class_type
        self.args = args
        self.type_args = type_args

    def children(self):
        return self.args

    def __str__(self):
        if self.type_args:
            return " new {}<{}> ({})".format(
                str(self.class_type.name),
                ", ".join(map(str, self.type_args)) + ")",
                ", ".join(map(str, self.args)) + ")"
            )

        return "new " + self.class_type.name + "(" + \
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
