from copy import deepcopy
from collections import defaultdict

from src import utils
from src.ir import ast, types as tp, type_utils as tu
from src.ir import kotlin_types as kt
from src.generators import Generator
from src.generators import utils as gu
from src.transformations.base import Transformation


def create_function_block(function, is_expr, var_decl, declared=False):
    if not declared:
        if_cond = ast.Conditional(is_expr, deepcopy(function.body),
                                  ast.Variable(var_decl.name))
        return ast.Block([var_decl, if_cond])
    if_cond = ast.Conditional(is_expr,
                              ast.Block(deepcopy(function.body.body[1:])),
                              ast.Variable(var_decl.name))
    return ast.Block([function.body.body[0], if_cond])


class ValueSubstitution(Transformation):

    CORRECTNESS_PRESERVING = True
    NAME = 'Value Substitution'

    def __init__(self, program, logger=None):
        super().__init__(program, logger)
        self.types.remove(kt.Any)
        self.generator = Generator(context=self.program.context)
        # We are not interested in types associated with abstract classes or
        # interfaces.
        self.types = [c for c in self.types
                      if getattr(c, 'class_type', 0) == ast.ClassDeclaration.REGULAR]

    def _generate_new(self, class_decl, class_type, params_map):
        return ast.New(
            class_type,
            args=[self.generator.generate_expr(
                params_map.get(f.field_type, f.field_type), only_leaves=True)
                  for f in class_decl.fields])

    def generate_new(self, etype):
        class_decl = self.generator.context.get_decl(
            ast.GLOBAL_NAMESPACE, etype.name)
        if isinstance(etype, tp.ParameterizedType):
            # The etype is a parameterized type, so this case comes from
            # variance. Therefore, we first need to get the class_declaration
            # of this type, and initialize the map of type parameters.
            params_map = {
                t_p: etype.type_args[i]
                for i, t_p in enumerate(etype.t_constructor.type_parameters)
            }
            return self._generate_new(class_decl, etype, params_map)

        if isinstance(etype, tp.TypeConstructor):
            # We selected a class that is parameterized. So before its use,
            # we need to instantiate it.
            class_type, params_map = tu.instantiate_type_constructor(
                etype, self.types)
        else:
            class_type, params_map = etype, {}
        return self._generate_new(class_decl, class_type, params_map)

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
            return super().visit_new(node)
        subclasses = tu.find_subtypes(node.class_type, self.types)
        if not subclasses:
            return node
        self.is_transformed = True
        sub_c = utils.random.choice(subclasses)
        generators = {
            kt.Boolean: gu.gen_bool_constant,
            kt.Char: gu.gen_char_constant,
            kt.String: gu.gen_string_constant,
            kt.Number: gu.gen_integer_constant,
            kt.Integer: gu.gen_integer_constant,
            kt.Byte: gu.gen_integer_constant,
            kt.Short: gu.gen_integer_constant,
            kt.Long: gu.gen_integer_constant,
            kt.Float: lambda: gu.gen_real_constant(kt.Float),
            kt.Double: gu.gen_real_constant,
        }
        generate = generators.get(sub_c, lambda: self.generate_new(sub_c))
        return generate()


