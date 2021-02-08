# pylint: disable=dangerous-default-value
from copy import deepcopy
from collections import defaultdict

from src import utils
from src.ir import ast, types as tp, type_utils as tu
from src.ir.context import get_decl
from src.generators import Generator
from src.generators import utils as gu
from src.transformations.base import (
    Transformation, change_depth, change_namespace)
from src.analysis.call_analysis import CNode, CallAnalysis


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

    def __init__(self, program, language, logger=None, options={}):
        super().__init__(program, language, logger, options)
        self.bt_factory = self.program.bt_factory
        self.types.remove(self.bt_factory.get_any_type())
        self.generator = Generator(
            context=self.program.context,
            language=language)
        # We are not interested in types associated with abstract classes or
        # interfaces.
        self.types = [c for c in self.types
                      if getattr(c, 'class_type', 0) ==
                      ast.ClassDeclaration.REGULAR]
        self.types.remove(self.bt_factory.get_any_type())
        self.generators = {
            self.bt_factory.get_boolean_type(): gu.gen_bool_constant,
            self.bt_factory.get_char_type(): gu.gen_char_constant,
            self.bt_factory.get_string_type(): gu.gen_string_constant,
            self.bt_factory.get_number_type(): gu.gen_integer_constant,
            self.bt_factory.get_integer_type(): gu.gen_integer_constant,
            self.bt_factory.get_byte_type(): gu.gen_integer_constant,
            self.bt_factory.get_short_type(): gu.gen_integer_constant,
            self.bt_factory.get_long_type(): gu.gen_integer_constant,
            self.bt_factory.get_float_type(): \
                lambda: gu.gen_real_constant(
                    self.bt_factory.get_float_type()),
            self.bt_factory.get_double_type(): gu.gen_real_constant,
            self.bt_factory.get_big_decimal_type(): gu.gen_real_constant,
        }

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
            # FIXME in extreme cases it may throw an RecursionError
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
        # gonna substitute one of its children or the current node.
        if node.children() and utils.random.bool():
            return super().visit_new(node)
        subclasses = tu.find_subtypes(node.class_type, self.types)
        if not subclasses:
            return node
        self.is_transformed = True
        sub_c = utils.random.choice(subclasses)
        generate = self.generators.get(sub_c, lambda: self.generate_new(sub_c))
        return generate()


