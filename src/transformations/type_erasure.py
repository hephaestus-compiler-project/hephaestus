# pylint: disable=too-many-instance-attributes
from copy import deepcopy

from src.ir import ast
from src.ir import types
from src.transformations.base import Transformation, change_namespace


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


class TypeArgumentErasureSubstitution(Transformation):
    """Remove type information when possible:

       Remove type arguments from ParameterizedTypes instantiations
    """
    CORRECTNESS_PRESERVING = True
    NAME = 'Type Erasure Substitution'

    def __init__(self, program, logger=None):
        super().__init__(program, logger)
        self._namespace: tuple = ast.GLOBAL_NAMESPACE

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
        fdecl = self.program.context.get_funcs(
            self._namespace, glob=True)[node.func]
        for pos, arg in enumerate(node.args):
            if (isinstance(arg, ast.New) and
                    isinstance(arg.class_type, types.ParameterizedType) and
                    fdecl.params[pos].param_type.name ==
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
        new_node = super().visit_var_decl(node)
        new_node = self._check_var_decl_infer(new_node)
        return new_node

    @change_namespace
    def visit_func_decl(self, node):
        new_node = super().visit_func_decl(node)
        new_node = self._check_func_decl_infer(new_node)
        return new_node

    def visit_new(self, node):
        new_node = super().visit_new(node)
        new_node = self._check_new_infer(new_node)
        return new_node

    def visit_func_call(self, node):
        new_node = super().visit_func_call(node)
        new_node = self._check_func_call_infer(new_node)
        return new_node
