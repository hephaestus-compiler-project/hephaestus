from copy import deepcopy
from collections import defaultdict

from src import utils
from src.ir import ast, types as tp
from src.ir import kotlin_types as kt
from src.generators import Generator
from src.transformations.base import Transformation


class ValueSubstitution(Transformation):

    CORRECTNESS_PRESERVING = True
    NAME = 'Value Substitution'

    def __init__(self):
        super(ValueSubstitution, self).__init__()
        self.program = None
        self.generator = None

    def visit_program(self, node):
        self.generator = Generator(context=node.context)
        usr_types = [d for d in node.declarations
                     if isinstance(d, ast.ClassDeclaration)] + \
            self.generator.RET_BUILTIN_TYPES
        self.types = usr_types
        usr_types.remove(kt.Any)
        new_node = super(ValueSubstitution, self).visit_program(node)
        if self.transform:
            self.program = new_node
        return new_node

    def generate_new(self, class_decl):
        return ast.New(
            class_decl.get_type(),
            args=[self.generator.generate_expr(f.field_type, only_leaves=True)
                  for f in class_decl.fields])

    def visit_equality_expr(self, node):
        # We are conservative here, because value subtitution may in the
        # children of an equality expression may break the corectness of
        # the program.
        #
        # To preserve corectness, wee need to get the greatest lower bound
        # of children. TODO: revisit.
        return node

    def visit_new(self, node):
        # If this node has children then randomly decide if we
        # gonna subtitute one of its children or the current node.
        if node.children() and utils.random.bool():
            return super(ValueSubstitution, self).visit_new(node)
        subclasses = tp.find_subtypes(node.class_type, self.types)
        subclasses = [c for c in subclasses
                      if not (isinstance(c, ast.ClassDeclaration) and
                              c.class_type != ast.ClassDeclaration.REGULAR)]
        if not subclasses:
            return node
        self.transform = True
        sub_c = utils.random.choice(subclasses)
        generators = {
            kt.Boolean: self.generator.gen_bool_constant,
            kt.Char: self.generator.gen_char_constant,
            kt.String: self.generator.gen_string_constant,
            kt.Integer: self.generator.gen_integer_constant,
            kt.Short: self.generator.gen_integer_constant,
            kt.Long: self.generator.gen_integer_constant,
            kt.Float: lambda: self.generator.gen_real_constant(kt.Float),
            kt.Double: self.generator.gen_real_constant,
        }
        generate = generators.get(sub_c, lambda: self.generate_new(sub_c))
        return generate()


