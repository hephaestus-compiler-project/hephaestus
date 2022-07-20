# pylint: disable=dangerous-default-value
from typing import List, Set, Union
from copy import deepcopy

import src.ir.type_utils as tu
import src.ir.types as types
from src import utils
from src.ir import BUILTIN_FACTORIES
from src.ir.builtins import BuiltinFactory, FunctionType
from src.ir.node import Node


GLOBAL_NAMESPACE = ('global',)


def check_list_eq(first, second):
    if len(first) != len(second):
        return False
    return all(s.is_equal(o) for o, s in zip(first, second))


def check_default_eq(first, second):
    if first is not None:
        return first.is_equal(second)
    else:
        return second is None


class Expr(Node):
    pass


class Program(Node):
    # Set default value to kotlin for backward compatibility
    def __init__(self, context, language):
        self.context = context
        self.language = language
        self.bt_factory: BuiltinFactory = BUILTIN_FACTORIES[language]

    def children(self):
        return self.context.get_declarations(GLOBAL_NAMESPACE,
                                             only_current=True).values()

    def update_children(self, children):
        super().update_children(children)
        for c in children:
            self.add_declaration(c)

    @property
    def declarations(self):
        # Get declarations as list
        return self.get_declarations().values()

    def get_declarations(self):
        return self.context.get_declarations(GLOBAL_NAMESPACE,
                                             only_current=True)

    def get_types(self):
        usr_types = [d for d in self.declarations
                     if isinstance(d, ClassDeclaration)]
        ttypes = usr_types + self.bt_factory.get_non_nothing_types()
        new_types = []
        for t in ttypes:
            if isinstance(t, types.TypeConstructor):
                t, _ = tu.instantiate_type_constructor(t, ttypes)
            new_types.append(t)
        return new_types

    def update_declarations(self, decls):
        self.context._context[GLOBAL_NAMESPACE]['decls'] = decls

    def _add_function(self, namespace, func):
        self.context.add_func(namespace, func.name, func)
        namespace = namespace + (func.name,)
        for p in func.params:
            self.context.add_var(namespace, p.name, p)
        if not func.body or not isinstance(func.body, Block):
            return
        stack = list(func.body.body)
        while stack:
            s = stack.pop()
            if isinstance(s, VariableDeclaration):
                self.context.add_var(namespace, s.name, s)

            if isinstance(s, FunctionDeclaration):
                self._add_function(namespace, s)

            if isinstance(s, Conditional):
                stack.append(s.true_branch)
                stack.append(s.false_branch)

            if isinstance(s, Block):
                stack.extend(s.body)

    def _add_class(self, namespace, class_decl):
        namespace = namespace + (class_decl.name,)
        for f in class_decl.fields:
            self.context.add_var(namespace, f.name, f)
        for f in class_decl.functions:
            self._add_function(namespace, f)

    def add_declaration(self, decl):
        decl_types = {
            FunctionDeclaration: self.context.add_func,
            ClassDeclaration: self.context.add_class,
            VariableDeclaration: self.context.add_var,
        }
        decl_types[decl.__class__](GLOBAL_NAMESPACE, decl.name, decl)
        if isinstance(decl, ClassDeclaration):
            self._add_class(GLOBAL_NAMESPACE, decl)

        if isinstance(decl, FunctionDeclaration):
            self._add_function(GLOBAL_NAMESPACE, decl)

    def remove_declaration(self, decl):
        decl_types = {
            FunctionDeclaration: self.context.remove_func,
            ClassDeclaration: self.context.remove_class,
            VariableDeclaration: self.context.remove_var,
        }
        decl_types[decl.__class__](GLOBAL_NAMESPACE, decl.name)

    def __str__(self):
        return "\n\n".join(map(str, self.children()))


class Block(Node):
    def __init__(self, body: List[Node], is_func_block=True):
        self.body = body
        self.is_func_block = is_func_block

    def children(self):
        return self.body

    def update_children(self, children):
        super().update_children(children)
        self.body = children

    def is_bottom(self):
        if self.body:
            return self.body[-1].is_bottom()
        return True

    def __str__(self):
        return "{{\n  {}\n}}".format("\n  ".join(map(str, self.body)))

    def is_equal(self, other):
        if isinstance(other, Block):
            return check_list_eq(self.body, other.body)
        return False


class Declaration(Node):
    def get_type(self):
        raise NotImplementedError('get_type() must be implemented')

    def __repr__(self):
        if hasattr(self, 'name'):
            # pylint: disable=no-member
            return self.name
        return super().__repr__()


