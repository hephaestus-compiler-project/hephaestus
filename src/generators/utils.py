"""
This file includes utility functions for the generator module.
"""
from dataclasses import dataclass

from src import utils as ut
from src.ir import ast
from src.ir import types as tp
from src.ir import type_utils as tu


### Data Classes ###

@dataclass
class SuperClassInfo:
    """
    A data class for storing information regarding a super class.
    """
    super_cls: ast.ClassDeclaration
    type_var_map: tu.TypeVarMap
    super_inst: ast.SuperClassInstantiation


@dataclass
class AttrAccessInfo:
    """
    A data class for storing information regarding a specific attribute
    access (either function or field).

    Attributes:
        receiver_t: The type of the receiver.
        receiver_inst: TypeVarMap for receiver_t in case receiver_t is a
            parameterized type.
        attr_decl: The declaration corresponding to the attribute (either field
            declaration or a function declaration).
        attr_inst: TypeVarMap for attr_decl if attr_decl is a parameterized
            function
    """
    receiver_t: tp.Type
    receiver_inst: tu.TypeVarMap
    attr_decl: ast.Declaration
    attr_inst: tu.TypeVarMap


@dataclass
class AttrReceiverInfo:
    """
    A data class for storing information regarding a receiver object and one
    of its attributes.

    Attributes:
        receiver_expr: The receiver expression (usually a Variable).
        receiver_inst: TypeVarMap for receiver in case receiver is a
            parameterized type.
        attr_decl: The declaration corresponding to the attribute (either a field
            declaration or a function declaration).
        attr_inst: TypeVarMap for attr_decl if attr_decl is a parameterized
            function.
    """
    receiver_expr: ast.Expr
    receiver_inst: tu.TypeVarMap
    attr_decl: ast.Declaration
    attr_inst: tu.TypeVarMap


### Utility functions ###

# NOTE maybe me can create an enum for class types
def select_class_type(contain_fields: bool):
    """Select class type for a class declaration.

    Args:
        contain_fields: set to True if the class contains a field.

    Returns:
        ast.ClassDeclaration.{REGULAR, ABSTRACT, INTERFACE}
    """
    # TODO probabilities table
    # there's higher probability to generate a regular class.
    if ut.random.bool():
        return ast.ClassDeclaration.REGULAR

    candidates = [ast.ClassDeclaration.ABSTRACT]
    if not contain_fields:
        candidates.append(ast.ClassDeclaration.INTERFACE)
    return ut.random.choice(candidates)


def init_variance_choices(type_var_map: tu.TypeVarMap) -> tu.VarianceChoices:
    """Generate variance_choices for the type variables of type_var_map
    """
    variance_choices = {}
    for type_var in type_var_map.keys():
        variance_choices[type_var] = (False, False)
        # If disable variance on specific type parameters, then we have to
        # do the same on its bound (assuming it is another type variable).
        while type_var.bound and type_var.bound.is_type_var():
            type_var = type_var.bound
            variance_choices[type_var] = (False, False)
    return variance_choices


def gen_identifier(ident_type:str=None) -> str:
    """Generate an identifier name.

    Args:
        ident_type: None or 'capitalize' or 'lower'

    Raises:
        AssertionError: Raises an AssertionError if the ident_type is neither
            'capitalize' nor 'lower'.
    """
    word = ut.random.word()
    if ident_type is None:
        return word
    if ident_type == 'lower':
        return word.lower()
    if ident_type == 'capitalize':
        return word.capitalize()
    raise AssertionError("ident_type should be 'capitalize' or 'lower'")
