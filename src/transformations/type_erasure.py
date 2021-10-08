# pylint: disable=too-many-instance-attributes,dangerous-default-value
from copy import deepcopy, copy
import itertools
from typing import Tuple

from src.ir import ast
from src.ir import types
from src.ir import type_utils as tp
from src.transformations.base import Transformation, change_namespace
from src.analysis import type_dependency_analysis as tda
from src.analysis.use_analysis import UseAnalysis, GNode


def deepcopynode(func):
    """Deepcopy the node before change it.

    We want this to not propagate changes to all occurrences of this node.
    This happens because many New Declarations reference to a single object
    (pointer).
    """
    def inner(self, node):
        node = deepcopy(node)
        new_node = func(self, node)
        return new_node
    return inner


class TypeErasure(Transformation):
    CORRECTNESS_PRESERVING = True

    def __init__(self, program, language, logger=None, options={}):
        super().__init__(program, language, logger, options)
        self._namespace = ast.GLOBAL_NAMESPACE

    @change_namespace
    def visit_class_decl(self, node):
        return super().visit_class_decl(node)

    @change_namespace
    def visit_func_decl(self, node):
        t_an = tda.TypeDependencyAnalysis(self.program,
                                          namespace=self._namespace[:-1])
        t_an.visit(node)
        type_graph = t_an.result()
        ommitable_nodes = [n for n in type_graph.keys()
                           if n.is_omittable()]
        # We enumerate all combinations of omittable nodes.
        combinations = [
            [
                i
                for comb in itertools.combinations(ommitable_nodes, k)
                for i in comb
            ]
            for k in range(len(ommitable_nodes), 0, -1)
        ]
        for combination in combinations:
            type_graph = copy(type_graph)
            # We are trying to find the maximal combination that is feasible.
            if tda.is_combination_feasible(type_graph, combination):
                for g_node in combination:
                    self.is_transformed = True
                    if isinstance(g_node, tda.DeclarationNode):
                        g_node.decl.var_type = None
                    if isinstance(g_node,
                                  tda.TypeConstructorInstantiationCallNode):
                        g_node.t.can_infer_type_args = True
                break
        return node