class VariableDeclaration(Declaration):
    def __init__(self, name: str,
                 expr: Expr,
                 is_final: bool = True,
                 var_type: types.Type = None,
                 inferred_type: types.Type = None):
        self.name = name
        self.expr = expr
        self.is_final = is_final
        self.var_type = var_type
        self.inferred_type = var_type if var_type else inferred_type
        assert self.inferred_type, ("The inferred_type of a variable must"
                                    " not be None")

    def children(self):
        return [self.expr]

    def omit_type(self):
        self.var_type = None

    def get_type(self):
        return self.inferred_type

    def update_children(self, children):
        super().update_children(children)
        self.expr = children[0]

    @property
    def is_type_inferred(self):
        return not bool(self.var_type)

    def __str__(self):
        prefix = "val " if self.is_final else "var "
        if self.var_type is None:
            return prefix + self.name + " = " + str(self.expr)
        return "{}{}: {} = {}".format(
            prefix, self.name, str(self.var_type), str(self.expr))

    def is_equal(self, other):
        if isinstance(other, VariableDeclaration):
            return (self.name == other.name and
                    self.expr.is_equal(other.expr) and
                    self.is_final == other.is_final and
                    self.var_type == other.var_type and
                    self.inferred_type == other.inferred_type)
        return False


class FieldDeclaration(Declaration):
    def __init__(self, name: str, field_type: types.Type, is_final=True,
                 can_override=False, override=False):
        self.name = name
        self.field_type = field_type
        self.is_final = is_final
        self.can_override = can_override
        self.override = override

    def children(self):
        return []

    def get_type(self):
        return self.field_type

    def update_children(self, children):
        pass

    @property
    def is_type_inferred(self):
        return False

    def __str__(self):
        return str(self.name) + ": " + str(self.field_type)

    def is_equal(self, other):
        if isinstance(other, FieldDeclaration):
            return (self.name == other.name and
                    self.field_type == other.field_type and
                    self.is_final == other.is_final and
                    self.can_override == other.can_override and
                    self.override == other.override)
        return False


class ObjectDecleration(Declaration):
    def __init__(self, name: str):
        self.name = name

    def get_type(self):
        return types.Object(self.name)

    def update_children(self, children):
        pass

    def __str__(self):
        return "object " + self.name

    def is_equal(self, other):
        if isinstance(other, ObjectDecleration):
            return self.name == other.name
        return False


class SuperClassInstantiation(Node):
    def __init__(self, class_type: types.Type, args: List[Expr] = []):
        assert not isinstance(class_type, types.AbstractType)
        self.class_type = class_type
        self.args = args

    def children(self):
        return self.args or []

    def update_children(self, children):
        super().update_children(children)
        if self.args is not None:
            self.args = children

    def __str__(self):
        if self.args is None:
            return self.class_type.name
        return "{}({})".format(
            self.class_type.name, ", ".join(map(str, self.args)))

    def is_equal(self, other):
        if isinstance(other, SuperClassInstantiation):
            return (self.class_type == other.class_type and
                    check_list_eq(self.args, other.args))
        return False


class CallArgument(Node):
    """
    This represents an argument of function / constructor call.

    A call argument can also be named (i.e., param_name = expr).
    In this case the field 'name' is not None.
    """

    def __init__(self, expr: Expr, name: str = None):
        self.expr = expr
        self.name = name

    def children(self):
        return [self.expr]

    def update_children(self, children):
        super().update_children(children)
        self.expr = children[0]

    def __str__(self):
        if self.name:
            return "{} = {}".format(self.name, str(self.expr))
        return str(self.expr)

    def is_equal(self, other):
        if isinstance(other, CallArgument):
            return (self.name == other.name and
                    self.expr.is_equal(other.is_equal))
        return False


class ParameterDeclaration(Declaration):
    def __init__(self, name: str,
                 param_type: types.Type,
                 vararg: bool = False,
                 default: Expr = None):
        self.name = name
        self.param_type = param_type
        self.vararg = vararg
        self.default = default

    def children(self):
        if self.default:
            return [self.default]
        return []

    def update_children(self, children):
        super().update_children(children)
        if self.default:
            self.default = children[0]

    def get_type(self):
        return self.param_type

    @property
    def is_type_inferred(self):
        return False

    def __str__(self):
        prefix = 'vararg ' if self.vararg else ''
        if self.default is None:
            return prefix + self.name + ": " + str(self.param_type)
        return "{}{}: {} = {}".format(
            prefix, self.name, str(self.param_type), str(self.default))

    def is_equal(self, other):
        if isinstance(other, ParameterDeclaration):
            return (self.name == other.name and
                    self.param_type == other.param_type and
                    self.vararg == other.vararg and
                    check_default_eq(self.default, other.default))
        return False