class TypeSubstitution(Transformation):
    CORRECTNESS_PRESERVING = True
    NAME = 'Type Substitution (Widening/Narrowing)'

    def __init__(self, program, logger=None):
        super().__init__(program, logger)
        self.generator = Generator(context=self.program.context)
        # We are not interested in types associated with abstract classes or
        # interfaces.
        self._defs = defaultdict(bool)
        self._namespace = ('global',)
        self._cached_type_widenings = {}
        self._func_decls = defaultdict(set)

    def get_current_class(self):
        cls_name = self._namespace[-2]
        return self.generator.context.get_decl(
            ast.GLOBAL_NAMESPACE, cls_name)

    def is_decl_used(self, decl):
        """Check if the given declaration is used in the current namespace. """
        return self._defs[(self._namespace, decl.name)]

    def _check_param_type(self, fun, param, param_index, old_type,
                          current_cls):
        # The signature of the function defined in the parent class must
        # be the same with that defined in the child class. The following
        # example demonstrates that sometimes, this is not the case
        #
        # class A<out T>
        #
        # interface B {
        #  fun foo(x: A<Any>): Unit
        # }
        #
        # class C: B {
        #  override fun foo(x: A<String>) {}
        # }

        # This function ensures that the signature of the function is the
        # same in both child and parent classes.
        funcs = self._func_decls.get(fun.name)
        if not funcs:
            return True

        for cls, p_fun in funcs:
            if cls.inherits_from(current_cls):
                parent_param = param
                child_param = p_fun.params[param_index]
            elif current_cls.inherits_from(cls):
                parent_param = p_fun.params[param_index]
                child_param = param
            else:
                continue

            if child_param.get_type() == parent_param.get_type():
                continue

            if child_param.get_type() == old_type:
                parent_param.param_type = deepcopy(old_type)
                return False

            if parent_param.get_type() == old_type or (
                    isinstance(parent_param.get_type(), tp.AbstractType)):
                if not isinstance(old_type, tp.AbstractType):
                    child_param.param_type = deepcopy(old_type)
                    return False

        return True

    def _type_widening(self, decl, setter):
        superclasses = tu.find_supertypes(decl.get_type(), self.types,
                                          concrete_only=True)
        if not superclasses:
            return False
        # Inspect cached type widenings for this particular declaration.
        sup_t = self._cached_type_widenings.get(
            (decl.name, decl.get_type().name))

        if sup_t is None:
            sup_t = utils.random.choice(superclasses)
            self._cached_type_widenings[(decl.name, decl.get_type().name)] = sup_t

        if isinstance(decl.get_type(), tp.ParameterizedType):
            # The current type of the declaration is parameterized type.

            # This comes with some restrictions. If this declaration is used
            # in the current namespace, unfortunately, we cannot perform
            # a smart cast, due to type erasure e.g.,
            #     if (decl is X<String>)
            #
            # Therefore, we don't perform type widening in this case.
            if self.is_decl_used(decl):
                return False
        self.is_transformed = True
        setter(decl, sup_t)
        return True

    def visit_class_decl(self, node):
        initial_namespace = self._namespace
        self._namespace += (node.name,)
        new_node = super().visit_class_decl(node)
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

    def no_smart_cast(self, node, decl, transform, old_type):
        old_tc = getattr(old_type, 't_constructor', None)
        new_tc = getattr(decl.get_type(), 't_constructor', None)
        if old_tc and old_tc == new_tc:
            # We are in a case like the following:
            # old_type (subtype)   = A<String>
            # new_type (supertype) = A<Any>
            # No need for smart cast.
            return True

        return not self.is_decl_used(decl) or not transform or (
            node.body is None)

    def visit_func_decl(self, node):
        initial_namespace = self._namespace
        self._namespace += (node.name,)
        current_cls = self.get_current_class()
        new_node = super().visit_func_decl(node)
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
        for i, param in enumerate(new_node.params):
            old_type = deepcopy(param.get_type())
            if isinstance(param.param_type, tp.AbstractType):
                self._check_param_type(new_node, param, i, old_type,
                                       current_cls)
                continue
            # Perform type widening on this function's parameters.
            transform = self._type_widening(
                param, lambda x, y: setattr(x, 'param_type', y))
            transform2 = self._check_param_type(
                new_node, param, i, old_type, current_cls)
            transform = transform and transform2
            # We cannot perform type widening in abstract types.
            if self.no_smart_cast(new_node, param, transform, old_type):
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
            use_var = self._add_is_expr(new_node, var_decl, param, old_type)
        if use_var:
            new_node.body = ast.Block([var_decl, new_node.body.body[0]])
        if node.func_type == ast.FunctionDeclaration.CLASS_METHOD:
            self._func_decls[new_node.name].add((current_cls, new_node))
        self._namespace = initial_namespace
        return new_node

    def visit_variable(self, node):
        namespace = self._namespace
        while len(namespace) > 0:
            if (namespace, node.name) in self._defs:
                # Specify the namespace where this variable is used.
                self._defs[(namespace, node.name)] = True
                break
            namespace = namespace[:-1]
        return node