class TypeArgumentErasureSubstitution(Transformation):
    """Remove type information when possible:

       Remove type arguments from ParameterizedTypes instantiations
    """
    CORRECTNESS_PRESERVING = True

    def __init__(self, program, language, logger=None, options={}):
        super().__init__(program, language, logger, options)
        self._namespace: tuple = ast.GLOBAL_NAMESPACE

        # We use this variable to find to which variable does a `New` assignment
        # belongs.
        # (namespace, var_decl)
        self._var_decl: Tuple[Tuple, ast.VariableDeclaration] = None

        # We use this variable to find to which assignment does a `New`
        # assignment belongs.
        self._assign: ast.Assignment = None

        # We use this variable to find the return statements of function
        # declarations. We don't want to infer type arguments for `New` nodes
        # that are in return statements. We select to infer type arguments for
        # such statements in _check_func_decl_infer
        self._ret_stmt: ast.Expr = None

        # A stack of tuples with expressions and their types provided by smart
        self.smart_casts = []

    def get_parent_decl(self, namespace):
        if namespace == ast.GLOBAL_NAMESPACE:
            return self.program
        return self.program.context.get_decl(namespace[:-1], namespace[-1])

    @deepcopynode
    def _check_new_infer(self, node: ast.New):
        """In case of ParameterizedType check if type arguments can be inferred.
        """
        # Check if all type parameters of constructor are used in field
        # declarations.
        # For example, in this case we can infer the type of type arguments
        #   class A<T, K> (val x: T, val y: K)
        #   val a = A("a", if (true) -1 else "a")
        # whereas in the following case we can't
        #   class A<T, K> (val x: T)
        #   val a = A("a") // not enough information to infer type variable K
        # TODO Add randomness
        if (isinstance(node.class_type, types.ParameterizedType) and
                not node.class_type.can_infer_type_args):
            cdecl = self.program.context.get_classes(
                self._namespace, glob=True)[node.class_type.name]
            if cdecl.all_type_params_in_fields():
                # Check if type argument are number-related types and if we are
                # in a var_decl of a number-related type.
                # For example, we can't infer the type argument in the
                # following case.
                #   class A<T>(T a)
                #   val x: Long = A<Long>(43).a
                # We will miss some cases when there is a cast. Maybe we can
                # handle such cases in the translator.
                #   class A<T>(T a)
                #   class B(A<Long> b)
                #   val x: Long = B(A<Long>(43).toLong()).b.a
                if (self._var_decl is not None and
                        self._var_decl[1].inferred_type in
                        self.program.bt_factory.get_number_types() and
                        any(ta in self.program.bt_factory.get_number_types()
                            for ta in node.class_type.type_args)):
                    return node
                # If the node is the return statement of a function or if it is
                # in the return statement of a function, then we cannot infer
                # its type arguments in case the function hasn't ret_type
                # declared.
                # For example consider the following scenario.
                #   open class A
                #   open class B<T: A>(var x: T)
                #   class C: A()
                #   fun foo() = B(C())
                #   val y: B<A> = foo()  // error
                if self._ret_stmt and tp.node_in_expr(node, self._ret_stmt):
                    return node
                # In next case we should check if there is a flow from the
                # variable to another variable, or function call, or New,
                # that has a different type than the new inferred type.
                # Example:
                #
                #  class A<T>(val x: T)
                #  fun foo(x: A<Any>) {}
                #  var a = A<Any>('x') // We cannot infer type arguments
                #  foo(a)              // because it will break here
                #
                # Currently, we cannot find the inferred type if we remove
                # the type arguments, thus; we simple check if there is a
                # flow from the variable to anywhere.
                if (self._var_decl is not None and
                        not self._var_decl[1].var_type):
                    namespace, var_decl = self._var_decl
                    analysis = UseAnalysis(self.program)
                    parent_decl = self.get_parent_decl(namespace)
                    if parent_decl is not None:
                        initial_namespace = namespace[:-1]
                        analysis.set_namespace(initial_namespace)
                        analysis.visit(parent_decl)
                        use_graph = analysis.result()
                        gnode = GNode(namespace, var_decl.name)
                        if len(use_graph[gnode]) != 0:
                            return node
                # If assign is a field of the analyzed new and its type is a
                # type parameter in the class declaration, then we should check
                # that the appropriate argument in the new has the same type
                # with the expr.
                #
                #  open class A {}
                #  class B: A() {}
                #  class C<T: A>(var x: T) {}
                #
                #  fun main() {
                #    C(B()).x = A() // Error Here
                #  }
                if (self._assign is not None and
                        # OK assign is a field of this class, and its type
                        # is a type parameter
                        any(f for f in cdecl.fields
                            if f.name == self._assign.name)):
                    # We should now check if the argument has the same type
                    # with the expression of assign.
                    arg_pos = next(i for i, f in enumerate(cdecl.fields)
                                   if f.name == self._assign.name)
                    arg_type = tp.get_type_hint(
                        node.args[arg_pos], self.program.context,
                        self._namespace, self.program.bt_factory,
                        self.types, smart_casts=self.smart_casts)
                    expr_type = tp.get_type_hint(
                        self._assign.expr, self.program.context,
                        self._namespace, self.program.bt_factory,
                        self.types, smart_casts=self.smart_casts)
                    if not expr_type == arg_type:
                        return node
                self.is_transformed = True
                node.class_type.can_infer_type_args = True
        return node

    @deepcopynode
    def _check_var_decl_infer(self, node: ast.VariableDeclaration):
        """If the expr is a New ParameterizedType check if type arguments
        can be inferred.
        """
        # Check if var_type is set and not a super--sub class.
        # For instance, in the following example we can remove the type arg.
        #   class A<T>
        #   val a: A<String> = A<String>()
        # But in the next one we can't.
        #   open class A
        #   class B<T>: A()
        #   val a: A = B<Int>()
        # TODO Add randomness
        if (node.var_type and
                isinstance(node.expr, ast.New) and
                isinstance(node.expr.class_type, types.ParameterizedType) and
                node.var_type.name == node.expr.class_type.name and
                not node.expr.class_type.can_infer_type_args):
            self.is_transformed = True
            node.expr.class_type.can_infer_type_args = True
        return node

    @deepcopynode
    def _check_func_call_infer(self, node: ast.FunctionCall):
        """We can remove type arguments from function's arguments that are
        ParameterizedTypes.
        """
        # Check if argument is New and class_type is ParameterizedType.
        # Example:
        #   class B<T, K>
        #   fun foo(x: B<Int, Char>) {}
        #   foo(B<Int, Char>()) // can be foo(B())
        # We can't remove type arguments when a ParameterDeclaration's
        # param_type is a super class of the argument.
        # Example:
        #   class B
        #   class C<T>
        #   fun foo(x: B)
        #   foo(C<Int>())  // cannot change
        # TODO Add randomness
        try:
            fdecl = self.program.context.get_funcs(
                self._namespace, glob=True)[node.func]
        except KeyError:
            # FIXME I don't know why this works.
            # The function can be declared in a different namespace than
            # the one we are currently on. For example, consider the following
            # fun foo(x: int)
            # ...
            # class A {
            #   fun bar() {
            #     foo(4)
            #   }
            # }
            #
            # If we add overloading, then this might stop working.

            fdecl = self.program.context.get_funcs(
                self._namespace, only_current=True)[node.func]
        len_p = len(fdecl.params)
        for pos, arg in enumerate(node.args):
            # Correctly define position of parameter in case of varargs.
            param_index = pos if pos < len_p else len_p - 1
            if (isinstance(arg, ast.New) and
                    isinstance(arg.class_type, types.ParameterizedType) and
                    fdecl.params[param_index].param_type.name ==
                    arg.class_type.name and
                    not arg.class_type.can_infer_type_args):
                self.is_transformed = True
                arg.class_type.can_infer_type_args = True
        return node

    @deepcopynode
    def _check_func_decl_infer(self, node: ast.FunctionDeclaration):
        """If there is a New expression in the return statement then
        we can infer its type arguments
        """
        # Check if ret_type is set and return statement is a ParameterizedType
        # Example:
        #   class A<T>
        #   fun buz(): A<Number> = A<Number>() // can be A()
        # If return statement is a subtyppe of ret_type, then we cannot change
        # it. Consider the following example.
        #   class A
        #   class B<T>: A()
        #   fun buz(): A = B<Int>() // cannot change to B()
        # TODO Add randomness
        if node.ret_type is None:
            return node
        if isinstance(node.body, ast.New):
            new = node.body
        elif (isinstance(node.body, ast.Block) and
                len(node.body.body) > 0 and
                isinstance(node.body.body[-1], ast.New)):
            new = node.body.body[-1]
        else:
            return node
        if (isinstance(new.class_type, types.ParameterizedType) and
                new.class_type.name == node.ret_type.name and
                not new.class_type.can_infer_type_args):
            self.is_transformed = True
            new.class_type.can_infer_type_args = True
        return node

    @change_namespace
    def visit_class_decl(self, node):
        return super().visit_class_decl(node)

    def visit_var_decl(self, node):
        self._var_decl = (self._namespace, node)
        new_node = super().visit_var_decl(node)
        new_node = self._check_var_decl_infer(new_node)
        self._var_decl = None
        return new_node

    def visit_assign(self, node):
        self._assign = node
        new_node = super().visit_assign(node)
        self._assign = None
        return new_node

    @change_namespace
    def visit_func_decl(self, node):
        old_ret_stmt = self._ret_stmt
        if (not node.ret_type and
                node.inferred_type != self.program.bt_factory.get_void_type()):
            self._ret_stmt = node.body.body[-1] \
                if isinstance(node.body, ast.Block) else node.body

        new_node = super().visit_func_decl(node)
        new_node = self._check_func_decl_infer(new_node)

        self._ret_stmt = old_ret_stmt
        return new_node

    def visit_new(self, node):
        new_node = super().visit_new(node)
        new_node = self._check_new_infer(new_node)
        return new_node

    def visit_func_call(self, node):
        new_node = super().visit_func_call(node)
        new_node = self._check_func_call_infer(new_node)
        return new_node

    def visit_conditional(self, node):
        children = node.children()
        new_children = []

        # Visit children
        cond = children[0]
        new_children.append(cond.accept(self))
        true_branch = children[1]
        false_branch = children[2]
        # Handle Smart Cast and is suffix
        prev_namespace = self._namespace
        if isinstance(cond, ast.Is):
            # true branch smart cast
            if not cond.operator.is_not:
                self.smart_casts.append((cond.lexpr, cond.rexpr))
                self._namespace = prev_namespace + ('true_block',)
                new_children.append(true_branch.accept(self))
                self.smart_casts.pop()
                self._namespace = prev_namespace + ('false_block',)
                new_children.append(false_branch.accept(self))
            # false branch smart cast
            else:
                self._namespace = prev_namespace + ('true_block',)
                new_children.append(true_branch.accept(self))
                self.smart_casts.append((cond.lexpr, cond.rexpr))
                self._namespace = prev_namespace + ('false_block',)
                new_children.append(false_branch.accept(self))
                self.smart_casts.pop()
        else:
            new_children.append(true_branch.accept(self))
            new_children.append(false_branch.accept(self))

        self._namespace = prev_namespace
        node.update_children(new_children)
        return node