class FunctionDeclaration(Declaration):
    CLASS_METHOD = 0
    FUNCTION = 1

    # body can be Block or Expr
    def __init__(self,
                 name: str,
                 params: List[ParameterDeclaration],
                 ret_type: types.Type,
                 body: Node,
                 func_type: int,
                 inferred_type: types.Type = None,
                 is_final=True,
                 override=False,
                 type_parameters=[]):
        self.name = name
        self.params = params
        self.ret_type = ret_type
        self.body = body
        self.func_type = func_type
        self.is_final = is_final
        self.override = override
        self.type_parameters = type_parameters
        self.inferred_type = (
            self.ret_type if inferred_type is None else inferred_type)
        assert self.inferred_type, ("The inferred_type of a function must"
                                    " not be None")

    def children(self):
        children = self.params + self.type_parameters
        if self.body is None:
            return children
        return children + [self.body]

    def update_children(self, children):
        def get_lst(start, end):
            return children[start:end]

        super().update_children(children)
        len_params = len(self.params)
        len_type_params = len(self.type_parameters)
        for i, c in enumerate(children[:len_params]):
            self.params[i] = c
        type_params = get_lst(len_params, len_params + len_type_params)
        for i, t_param in enumerate(type_params):
            self.type_parameters[i] = t_param
        if self.body is None:
            return
        self.body = children[-1]

    def omit_type(self):
        self.ret_type = None

    def get_type(self):
        return self.inferred_type

    def is_class_method(self):
        return self.func_type == self.CLASS_METHOD

    def is_parameterized(self):
        return bool(self.type_parameters)

    def get_signature(self, function_type: FunctionType):
        type_args = [p.param_type for p in self.params] + [self.ret_type]
        return types.ParameterizedType(function_type, type_args)

    def __str__(self):
        type_params_str = (
            "<" + ", ".join(map(str, self.type_parameters)) + "> "
            if self.type_parameters
            else ""
        )
        if self.ret_type is None:
            return "{}fun {}({}) =\n  {}".format(
                type_params_str, self.name, ",".join(map(str, self.params)),
                str(self.body))
        return "{}fun {}({}): {} =\n  {}".format(
            type_params_str, self.name, ",".join(map(str, self.params)),
            str(self.ret_type), str(self.body))

    def is_equal(self, other):
        if isinstance(other,  FunctionDeclaration):
            return (self.name == other.name and
                    self.ret_type == other.ret_type and
                    (
                        self.body == other.body
                        if self.body is None
                        else self.body.is_equal(other.body)
                    ) and
                    self.func_type == other.func_type and
                    self.is_final == other.is_final and
                    check_list_eq(self.params, other.params) and
                    check_list_eq(self.type_parameters,
                                  other.type_parameters) and
                    self.inferred_type == other.inferred_type)
        return False


def _instantiate_type_param_rec(t_param: types.TypeParameter,
                                type_var_map: dict):
    new_t_param = deepcopy(t_param)
    if not new_t_param.is_type_var():
        return new_t_param
    if new_t_param.bound is not None:
        new_bound = types.substitute_type(new_t_param.bound, type_var_map)
        new_t_param.bound = _instantiate_type_param_rec(new_bound,
                                                        type_var_map)
    return new_t_param

class Lambda(Expr):
    # body can be Block or Expr
    def __init__(self,
                 shadow_name: str,  # we use it in namespace
                 params: List[ParameterDeclaration],
                 ret_type: types.Type,
                 body: Node,
                 signature: types.ParameterizedType):
        self.name = shadow_name
        self.params = params
        self.ret_type = ret_type
        self.body = body
        self.signature = signature

    def children(self):
        if self.body is None:
            return self.params
        return self.params + [self.body]

    def update_children(self, children):
        super().update_children(children)
        len_params = len(self.params)
        for i, c in enumerate(children[:len_params]):
            self.params[i] = c
        if self.body is None:
            return
        self.body = children[-1]

    def get_type(self):
        return self.ret_type

    def get_signature(self, function_type: FunctionType):
        type_args = [p.param_type for p in self.params] + [self.ret_type]
        return types.ParameterizedType(function_type, type_args)

    def __str__(self):
        if self.ret_type is None:
            return "lambda ({}) =\n  {}".format(
                ",".join(map(str, self.params)), str(self.body))
        return "lambda ({}): {} =\n  {}".format(
            ",".join(map(str, self.params)), str(self.ret_type),
            str(self.body))

    def is_equal(self, other):
        if isinstance(other,  Lambda):
            return (self.ret_type == other.ret_type and
                    (
                        self.body == other.body
                        if self.body is None
                        else self.body.is_equal(other.body)
                    ) and
                    check_list_eq(self.params, other.params))
        return False