class TypeSubstitution(Transformation):
    CORRECTNESS_PRESERVING = True
    NAME = 'Type Substitution (Widening/Narrowing)'


    def __init__(self):
        super(TypeSubstitution, self).__init__()
        self.program = None
        self.generator = None
        self._defs = defaultdict(bool)
        self._namespace = ('global',)
        self._cached_type_widenings = {}

    def _type_widening(self, decl, setter):
        superclasses = tp.find_supertypes(decl.get_type(), self.types)
        if not superclasses:
            return False
        sup_t = self._cached_type_widenings.get(
            (decl.name, decl.get_type().name))
        if sup_t is None:
            sup_t = utils.random.choice(superclasses)
            if isinstance(sup_t, ast.ClassDeclaration):
                sup_t = sup_t.get_type()
            self._cached_type_widenings[(decl.name, decl.get_type().name)] = sup_t
        self.transform = True
        setter(decl, sup_t)
        return True

    def visit_program(self, node):
        self.generator = Generator(context=node.context)
        usr_types = [d for d in node.declarations
                     if isinstance(d, ast.ClassDeclaration)] + \
            self.generator.RET_BUILTIN_TYPES
        self.types = usr_types
        new_node = super(TypeSubstitution, self).visit_program(node)
        if self.transform:
            self.program = new_node
        return new_node

    def _create_function_block(self, function, is_expr, var_decl,
                               declared=False):
        if not declared:
            if_cond = ast.Conditional(is_expr, deepcopy(function.body),
                                      ast.Variable(var_decl.name))
            return ast.Block([var_decl, if_cond])
        if_cond = ast.Conditional(is_expr,
                                  ast.Block(deepcopy(function.body.body[1:])),
                                  ast.Variable(var_decl.name))
        return ast.Block([function.body.body[0], if_cond])

    def visit_class_decl(self, node):
        initial_namespace = self._namespace
        self._namespace += (node.name,)
        new_node = super(TypeSubstitution, self).visit_class_decl(node)
        self._namespace = initial_namespace
        return new_node

    def visit_param_decl(self, node):
        self._defs[(self._namespace, node.name)] = False
        return node

    def visit_field_decl(self, node):
        self._defs[(self._namespace, node.name)] = False
        return node

    def generate_variable_declaration(self, name, etype):
        expr = self.generator.generate_expr(etype, only_leaves=True)
        return ast.VariableDeclaration(name, expr, var_type=etype)

    def _add_is_expr(self, node, var_decl, param, old_type):
        bool_expr = self.generator.generate_expr(kt.Boolean, only_leaves=True)
        is_expr = ast.Is(ast.Variable(param.name), old_type,
                         utils.random.bool())
        and_expr = ast.LogicalExpr(
            bool_expr, is_expr,
            ast.Operator('&&')
            if bool_expr.literal == 'true'
            else ast.Operator('||'))
        use_var = False
        ret_var = []
        if var_decl:
            # This function has already declared a ret variable.
            if isinstance(node.body.body[0], ast.VariableDeclaration) and \
                    node.body.body[0].name == 'ret':
                if_body = ast.Block(deepcopy(node.body.body[1:]))
                ret_var = [var_decl]
            else:
                if_body = deepcopy(node.body)
                use_var = True
        else:
            if_body = deepcopy(node.body)
        # If we have define a variable declaration, create a reference
        # to this variable. Otherwise, we create an expresssion of the
        # expected type (same with the return type of the function).
        if var_decl:
            else_expr = ast.Variable(var_decl.name)
        elif node.get_type() == kt.Unit:
            else_expr = ast.Block([])
        else:
            else_expr = self.generator.generate_expr(node.get_type(),
                                                     only_leaves=True)
        if not is_expr.operator.is_not:
            # if (x is T) ... else var
            if_cond = ast.Conditional(
                and_expr, if_body, else_expr)
        else:
            # if (x !is T) var else ...
            if_cond = ast.Conditional(
                and_expr, else_expr, if_body)
        if var_decl:
            node.body = ast.Block(ret_var + [if_cond])
        elif node.get_type() == kt.Unit:
            node.body = ast.Block([if_cond])
        else:
            node.body = if_cond
        return use_var

    def visit_func_decl(self, node):
        initial_namespace = self._namespace
        self._namespace += (node.name,)
        new_node = super(TypeSubstitution, self).visit_func_decl(node)
        is_expression = (not isinstance(new_node.body, ast.Block) or
                         new_node.get_type() == kt.Unit)
        if not is_expression:
            # If function is not expression-based, create a variable
            # declaration holding a value whose type is the same with the
            # return type of the function.

            # This variable declaration is gonna be used, if we ll create
            # a conditional expression inside the function. E.g.,

            # fun foo(x: Any): R {
            #   val ret: R = ...
            #   if (x is T) ..
            #   else return ret
            # }
            var_decl = self.generate_variable_declaration("ret",
                                                          new_node.get_type())
        else:
            var_decl = None
        use_var = False
        for p in new_node.params:
            # Perform type widening on this function's parameters.
            old_type = p.param_type
            transform = self._type_widening(
                p, lambda x, y: setattr(x, 'param_type', y))
            if (not self._defs[(self._namespace, p.name)] or
                    not transform or new_node.body is None):
                # We are done, if one of the following applies:
                #
                # * The parameter is not used in the function.
                # * The type widening operator was not applied.
                # * The function is abstract.
                continue

            # Otherwise, replace the function body as follows
            # fun (x: T1): R = ...
            # =>
            # fun (x: T2): R = {
            #   val ret : R = ...
            #   if (x is T1) ... else ret
            # }
            use_var = self._add_is_expr(new_node, var_decl, p, old_type)
        if use_var:
            new_node.body = ast.Block([var_decl, new_node.body.body[0]])
        self._namespace = initial_namespace
        return new_node

    def visit_variable(self, node):
        namespace = self._namespace
        while len(namespace) > 0:
            if (namespace, node.name) in self._defs:
                # Specify the namespace where this variable is used.
                self._defs[(namespace, node.name)] = True
                break
            else:
                namespace = namespace[:-1]
        return node
