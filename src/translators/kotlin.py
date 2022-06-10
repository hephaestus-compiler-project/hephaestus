from src.ir import ast, kotlin_types as kt, types as tp, type_utils as tu
from src.translators.base import BaseTranslator


def append_to(visit):
    def inner(self, node):
        self._nodes_stack.append(node)
        res = visit(self, node)
        self._nodes_stack.pop()
    return inner


class KotlinTranslator(BaseTranslator):

    filename = "program.kt"
    incorrect_filename = "incorrect.kt"
    executable = "program.jar"

    def __init__(self, package=None, options={}):
        super().__init__(package, options)
        self._children_res = []
        self.ident = 0
        self.is_unit = False
        self.is_lambda = False
        self._cast_integers = False
        self.context = None

        # We need nodes_stack to assign lambdas to vars when needed.
        # Specifically, in visit_lambda we use `var y = ` as a prefix only if
        # parent node is a block and its parent is a function declaration that
        # return Unit.
        self._nodes_stack = [None]

    def _reset_state(self):
        self._children_res = []
        self.ident = 0
        self.is_unit = False
        self.is_lambda = False
        self._cast_integers = False
        self._nodes_stack = [None]
        self.context = None

    @staticmethod
    def get_filename():
        return KotlinTranslator.filename

    @staticmethod
    def get_incorrect_filename():
        return KotlinTranslator.incorrect_filename

    def type_arg2str(self, t_arg):
        if not isinstance(t_arg, tp.WildCardType):
            return self.get_type_name(t_arg)
        if t_arg.is_invariant():
            return "*"
        elif t_arg.is_covariant():
            return "out " + self.get_type_name(t_arg.bound)
        else:
            return "in " + self.get_type_name(t_arg.bound)

    def get_type_name(self, t):
        if t.is_wildcard():
            t = t.get_bound_rec()
            return self.get_type_name(t)
        t_constructor = getattr(t, 't_constructor', None)
        if not t_constructor:
            return t.get_name()
        if isinstance(t_constructor, kt.SpecializedArrayType):
            return "{}Array".format(self.get_type_name(
                t.type_args[0]))
        return "{}<{}>".format(t.name, ", ".join([self.type_arg2str(ta)
                                                  for ta in t.type_args]))

    def pop_children_res(self, children):
        len_c = len(children)
        if not len_c:
            return []
        res = self._children_res[-len_c:]
        self._children_res = self._children_res[:-len_c]
        return res

    def visit_program(self, node):
        self.context = node.context
        children = node.children()
        for c in children:
            c.accept(self)
        if self.package:
            package_str = 'package ' + self.package + '\n'
        else:
            package_str = ''
        self.program = package_str + '\n\n'.join(
            self.pop_children_res(children))

    @append_to
    def visit_block(self, node):
        children = node.children()
        is_unit = self.is_unit
        is_lambda = self.is_lambda
        self.is_unit = False
        self.is_lambda = False
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        res = "{" if not is_lambda else ""
        res += "\n" + "\n".join(children_res[:-1])
        if children_res[:-1]:
            res += "\n"
        ret_keyword = "return " if node.is_func_block and not is_unit and not is_lambda else ""
        if children_res:
            res += " " * self.ident + ret_keyword + \
                   children_res[-1] + "\n" + \
                   " " * self.ident
        else:
            res += " " * self.ident + ret_keyword + "\n" + \
                   " " * self.ident
        res += "}" if not is_lambda else ""
        self.is_unit = is_unit
        self.is_lambda = is_lambda
        self._children_res.append(res)

    @append_to
    def visit_super_instantiation(self, node):
        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        if node.args is None:
            self._children_res.append(self.get_type_name(node.class_type))
            return
        self._children_res.append(
            self.get_type_name(node.class_type) + "(" + ", ".join(
                children_res) + ")")

    @append_to
    def visit_class_decl(self, node):
        old_ident = self.ident
        self.ident += 2
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        field_res = [children_res[i]
                     for i, _ in enumerate(node.fields)]
        len_fields = len(field_res)
        superclasses_res = [children_res[i + len_fields]
                            for i, _ in enumerate(node.superclasses)]
        len_supercls = len(superclasses_res)
        function_res = [children_res[i + len_fields + len_supercls]
                        for i, _ in enumerate(node.functions)]
        len_functions = len(function_res)
        type_parameters_res = ", ".join(
            children_res[len_fields + len_supercls + len_functions:])

        is_sam = tu.is_sam(self.context, cls_decl=node)
        class_prefix = "interface" if is_sam else node.get_class_prefix()

        res = "{ident}{f}{o}{p} {n}".format(
            ident=" " * old_ident,
            f="fun " if is_sam else "",
            o="open " if (not node.is_final and
                          node.class_type != ast.ClassDeclaration.INTERFACE and
                          not is_sam) else "",
            p=class_prefix,
            n=node.name,
        )

        if type_parameters_res:
            res = "{}<{}>".format(res, type_parameters_res)
        if field_res:
            res = "{}({})".format(
                res, ", ".join(field_res))
        if superclasses_res:
            res += ": " + ", ".join(superclasses_res)
        if function_res:
            res += " {\n" + "\n\n".join(
                function_res) + "\n" + " " * old_ident + "}"
        self.ident = old_ident
        self._children_res.append(res)

    @append_to
    def visit_type_param(self, node):
        self._children_res.append("{}{}{}{}".format(
            node.variance_to_string(),
            ' ' if node.variance != tp.Invariant else '',
            node.name,
            ': ' + (
                self.get_type_name(node.bound)
                if node.bound is not None
                else kt.Any.name
            )
        ))

    @append_to
    def visit_var_decl(self, node):
        old_ident = self.ident
        prefix = " " * self.ident
        self.ident = 0
        children = node.children()
        prev = self._cast_integers
        if node.var_type is None:
            self._cast_integers = True
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        var_type = "val " if node.is_final else "var "
        res = prefix + var_type + node.name
        if node.var_type is not None:
            res += ": " + self.get_type_name(node.var_type)
        res += " = " + children_res[0]
        self.ident = old_ident
        self._cast_integers = prev
        self._children_res.append(res)

    @append_to
    def visit_call_argument(self, node):
        old_ident = self.ident
        self.ident = 0
        children = node.children()
        for c in node.children():
            c.accept(self)
        self.ident = old_ident
        children_res = self.pop_children_res(children)
        res = children_res[0]
        if node.name:
            res = node.name + " = " + res
        self._children_res.append(res)

    @append_to
    def visit_field_decl(self, node):
        prefix = 'open ' if node.can_override else ''
        prefix += '' if not node.override else 'override '
        prefix += 'val ' if node.is_final else 'var '
        res = prefix + node.name + ": " + self.get_type_name(node.field_type)
        self._children_res.append(res)

    @append_to
    def visit_param_decl(self, node):
        old_ident = self.ident
        self.ident = 0
        children = node.children()
        for c in node.children():
            c.accept(self)
        self.ident = old_ident
        vararg_str = 'vararg ' if node.vararg else ''
        # Recall that varargs ara actually arrays in the signature of
        # the corresponding parameters.
        param_type = (
            node.param_type.type_args[0]
            if node.vararg and isinstance(node.param_type,
                                          tp.ParameterizedType)
            else node.param_type)
        res = vararg_str + node.name + ": " + self.get_type_name(param_type)
        if len(children):
            children_res = self.pop_children_res(children)
            res += " = " + children_res[0]
        self._children_res.append(res)

    @append_to
    def visit_func_decl(self, node):
        old_ident = self.ident
        self.ident += 2
        children = node.children()
        prev_is_unit = self.is_unit
        self.is_unit = node.get_type() == kt.Unit
        prev_c = self._cast_integers
        is_expression = not isinstance(node.body, ast.Block)
        if is_expression:
            self._cast_integers = True
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        param_res = [children_res[i] for i, _ in enumerate(node.params)]
        len_params = len(node.params)
        len_type_params = len(node.type_parameters)
        type_parameters_res = ", ".join(
            children_res[len_params:len_type_params + len_params])
        body_res = children_res[-1] if node.body else ''
        prefix = " " * old_ident
        prefix += "" if node.is_final else "open "
        prefix += "" if not node.override else "override "
        prefix += "" if node.body is not None else "abstract "
        type_params = (
            "<" + type_parameters_res + ">" if type_parameters_res else "")
        res = prefix + "fun " + type_params + node.name + "(" + ", ".join(
            param_res) + ")"
        if node.ret_type:
            res += ": " + self.get_type_name(node.ret_type)
        if body_res:
            sign = "=" if is_expression and node.get_type() != kt.Unit else ""
            res += " " + sign + "\n" + body_res
        self.ident = old_ident
        self.is_unit = prev_is_unit
        self._cast_integers = prev_c
        self._children_res.append(res)

    @append_to
    def visit_lambda(self, node):
        def inside_block_unit_function():
            if (isinstance(self._nodes_stack[-2], ast.Block) and
                    isinstance(self._nodes_stack[-3], (ast.Lambda,
                               ast.FunctionDeclaration)) and
                    self._nodes_stack[-3].ret_type == kt.Unit):
                return True
            return False

        old_ident = self.ident
        is_expression = not isinstance(node.body, ast.Block)
        self.ident = 0 if is_expression else self.ident + 2
        children = node.children()

        prev_is_unit = self.is_unit
        prev_is_lambda = self.is_lambda
        self.is_unit = node.get_type() == kt.Unit
        use_lambda = (isinstance(self._nodes_stack[-2], ast.VariableDeclaration)
                      and tu.is_sam(self.context,
                                    etype=self._nodes_stack[-2].inferred_type))
        self.is_lambda = use_lambda

        sam_name = ""
        if use_lambda:
            sam_name = self.get_type_name(self._nodes_stack[-2].inferred_type)

        prev_c = self._cast_integers
        if is_expression:
            self._cast_integers = True

        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        self.ident = old_ident

        param_res = [children_res[i] for i, _ in enumerate(node.params)]
        body_res = children_res[-1] if node.body else ''

        if is_expression or use_lambda:
            # use the lambda syntax: { params -> stmt }
            res = "{var}{sam_name}{{{params} -> {body}}}".format(
                var="" if not inside_block_unit_function() else "var y = ",
                sam_name=sam_name if use_lambda else "",
                params=", ".join(param_res),
                body=body_res
            )
        else:
            # Use the fun syntax : fun (params): ret_type { ... }
            res = "{ident}fun ({params}){ret_type} {body}".format(
                ident=" " * self.ident,
                params=", ".join(param_res),
                ret_type=": " + self.get_type_name(node.ret_type) \
                    if node.ret_type else "",
                body=body_res
            )

        self.is_unit = prev_is_unit
        self.is_lambda = prev_is_lambda
        self._cast_integers = prev_c
        self._children_res.append(res)

    @append_to
    def visit_bottom_constant(self, node):
        bottom = "{}TODO(){}".format(
            "(" if node.t else "",
            " as " + self.get_type_name(node.t) + ")" if node.t else ""
        )
        self._children_res.append((self.ident * " ") + bottom)

    @append_to
    def visit_integer_constant(self, node):
        if not self._cast_integers:
            self._children_res.append(" " * self.ident + str(node.literal))
            return
        integer_types = {
            kt.Long: ".toLong()",
            kt.Short: ".toShort()",
            kt.Byte: ".toByte()",
            kt.Number: " as Number",
        }
        suffix = integer_types.get(node.integer_type, "")
        literal = str(node.literal)
        literal = (
            "(" + literal + ")"
            if suffix and literal[0] == '-'
            else literal
        )
        self._children_res.append(" " * self.ident + literal + suffix)

    @append_to
    def visit_real_constant(self, node):
        real_types = {
            kt.Float: "f"
        }
        suffix = real_types.get(node.real_type, "")
        self._children_res.append(
            " " * self.ident + str(node.literal) + suffix)

    @append_to
    def visit_char_constant(self, node):
        self._children_res.append("{}'{}'".format(
            " " * self.ident, node.literal))

    @append_to
    def visit_string_constant(self, node):
        self._children_res.append('{}"{}"'.format(
            " " * self.ident, node.literal))

    @append_to
    def visit_boolean_constant(self, node):
        self._children_res.append(" " * self.ident + str(node.literal))

    @append_to
    def visit_array_expr(self, node):
        is_specialized = isinstance(
            node.array_type.t_constructor, kt.SpecializedArrayType)
        if not node.length:
            if not is_specialized:
                self._children_res.append("{}emptyArray<{}>()".format(
                    " " * self.ident,
                    self.get_type_name(node.array_type.type_args[0])))
            else:
                # Specialized array
                t_arg = self.get_type_name(node.array_type.type_args[0])
                self._children_res.append("{}{}Array(0)".format(
                    " " * self.ident, t_arg))
            return
        old_ident = self.ident
        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        self.ident = old_ident

        template = (
            "{}arrayOf<{}>({})"
            if not is_specialized
            else "{}{}ArrayOf({})"
        )
        t_arg = self.get_type_name(node.array_type.type_args[0])
        if is_specialized:
            t_arg = t_arg.lower()
        return self._children_res.append(template.format(
            " " * self.ident,
            t_arg,
            ", ".join(children_res)))

    @append_to
    def visit_variable(self, node):
        self._children_res.append(" " * self.ident + node.name)

    @append_to
    def visit_binary_op(self, node):
        old_ident = self.ident
        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        res = "{}({} {} {})".format(
            " " * old_ident, children_res[0], node.operator,
            children_res[1])
        self.ident = old_ident
        self._children_res.append(res)

    def visit_logical_expr(self, node):
        self.visit_binary_op(node)

    def visit_equality_expr(self, node):
        prev = self._cast_integers
        # When we encounter equality epxressions,
        # we need to explicitly cast integer literals.
        # Kotlin does not permit operations like the following
        # val d: Short = 1
        # d == 2
        #
        # As a workaround, we can do
        # d == 2.toShort()
        self._cast_integers = True
        self.visit_binary_op(node)
        self._cast_integers = prev

    def visit_comparison_expr(self, node):
        self.visit_binary_op(node)

    def visit_arith_expr(self, node):
        self.visit_binary_op(node)

    @append_to
    def visit_conditional(self, node):
        old_ident = self.ident
        self.ident += 2
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        res = "{}(if ({})\n{}\n{}else\n{})".format(
            " " * old_ident, children_res[0][self.ident:], children_res[1],
            " " * old_ident, children_res[2])
        self.ident = old_ident
        self._children_res.append(res)

    @append_to
    def visit_is(self, node):
        old_ident = self.ident
        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        res = "{}{} {} {}".format(
            " " * old_ident, children_res[0], str(node.operator),
            node.rexpr.name)
        self.ident = old_ident
        self._children_res.append(res)

    @append_to
    def visit_new(self, node):
        old_ident = self.ident
        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        self.ident = old_ident
        # Remove type arguments from Parameterized Type
        if getattr(node.class_type, 'can_infer_type_args', None) is True:
            self._children_res.append("{}({})".format(
                " " * self.ident + node.class_type.name,
                ", ".join(children_res)))
        else:
            self._children_res.append("{}({})".format(
                " " * self.ident + self.get_type_name(node.class_type),
                ", ".join(children_res)))

    @append_to
    def visit_field_access(self, node):
        old_ident = self.ident
        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)
        children_res = self.pop_children_res(children)
        self.ident = old_ident
        receiver_expr = (
            '({})'.format(children_res[0])
            if isinstance(node.expr, ast.BottomConstant)
            else children_res[0]
        )
        res = "{}{}.{}".format(" " * self.ident, receiver_expr, node.field)
        self._children_res.append(res)

    @append_to
    def visit_func_ref(self, node):
        old_ident = self.ident

        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)

        self.ident = old_ident

        children_res = self.pop_children_res(children)
        # TODO handle lambdas
        receiver = children_res[0] if children_res else ""
        receiver += "::"
        res = "{ident}{receiver}{name}".format(
            ident=" " * self.ident,
            receiver=receiver,
            name=node.func
        )
        self._children_res.append(res)

    @append_to
    def visit_func_call(self, node):
        old_ident = self.ident
        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)
        self.ident = old_ident
        children_res = self.pop_children_res(children)
        type_args = (
            "<" + ",".join(
                [self.get_type_name(t) for t in node.type_args]) + ">"
            if not node.can_infer_type_args and node.type_args
            else ""
        )
        if node.receiver:
            receiver_expr = (
                '({})'.format(children_res[0])
                if isinstance(node.receiver, ast.BottomConstant)
                else children_res[0]
            )
            res = "{}{}.{}{}({})".format(
                " " * self.ident, receiver_expr, node.func,
                type_args,
                ", ".join(children_res[1:]))
        else:
            res = "{}{}{}({})".format(
                " " * self.ident, node.func, type_args,
                ", ".join(children_res))
        self._children_res.append(res)

    @append_to
    def visit_assign(self, node):
        old_ident = self.ident
        prev = self._cast_integers
        self._cast_integers = True
        self.ident = 0
        children = node.children()
        for c in children:
            c.accept(self)
        self.ident = old_ident
        children_res = self.pop_children_res(children)
        if node.receiver:
            receiver_expr = (
                '({})'.format(children_res[0])
                if isinstance(node.receiver, ast.BottomConstant)
                else children_res[0]
            )
            res = "{}{}.{} = {}".format(" " * old_ident, receiver_expr,
                                        node.name, children_res[1])
        else:
            res = "{}{} = {}".format(" " * old_ident, node.name,
                                     children_res[0])
        self.ident = old_ident
        self._cast_integers = prev
        self._children_res.append(res)