class ClassDeclaration(Declaration):
    REGULAR = 0
    INTERFACE = 1
    ABSTRACT = 2

    def __init__(self, name: str,
                 superclasses: List[SuperClassInstantiation],
                 class_type: int = None,
                 fields: List[FieldDeclaration] = [],
                 functions: List[FunctionDeclaration] = [],
                 is_final=True,
                 type_parameters: List[types.TypeParameter] = []):
        self.name = name
        self.superclasses = superclasses
        self.class_type = class_type or self.REGULAR
        self.fields = fields
        self.functions = functions
        self.is_final = is_final
        self.type_parameters = type_parameters
        self.supertypes = [s.class_type for s in self.superclasses]

    @property
    def attributes(self):
        return self.fields + self.functions

    def children(self):
        return self.fields + self.superclasses + self.functions + \
            self.type_parameters

    def update_children(self, children):
        def get_lst(start, end):
            return children[start:end]

        super().update_children(children)
        len_fields = len(self.fields)
        len_supercls = len(self.superclasses)
        len_functions = len(self.functions)
        len_tp = len(self.type_parameters)
        fields = get_lst(0, len_fields)
        for i, c in enumerate(fields):
            self.fields[i] = c
        supercls = get_lst(len_fields, len_fields + len_supercls)
        for i, c in enumerate(supercls):
            self.superclasses[i] = c
            self.supertypes[i] = c.class_type
        functions = get_lst(len_fields + len_supercls,
                            len_fields + len_supercls + len_functions)
        for i, c in enumerate(functions):
            self.functions[i] = c
        type_params = get_lst(
            len_fields + len_supercls + len_functions,
            len_fields + len_supercls + len_functions + len_tp)
        for i, c in enumerate(type_params):
            self.type_parameters[i] = c

    def get_type(self):
        if self.type_parameters:
            return types.TypeConstructor(
                self.name, self.type_parameters,
                self.supertypes)
        return types.SimpleClassifier(
            self.name, self.supertypes)

    def get_class_prefix(self):
        if self.class_type == self.REGULAR:
            return "class"
        if self.class_type == self.INTERFACE:
            return "interface"
        return "abstract class"

    def is_parameterized(self):
        return bool(self.type_parameters)

    def is_interface(self):
        return self.class_type == self.INTERFACE

    def is_abstract(self):
        return self.class_type == self.ABSTRACT

    def is_regular(self):
        return self.class_type == self.REGULAR

    def get_field(self, field_name):
        for f in self.fields:
            if f.name == field_name:
                return f
        return None

    def get_overridable_functions(self):
        return [
            f
            for f in self.functions
            if not f.is_final
        ]

    def get_overridable_fields(self):
        return [
            f
            for f in self.fields
            if f.can_override
        ]

    def get_callable_functions(self, class_decls) -> Set[FunctionDeclaration]:
        """All functions that can be called in instantiations of this class
        """
        # Get functions that are implemented in the current class
        functions = set(self.functions)

        if not self.superclasses:
            return functions

        # Retrieve functions from the inheritance chain.
        super_cls = self.superclasses[0]
        class_decl = tu.get_superclass_decl(super_cls, class_decls)

        if not class_decl:
            return functions

        type_var_map = tu.get_superclass_type_var_map(super_cls, class_decl)

        parent_funcs = class_decl.get_callable_functions(class_decls)

        # substitute type variables in parent's functions
        for f in parent_funcs:
            new_f = deepcopy(f)
            params = []
            for p in f.params:
                new_p = deepcopy(p)
                new_p.param_type = types.substitute_type(p.get_type(),
                                                         type_var_map)
                params.append(new_p)
            type_params = []
            for t_param in f.type_parameters:
                new_tparam = deepcopy(t_param)
                if new_tparam.bound:
                    new_tparam.bound = types.substitute_type(t_param.bound,
                                                             type_var_map)
                type_params.append(new_tparam)
            ret_type = types.substitute_type(f.get_type(),
                                             type_var_map)
            new_f.type_parameters = type_params
            new_f.params = params
            new_f.inferred_type = ret_type
            new_f.ret_type = ret_type
            functions.add(new_f)

        return functions

    def get_all_fields(self, class_decls) -> Set[FieldDeclaration]:
        """
        All fields (including the inheritted ones) that can be accessed by
        instantiations of this class.
        """
        fields = set(self.fields)
        field_names = {f.name for f in fields}

        if not self.superclasses:
            return fields

        # Retrieve fields from the inheritance chain.
        super_cls = self.superclasses[0]
        class_decl = tu.get_superclass_decl(super_cls, class_decls)

        if not class_decl:
            return fields

        type_var_map = tu.get_superclass_type_var_map(super_cls, class_decl)

        parent_fields = class_decl.get_all_fields(class_decls)

        # substitute type variables in parent's functions
        for f in parent_fields:
            if f.name in field_names:
                # We override this field in the current class
                continue
            new_f = deepcopy(f)
            new_f.field_type = types.substitute_type(f.get_type(),
                                                     type_var_map)
            fields.add(new_f)

        return fields

    def get_all_attributes(self, class_decls) -> Set[Union[FunctionDeclaration, FieldDeclaration]]:
        """
        Get all attributes (fields + functions) from the inheritance chain
        """
        attributes = self.get_callable_functions(class_decls)
        attributes.update(self.get_all_fields(class_decls))
        return attributes

    def get_abstract_functions(self, class_decls) -> List[FunctionDeclaration]:
        # Get the abstract functions that are declared in the current class.
        functions = {
            f
            for f in self.functions
            if f.body is None
        }
        if not self.superclasses:
            return functions

        # Retrieve any abstract function from the inheritance chain.
        super_cls = self.superclasses[0]
        class_decl = tu.get_superclass_decl(super_cls, class_decls)

        if not class_decl:
            return functions

        type_var_map = tu.get_superclass_type_var_map(super_cls, class_decl)

        funcs = class_decl.get_abstract_functions(class_decls)
        implemented_funcs = {f.name for f in self.functions
                             if f.body is not None}
        for f in funcs:
            if f.name in implemented_funcs:
                continue
            new_f = deepcopy(f)
            params = []
            for p in f.params:
                new_p = deepcopy(p)
                new_p.param_type = types.substitute_type(new_p.get_type(),
                                                         type_var_map)
                if new_p.param_type.is_type_var() and (
                        new_p.param_type.bound is not None):
                    new_p.param_type.bound = _instantiate_type_param_rec(
                        new_p.param_type.bound, type_var_map
                    )
                params.append(new_p)
            type_params = [
                _instantiate_type_param_rec(t, type_var_map)
                for t in f.type_parameters
            ]
            ret_type = types.substitute_type(deepcopy(f.get_type()),
                                             type_var_map)
            if ret_type.is_type_var() and ret_type.bound is not None:
                ret_type.bound = _instantiate_type_param_rec(ret_type.bound,
                                                             type_var_map)
            new_f.params = params
            new_f.inferred_type = ret_type
            new_f.ret_type = ret_type
            new_f.type_parameters = type_params
            functions.add(new_f)
        return functions

    def inherits_from(self, cls):
        """
        Check if the current class directly inherits from the given class.
        """
        other_t = cls.get_type()
        supertypes = self.get_type().supertypes
        if not cls.is_parameterized():
            return other_t in supertypes
        return any(getattr(st, 't_constructor', None) == other_t
                   for st in supertypes)

    def all_type_params_in_fields(self):
        """Check if all type parameters are used in fields
        """
        if not self.is_parameterized:
            return False
        for tparam in self.type_parameters:
            used = False
            for fdecl in self.fields:
                used = True if fdecl.field_type == tparam else used
            if not used:
                return False
        return True

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

    def is_equal(self, other):
        if isinstance(other, ClassDeclaration):
            return (self.name == other.name and
                    check_list_eq(self.superclasses, other.superclasses) and
                    self.class_type == other.class_type and
                    check_list_eq(self.functions, other.functions) and
                    self.is_final == other.is_final and
                    check_list_eq(self.type_parameters, other.type_parameters)
                    and self.supertypes == other.supertypes)
        return False