class TypeSubstitution(Transformation):
    CORRECTNESS_PRESERVING = True

    def __init__(self, program, language, logger=None, options={}):
        super().__init__(program, language, logger, options)
        self.bt_factory = self.program.bt_factory
        self.generator = Generator(context=self.program.context)
        self.generator = Generator(
            context=self.program.context,
            language=language)
        # We are not interested in types associated with abstract classes or
        # interfaces.
        self._defs = defaultdict(bool)
        self._namespace = ('global',)
        self._cached_type_widenings = {}
        self._func_decls = defaultdict(set)
        self._calls = None
        self.disable_params_type_widening = self.options.get(
            "disable_params_type_widening", False)

    def get_current_class(self):
        cls_name = self._namespace[-2]
        return self.generator.context.get_decl(
            ast.GLOBAL_NAMESPACE, cls_name)

    def is_decl_used(self, decl):
        """Check if the given declaration is used in the current namespace. """
        return self._defs[(self._namespace, decl.name)]

    def _get_calls(self):
        if not self._calls:
            ca = CallAnalysis(self.program)
            _, self._calls = ca.result()
        return self._calls[CNode(self._namespace)]

    def _check_param_overriden_fun(self, fun, param, param_index, old_type,
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

        cls, p_fun = list(funcs)[0]
        current_cls_sts = [st.name
                           for st in current_cls.get_type().get_supertypes()]

        transform = True
        for cls, p_fun in funcs:

            cls_sts = [st.name for st in cls.get_type().get_supertypes()]

            if current_cls.name in cls_sts:
                child_cls_sts, parent_cls = cls_sts, current_cls
                parent_namespace = self._namespace
                parent_param = param
                child_param = p_fun.params[param_index]
                child_namespace = ast.GLOBAL_NAMESPACE + (cls.name, p_fun.name)
            elif cls.name in current_cls_sts:
                child_cls_sts, parent_cls = current_cls_sts, cls
                parent_namespace = ast.GLOBAL_NAMESPACE + (
                    cls.name, p_fun.name)
                parent_param = p_fun.params[param_index]
                child_param = param
                child_namespace = self._namespace
            else:
                # There is no parent-child relations between the current class
                # and `cls`, so there is no restriction for the type of
                # function's parameter.
                continue

            if child_param.get_type() == parent_param.get_type():
                # The type of the parameter is the same for both functions,
                # so we are OK.
                continue

            if child_param.get_type() == old_type:
                if not isinstance(parent_param.param_type, tp.AbstractType):
                    # Since, we didn't update the child method, we must not
                    # update the parent. Update the context accordingly.
                    # Note that we update the parent only if it's parameter
                    # is not abstract.
                    parent_param.param_type = deepcopy(old_type)
                    self.program.context.add_var(
                        parent_namespace, parent_param.name, parent_param)
                    transform = False
                    continue

            if not isinstance(old_type, tp.AbstractType):
                # We have to change the param type of the child method
                # back to the old one. Update context accordingly.
                if not isinstance(parent_param.param_type, tp.AbstractType):
                    # Case 1: If the parent is abstract, then we keep the
                    # old type of child.
                    child_param.param_type = deepcopy(parent_param.param_type)
                    self.program.context.add_var(
                        child_namespace, child_param.name, child_param)
                else:
                    # Case 2: If the parent is not abstract, then the child
                    # must be the same with the parent.
                    # This protects us from situtations like the following
                    #
                    # Initial Program
                    # ===============
                    # X<out T>
                    # foo(x: X<Int>) // parent
                    # override foo(x: X<Int>) // child
                    #
                    # Final Program
                    # =============
                    # foo(x: X<Number>) // parent
                    # override foo(x: X<Any>) // child wrong!!!!
                    #
                    # The following assignment ensures that the .type of
                    # child param is X<Number> and not X<Any>
                    child_param.param_type = deepcopy(old_type)
                    self.program.context.add_var(
                        child_namespace, child_param.name, child_param)
                transform = False
            else:
                supertype = [st for st in child_cls_sts
                             if st.name == parent_cls.name]
                if isinstance(supertype, tp.ParameterizedType):
                    type_param_map = {
                        t_param: supertype.type_args[i]
                        for i, t_param in enumerate(
                            supertype.t_constructor.type_parameters)
                    }
                    prev_type = type_param_map.get(old_type)
                    if prev_type:
                        child_param.param_type = deepcopy(prev_type)
                        self.program.context.add_var(
                            child_namespace, child_param.name, child_param)
                transform = False

        return transform

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
            self._cached_type_widenings[(decl.name, decl.get_type().name)] = \
                sup_t

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
        # At this point, we update the type of the parameter.
        # So we set the field to `is_transformed=True`, and update the context
        # of the program accordingly.
        self.is_transformed = True
        setter(decl, sup_t)
        self.program.context.add_var(self._namespace, decl.name, decl)
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
        bool_expr = self.generator.generate_expr(
            self.bt_factory.get_boolean_type(), only_leaves=True)
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
        elif node.get_type() == self.bt_factory.get_void_type():
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
        elif node.get_type() == self.bt_factory.get_void_type():
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
        if self.disable_params_type_widening:
            # We cannot continue because we will need to use Is
            self._namespace = initial_namespace
            return new_node

        is_expression = (not isinstance(new_node.body, ast.Block) or
                         new_node.get_type() == self.bt_factory.get_void_type())
        var_decl = None
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
            # TODO Check if there is a FieldDeclaration with the same type as
            # return type
            if not isinstance(new_node.get_type(), tp.AbstractType):
                var_decl = self.generate_variable_declaration(
                    "ret", new_node.get_type())
                self.program.context.add_var(self._namespace, var_decl.name,
                                             var_decl)
        use_var = False
        for i, param in enumerate(new_node.params):
            old_type = deepcopy(param.get_type())

            # We cannot perform type widening if there is a New as argument
            # with can_infer_type_args set to True. Consider the following
            # example
            #
            #  fun foo(x: A<Int>) {...}
            #  fun bar() {
            #      foo(A())
            #  }
            new_node_calls = self._get_calls()  # set of FunctionCall objects
            if any(isinstance(fcal.args[i], ast.New) and
                   isinstance(fcal.args[i].class_type, tp.ParameterizedType) and
                   fcal.args[i].class_type.can_infer_type_args
                   for fcal in new_node_calls):
                self._check_param_overriden_fun(
                    new_node, param, i, old_type, current_cls)
                continue

            if isinstance(param.param_type, tp.AbstractType):
                self._check_param_overriden_fun(
                    new_node, param, i, old_type, current_cls)
                continue
            is_transformed = self.is_transformed
            # Perform type widening on this function's parameters.
            transform = self._type_widening(
                param, lambda x, y: setattr(x, 'param_type', y))
            transform2 = self._check_param_overriden_fun(
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

            if isinstance(new_node.get_type(), tp.AbstractType):
                param.param_type = old_type
                self.program.context.add_var(self._namespace, param.name,
                                             param)
                self.is_transformed = is_transformed

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
        if current_cls is not None:
            self._func_decls[new_node.name].add((current_cls, new_node))
        self._namespace = initial_namespace
        self.program.context.add_func(self._namespace, new_node.name,
                                      new_node)
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


class IncorrectSubtypingSubstitution(ValueSubstitution):

    CORRECTNESS_PRESERVING = False

    def __init__(self, program, logger=None, min_expr_depth=5):
        super().__init__(program, logger)
        self.depth = 0
        self.min_expr_depth = min_expr_depth
        self._namespace = ast.GLOBAL_NAMESPACE
        self._expected_type = None
        self.error_injected = None

    def replace_value_node(self, node, exclude=[]):
        # We have already performed a transformation or the value is included
        # in a simple expression.
        if self.is_transformed or self.depth < self.min_expr_depth or (
              not self._expected_type or utils.random.bool()):
            return node
        types = [tt for tt in self.types if tt not in exclude]
        ir_type = tu.find_irrelevant_type(self._expected_type, types)
        if ir_type is None:
            # We didn't find an irrelevant type, so we can't substitute
            # the given node.
            return node

        generate = self.generators.get(ir_type,
                                       lambda: self.generate_new(ir_type))
        self.is_transformed = True
        self.error_injected = 'Expected type is {}, but {} was found'.format(
            str(self._expected_type), str(ir_type))
        return generate()

    def _get_attribute_types(self, node, name, attr_getter):
        if node.receiver is None:
            # We have an access without a receiver. Then, simply find
            # the declaration of this variable/function in the context,
            # and retrieve its types.
            decl = get_decl(self.program.context, self._namespace, name)
            if decl is None:
                return None
            return (
                [p.get_type() for p in attr_getter(decl[1])]
                if attr_getter
                else [decl[1].get_type()]
            )

        # At this point, we have an attribute access with a receiver. First,
        # find the type of its receiver, and retrieve the declaration of
        # the correspondng attribute/method from the inheritance chain of
        # the receiver.
        receiver_t = tu.get_type_hint(node.receiver, self.program.context,
                                      self._namespace)
        decl = tu.get_decl_from_inheritance(
            receiver_t, name, self.program.context)
        if decl is None:
            # We were unable to find the declaration.
            return None
        decl, receiver = decl
        if not attr_getter:
            return [decl.get_type()]
        types = []
        for p in attr_getter(decl):
            if not isinstance(p.get_type(), tp.AbstractType):
                types.append(p.get_type())
                continue

            # At this point, the declaration says that
            # the type of the current attribute is abstract. So, based on
            # the instantiation of the receiver, find its concrete type.
            type_param_map = {
                t_param: receiver.type_args[i]
                for i, t_param in enumerate(
                    receiver.t_constructor.type_parameters)
            }
            concrete_type = type_param_map.get(p.get_type())
            assert concrete_type is not None
            types.append(concrete_type)
        return types

    def _replace_node_args(self, node, types):
        receiver = getattr(node, 'receiver', None)
        new_children = [receiver] if receiver else []
        previous = self._expected_type
        for i, t in enumerate(types):
            if t != self.bt_factory.get_any_type():
                self._expected_type = t
                new_children.append(self.visit(node.args[i]))
            else:
                # We can't perform the substitution, when the expected type
                # is Any, as any type is valid.
                new_children.append(node.args[i])
        self._expected_type = previous
        node.update_children(new_children)
        return node

    @change_namespace
    def visit_class_decl(self, node):
        return super().visit_class_decl(node)

    @change_namespace
    def visit_func_decl(self, node):
        previous = self._expected_type
        self._expected_type = (
            node.get_type()
            if node.get_type() != self.bt_factory.get_void_type() else None)
        new_node = super().visit_func_decl(node)
        self._expected_type = previous
        return new_node

    @change_depth
    def visit_integer_constant(self, node):
        return self.replace_value_node(
            node, exclude=[
                self.bt_factory.get_byte_type(),
                self.bt_factory.get_short_type(),
                self.bt_factory.get_integer_type(),
                self.bt_factory.get_long_type()])

    @change_depth
    def visit_real_constant(self, node):
        return self.replace_value_node(node, exclude=[])

    @change_depth
    def visit_char_constant(self, node):
        return self.replace_value_node(node, exclude=[])

    @change_depth
    def visit_string_constant(self, node):
        return self.replace_value_node(node, exclude=[])

    @change_depth
    def visit_boolean_constant(self, node):
        return self.replace_value_node(node, exclude=[])

    @change_depth
    def visit_variable(self, node):
        vardecl = get_decl(self.program.context, self._namespace, node.name)
        assert vardecl is not None
        _, decl = vardecl
        if decl.get_type() == self.bt_factory.get_any_type():
            return node
        return self.replace_value_node(node, exclude=[])

    @change_depth
    def visit_var_decl(self, node):
        # If the type of variable is Any or we perform type inference,
        # then, it's not safe to perfom the substitution.
        if (node.get_type() == self.bt_factory.get_any_type() or
                node.var_type is None):
            return node
        previous = self._expected_type
        self._expected_type = node.get_type()
        new_node = super().visit_var_decl(node)
        self._expected_type = previous
        return new_node

    def visit_logical_expr(self, node):
        previous = self._expected_type
        self._expected_type = self.bt_factory.get_boolean_type()
        new_node = super().visit_logical_expr(node)
        self._expected_type = previous
        return new_node

    @change_depth
    def visit_equality_expr(self, node):
        previous = self._expected_type
        self._expected_type = None
        new_node = super().visit_equality_expr(node)
        self._expected_type = previous
        return new_node

    @change_depth
    def visit_comparison_expr(self, node):
        return node

    @change_depth
    def visit_arith_expr(self, node):
        return node

    @change_depth
    def visit_conditional(self, node):
        previous = self._expected_type
        self._expected_type = self.bt_factory.get_boolean_type()
        cond = self.visit(node.cond)
        self._expected_type = previous
        expr1 = self.visit(node.true_branch)
        expr2 = self.visit(node.false_branch)
        node.update_children([cond, expr1, expr2])
        return node

    @change_depth
    def visit_is(self, node):
        return node

    @change_depth
    def visit_new(self, node):
        # We call the constructor of Any so, there's nothing to replace.
        if node.class_type == self.bt_factory.get_any_type():
            return node
        if utils.random.bool():
            return self.replace_value_node(node, exclude=[])
        _, cls = get_decl(self.program.context, ast.GLOBAL_NAMESPACE,
                          node.class_type.name)
        if not cls.is_parameterized():
            field_types = [f.get_type() for f in cls.fields]
        else:
            type_param_map = {
                t_param: node.class_type.type_args[i]
                for i, t_param in enumerate(
                    node.class_type.t_constructor.type_parameters)
            }
            field_types = []
            for f in cls.fields:
                if isinstance(f.get_type(), tp.AbstractType) and (
                        node.class_type.can_infer_type_args):
                    field_types.append(self.bt_factory.get_any_type())
                else:
                    field_types.append(type_param_map.get(f.get_type(),
                                                          f.get_type()))
        return self._replace_node_args(node, field_types)

    @change_depth
    def visit_field_access(self, node):
        # TODO handle receiver of field access.
        return node
        # rec_t = tu.get_type_hint(node.expr, self.program.context,
        #                          self._namespace)
        # if not rec_t:
        #     return node
        # previous = self._expected_type
        # self._expected_type = rec_t
        # new_rec = self.visit(node.expr)
        # self._expected_type = previous
        # node.update_children([new_rec])
        # return node

    @change_depth
    def visit_func_call(self, node):
        param_types = self._get_attribute_types(node, node.func,
                                                lambda x: x.params)
        # We were not able to find the parameters of the function, so it's
        # not safe to perform the substitution here.
        if param_types is None:
            return node

        return self._replace_node_args(node, param_types)

    @change_depth
    def visit_assign(self, node):
        lhs_type = self._get_attribute_types(node, node.name, None)
        if lhs_type is None:
            return node

        previous = self._expected_type
        self._expected_type = lhs_type[0]
        children = [node.receiver] if node.receiver else []
        expr_node = self.visit(node.expr)
        node.update_children(children + [expr_node])
        self._expected_type = previous
        return node