class Constant(Expr):
    def __init__(self, literal: str):
        self.literal = literal

    def children(self):
        return []

    def update_children(self, children):
        pass

    def __str__(self):
        return str(self.literal)

    def is_equal(self, other):
        if isinstance(other, Constant):
            return self.literal == other.literal
        return False


# This is a constant representing a value whose type is the Bottom type,
# meaning that it's subtype of any other type.
class BottomConstant(Constant):
    def __init__(self, t: types.Type):
        super().__init__("_B_")
        self.t = t

    def is_equal(self, other):
        if isinstance(other, BottomConstant):
            return self.t == other.t
        return False

    def is_bottom(self):
        return True


class IntegerConstant(Constant):
    # TODO: Support Hex Integer literals, binary integer literals?
    def __init__(self, literal: int, integer_type):
        assert isinstance(literal, int), 'Integer literal must be int'
        super().__init__(literal)
        self.integer_type = integer_type

    def is_equal(self, other):
        if isinstance(other, IntegerConstant):
            return (self.literal == other.literal and
                    self.integer_type == other.integer_type)
        return False


class RealConstant(Constant):

    def __init__(self, literal: str, real_type):
        assert '.' in literal and utils.is_number(literal), (
            'Real literal is not valid')
        super().__init__(literal)
        self.real_type = real_type

    def is_equal(self, other):
        if isinstance(other, RealConstant):
            return (self.literal == other.literal and
                    self.real_type == other.real_type)
        return False


class BooleanConstant(Constant):
    def __init__(self, literal: str):
        assert literal in ('true', 'false'), (
            'Boolean literal is not "true" or "false"')
        super().__init__(literal)


class CharConstant(Constant):
    def __init__(self, literal: str):
        assert len(literal) == 1, (
            'Character literal must be a single character')
        super().__init__(literal)

    def __str__(self):
        return "'{}'".format(self.literal)


class StringConstant(Constant):

    def __str__(self):
        return '"{}"'.format(self.literal)


class ArrayExpr(Expr):
    def __init__(self, array_type: types.Type, length: int, exprs: List[Expr]):
        self.length = length
        self.array_type = array_type
        self.exprs = exprs

    def children(self):
        return self.exprs

    def update_children(self, children):
        super().update_children(children)
        self.exprs = children

    def __str__(self):
        return "{}[]".format(str(self.array_type))

    def is_equal(self, other):
        if isinstance(other, ArrayExpr):
            return (self.array_type == other.array_type and
                    self.length == other.length and
                    self.exprs == other.exprs)
        return False


class Variable(Expr):
    def __init__(self, name: str):
        self.name = name

    def children(self):
        return []

    def update_children(self, children):
        pass

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return str(self.name)

    def is_equal(self, other):
        if isinstance(other, Variable):
            return self.name == other.name
        return False


class Conditional(Expr):
    def __init__(self, cond: Expr, true_branch: Block, false_branch: Block,
                 inferred_type: types.Type):
        self.cond = cond
        self.true_branch = true_branch
        self.false_branch = false_branch
        self.inferred_type = inferred_type

    def children(self):
        return [self.cond, self.true_branch, self.false_branch]

    def update_children(self, children):
        super().update_children(children)
        self.cond = children[0]
        self.true_branch = children[1]
        self.false_branch = children[2]

    def is_bottom(self):
        return self.true_branch.is_bottom() and self.false_branch.is_bottom()

    def get_type(self):
        return self.inferred_type

    def __str__(self):
        return "if ({})\n  {}\nelse\n  {}".format(
            str(self.cond), str(self.true_branch), str(self.false_branch))

    def is_equal(self, other):
        if isinstance(other, Conditional):
            return (self.cond.is_equal(other.cond) and
                    self.true_branch.is_equal(other.true_branch) and
                    self.false_branch.is_equal(other.false_branch) and
                    self.inferred_type == other.inferred_type)
        return False


class Operator(Node):
    def __init__(self, name: str, is_not=False):
        self.name = name
        self.is_not = is_not

    def children(self):
        return []

    def update_children(self, children):
        pass

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.name == other.name and
                self.is_not == other.is_not)

    def __hash__(self):
        hash(str(self.__class__) + str(self.name) + str(self.is_not))

    def __str__(self):
        if self.is_not:
            return "!" + self.name
        return self.name

    def is_equal(self, other):
        return (self.__class__ == other.__class__ and
                self.name == other.name and
                self.is_not == other.is_not)


class BinaryOp(Expr):
    ALL_OPERATORS = None
    VALID_OPERATORS = None

    def __init__(self, lexpr: Expr, rexpr: Expr, operator: Operator):
        if self.VALID_OPERATORS is not None:
            # pylint: disable=unsupported-membership-test
            # @theosotr should we keep this check? If we ant to keep it we may
            # want to check if the operator is valid for a given language
            assert operator in self.ALL_OPERATORS, (
                'Binary operator ' + operator + ' is not valid')
        self.lexpr = lexpr
        self.rexpr = rexpr
        self.operator = operator

    def children(self):
        return [self.lexpr, self.rexpr]

    def update_children(self, children):
        super().update_children(children)
        self.lexpr = children[0]
        self.rexpr = children[1]

    def __str__(self):
        return "{} {} {}".format(
            str(self.lexpr), str(self.operator), str(self.rexpr))

    def is_equal(self, other):
        if isinstance(other, BinaryOp):
            return (self.lexpr.is_equal(other.lexpr) and
                    self.rexpr.is_equal(other.rexpr) and
                    self.operator == other.operator)
        return False


class LogicalExpr(BinaryOp):
    ALL_OPERATORS = [
        Operator('&&'),
        Operator('||')
    ]
    VALID_OPERATORS = {
        "kotlin": [
            Operator('&&'),
            Operator('||')
        ],
        "groovy": [
            Operator('&&'),
            Operator('||')
        ],
        "java": [
            Operator('&&'),
            Operator('||')
        ],
        "typescript": [
            Operator('&&'),
            Operator('||')
        ]
    }


class EqualityExpr(BinaryOp):
    ALL_OPERATORS = [
        Operator('=='),
        Operator('==='),
        Operator('=', is_not=True),
        Operator('==', is_not=True)
    ]
    VALID_OPERATORS = {
        "kotlin": [
            Operator('=='),
            Operator('==='),
            Operator('=', is_not=True),
            Operator('==', is_not=True)
        ],
        "groovy": [
            Operator('=='),
            Operator('==='),
            Operator('=', is_not=True),
            Operator('==', is_not=True)
        ],
        "java": [
            Operator('=='),
            Operator('=', is_not=True)
        ],
        "typescript": [
            Operator('==='),
            Operator('==', is_not= True)
        ]
    }


class ComparisonExpr(BinaryOp):
    ALL_OPERATORS = [
        Operator('>'),
        Operator('>='),
        Operator('<'),
        Operator('<=')
    ]
    VALID_OPERATORS = {
        "kotlin": [
            Operator('>'),
            Operator('>='),
            Operator('<'),
            Operator('<=')
        ],
        "groovy": [
            Operator('>'),
            Operator('>='),
            Operator('<'),
            Operator('<=')
        ],
        "java": [
            Operator('>'),
            Operator('>='),
            Operator('<'),
            Operator('<=')
        ],
        "typescript": [
            Operator('>'),
            Operator('>='),
            Operator('<'),
            Operator('<=')
        ]
    }


class ArithExpr(BinaryOp):
    ALL_OPERATORS = [
        Operator('+'),
        Operator('-'),
        Operator('/'),
        Operator('*')
    ]
    VALID_OPERATORS = {
        "kotlin": [
            Operator('+'),
            Operator('-'),
            Operator('/'),
            Operator('*')
        ],
        "groovy": [
            Operator('+'),
            Operator('-'),
            Operator('/'),
            Operator('*')
        ],
        "java": [
            Operator('+'),
            Operator('-'),
            Operator('/'),
            Operator('*')
        ],
        "typescript": [
            Operator('+'),
            Operator('-'),
            Operator('/'),
            Operator('*')
        ]
    }


class Is(BinaryOp):
    def __init__(self, expr: Expr, etype: types.Type, is_not=False):
        operator = Operator('is', is_not=is_not)
        super().__init__(expr, etype, operator)

    def children(self):
        return [self.lexpr]

    def update_children(self, children):
        # We want to call the update_children of expr
        # pylint: disable=bad-super-call
        super(BinaryOp, self).update_children(children)
        self.lexpr = children[0]


class New(Expr):
    def __init__(self, class_type: types.Type, args: List[Expr]):
        self.class_type = class_type
        self.args = args

    def children(self):
        return self.args

    def update_children(self, children):
        super().update_children(children)
        self.args = children

    def __str__(self):
        if getattr(self.class_type, 'type_args', None) is not None:
            return " new {}<{}> ({})".format(
                str(self.class_type.name),
                ", ".join(map(str, self.class_type.type_args)) + ")",
                ", ".join(map(str, self.args)) + ")"
            )

        return "new " + self.class_type.name + "(" + \
            ", ".join(map(str, self.args)) + ")"

    def is_equal(self, other):
        if isinstance(other, New):
            return (self.class_type == other.class_type and
                    check_list_eq(self.args, other.args))
        return False


class FieldAccess(Expr):
    def __init__(self, expr: Expr, field: str):
        self.expr = expr
        self.field = field

    def children(self):
        return [self.expr]

    def update_children(self, children):
        super().update_children(children)
        self.expr = children[0]

    def __str__(self):
        return str(self.expr) + "." + self.field

    def is_equal(self, other):
        if isinstance(other, FieldAccess):
            return (self.expr.is_equal(other.expr) and
                    self.field == other.field)
        return False


class FunctionCall(Expr):
    def __init__(self, func: str, args: List[CallArgument],
                 receiver: Expr = None,
                 type_args: List[types.Type] = [],
                 is_ref_call: bool = False):
        self.func = func
        self.args = args
        self.receiver = receiver
        self.type_args = type_args
        self.is_ref_call = is_ref_call
        self._can_infer_type_args = False
        self.type_parameters = []

    def children(self):
        if self.receiver is None:
            return self.args
        return [self.receiver] + self.args

    def update_children(self, children):
        super().update_children(children)
        if self.receiver is None:
            self.args = children
        else:
            self.receiver = children[0]
            self.args = children[1:]

    def get_type_variable_assignments(self):
        return {
            t_param: self.type_args[i]
            for i, t_param in enumerate(self.type_parameters)
        }

    @property
    def can_infer_type_args(self):
        return self._can_infer_type_args

    @property
    def name(self):
        return self.func

    @can_infer_type_args.setter
    def can_infer_type_args(self, value):
        if not isinstance(value, bool):
            raise TypeError("Must be bool")
        self._can_infer_type_args = value

    def __str__(self):
        type_args_str = (
            "<" + ", ".join(map(str, self.type_args)) + ">"
            if self.type_args
            else ""
        )
        if self.receiver is None:
            return "{}{}({})".format(self.func,
                                     type_args_str,
                                     ", ".join(map(str, self.args)))
        return "{}.{}{}({})".format(
            str(self.receiver), self.func, type_args_str,
            ", ".join(map(str, self.args)))

    def is_equal(self, other):
        if isinstance(other, FunctionCall):
            return (self.func == other.func and
                    check_list_eq(self.args, other.args) and
                    check_list_eq(self.type_args, other.type_args) and
                    check_default_eq(self.receiver, other.receiver) and
                    self.is_ref_call == other.is_ref_call)
        return False


class FunctionReference(Expr):
    def __init__(self, func: str, receiver: Expr, signature: types.Type):
        self.func = func
        self.receiver = receiver
        self.signature = signature

    def children(self):
        if not self.receiver:
            return []
        return [self.receiver]

    def update_children(self, children):
        super().update_children(children)
        if self.receiver:
            self.receiver = children[0]

    def get_signature(self):
        return self.signature

    def __str__(self):
        return "{}::{}".format(str(self.receiver), self.func)

    def is_equal(self, other):
        if isinstance(other, FunctionReference):
            return (self.func == other.func and
                    check_default_eq(self.receiver, other.receiver))
        return False


class Assignment(Expr):
    def __init__(self, name: str, expr: Expr, receiver: Expr = None):
        self.name = name
        self.expr = expr
        self.receiver = receiver

    def children(self):
        if self.receiver is not None:
            return [self.receiver, self.expr]
        return [self.expr]

    def update_children(self, children):
        super().update_children(children)
        if self.receiver is not None:
            self.receiver = children[0]
            self.expr = children[1]
        else:
            self.expr = children[0]

    def __str__(self):
        if self.receiver:
            return "{}.{} = {}".format(str(self.receiver), str(self.name),
                                       str(self.expr))
        return "{} = {}".format(str(self.name), str(self.expr))

    def is_equal(self, other):
        if isinstance(other, Assignment):
            return (self.name == other.name and
                    self.expr.is_equal(other.expr) and
                    check_default_eq(self.receiver, other.receiver))
        return False
