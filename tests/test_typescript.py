from src.ir.builtins import NumberType
import src.ir.typescript_types as tst
import src.ir.typescript_ast as ts_ast
import src.ir.types as tp
import src.ir.type_utils as tu


def test_type_alias_with_literals():
    string_alias = ts_ast.TypeAliasDeclaration("Foo", tst.StringType()).get_type()
    number_alias = ts_ast.TypeAliasDeclaration("Bar", tst.NumberType()).get_type()

    string_lit = tst.StringLiteralType("foo")
    number_lit = tst.NumberLiteralType(5)

    assert string_lit.is_subtype(string_alias)
    assert not string_alias.is_subtype(string_lit)
    assert number_lit.is_subtype(number_alias)
    assert not number_alias.is_subtype(number_lit)


def test_type_alias_with_literals2():
    string_alias = ts_ast.TypeAliasDeclaration("Foo", tst.StringLiteralType("foo")).get_type()
    number_alias = ts_ast.TypeAliasDeclaration("Bar", tst.NumberLiteralType(5)).get_type()

    string_lit = tst.StringLiteralType("foo")
    number_lit = tst.NumberLiteralType(5)

    assert string_lit.is_subtype(string_alias)
    assert number_lit.is_subtype(number_alias)
    assert string_alias.is_subtype(string_lit)
    assert number_alias.is_subtype(number_lit)


def test_union_types_simple():
    union_1 = tst.UnionType([tst.NumberType(), tst.BooleanType()])

    bar_lit = tst.StringLiteralType("bar")
    union_2 = tst.UnionType([tst.BooleanType(), bar_lit])

    union_3 = tst.UnionType([tst.BooleanType(), tst.NumberType()])

    assert not union_1.is_subtype(union_2)
    assert not union_2.is_subtype(union_1)
    assert union_3.is_subtype(union_1)
    assert union_1.is_subtype(union_3)


def test_union_types_other_types():
    union = tst.UnionType([tst.NumberType(), tst.BooleanType()])
    assert tst.NumberType().is_subtype(union)


def test_union_type_assign():
    union = tst.UnionType([tst.StringType(), tst.NumberType(), tst.BooleanType(), tst.ObjectType()])
    foo = tst.StringType()

    assert len(union.types) == 4
    assert not union.is_subtype(foo)
    assert foo.is_subtype(union)


def test_union_type_param():
    union1 = tst.UnionType([tst.NumberType(), tst.NullType()])
    union2 = tst.UnionType([tst.StringLiteralType("foo"), tst.NumberType()])
    t_param = tp.TypeParameter("T", bound=union2)

    assert not union2.is_subtype(union1)
    assert not union1.is_subtype(t_param)
    assert not t_param.is_subtype(union1)


def test_union_type_substitution():
    type_param1 = tp.TypeParameter("T1")
    type_param2 = tp.TypeParameter("T2")
    type_param3 = tp.TypeParameter("T3")
    type_param4 = tp.TypeParameter("T4")

    foo = tp.TypeConstructor("Foo", [type_param1, type_param2])
    foo_p = foo.new([tst.NumberType(), type_param3])

    union = tst.UnionType([tst.StringLiteralType("bar"), foo_p])
    ptype = tp.substitute_type(union, {type_param3: type_param4})

    assert ptype.types[1].type_args[0] == tst.NumberType()
    assert ptype.types[1].type_args[1] == type_param4


def test_union_type_substitution_type_var_bound():
    type_param1 = tp.TypeParameter("T1")
    type_param2 = tp.TypeParameter("T2", bound=type_param1)
    type_map = {type_param1: tst.StringType()}

    union = tst.UnionType([tst.NumberType(), type_param2])
    ptype_union = tp.substitute_type(union, type_map)
    ptype = ptype_union.types[1]


    assert ptype.name == type_param2.name
    assert ptype.variance == type_param2.variance
    assert ptype.bound == tst.StringType()


def test_union_to_type_variable_free():
    type_param1 = tp.TypeParameter("T1")
    type_param2 = tp.TypeParameter("T2")
    foo = tp.TypeConstructor("Foo", [type_param1])
    foo_t = foo.new([type_param2])
    union = tst.UnionType([foo_t, tst.StringLiteralType("bar")])

    union_n = union.to_type_variable_free(tst.TypeScriptBuiltinFactory())
    foo_n = union_n.types[0]
    assert foo_n.type_args[0] == tp.WildCardType(tst.ObjectType(), variance=tp.Covariant)

    type_param2.bound = tst.NumberType()
    foo_t = foo.new([type_param2])
    union = tst.UnionType([foo_t, tst.NumberLiteralType(43)])

    union_n = union.to_type_variable_free(tst.TypeScriptBuiltinFactory())
    foo_n = union_n.types[0]
    assert foo_n.type_args[0] == tp.WildCardType(tst.NumberType(), variance=tp.Covariant)

    bar = tp.TypeConstructor("Bar", [tp.TypeParameter("T")])
    bar_p = bar.new([type_param2])
    foo_t = foo.new([bar_p])
    union = tst.UnionType([foo_t, tst.NumberType(), tst.StringType(), tst.AliasType(tst.StringLiteralType("foobar"))])

    union_n = union.to_type_variable_free(tst.TypeScriptBuiltinFactory())
    foo_n = union_n.types[0]
    assert foo_n.type_args[0] == bar.new(
        [tp.WildCardType(tst.NumberType(), variance=tp.Covariant)])


def test_union_type_unification_type_var():
    union = tst.UnionType([tst.StringType(), tst.StringLiteralType("foo")])
    type_param = tp.TypeParameter("T")

    type_var_map = tu.unify_types(union, type_param, tst.TypeScriptBuiltinFactory())
    assert len(type_var_map) == 1
    assert type_var_map == {type_param: union}

    # Case 2: unify a union with a bounded type param, which has an
    # incompatible bound with the given union.
    union = tst.UnionType([tst.NumberType(), tst.StringType()])
    type_param = tp.TypeParameter("T", bound=tst.NumberType())

    type_var_map = tu.unify_types(union, type_param,
                                  tst.TypeScriptBuiltinFactory())
    assert type_var_map == {}


    # Case 3: unify a union with a bounded type param, which has a compatible
    # bound with the given union.
    type_param = tp.TypeParameter("T", bound=union)
    type_var_map = tu.unify_types(union, type_param,
                                  tst.TypeScriptBuiltinFactory())
    assert type_var_map == {type_param: union}

def test_union_type_unification():
    type_param = tp.TypeParameter("T")
    union1 = tst.UnionType([tst.NumberLiteralType(1410), tst.NumberType(), tst.StringType()])
    union2 = tst.UnionType([type_param, tst.NumberType(), tst.StringType()])
    assert union1.is_subtype(union2)

    type_var_map = tu.unify_types(union1, union2, tst.TypeScriptBuiltinFactory())
    assert len(type_var_map) == 1
    assert type_var_map == {type_param: union1.types[0]}

    type_param2 = tp.TypeParameter("G")
    union3 = tst.UnionType([type_param, type_param2, tst.StringLiteralType("foo")])

    type_var_map = tu.unify_types(union1, union3, tst.TypeScriptBuiltinFactory())
    assert len(type_var_map) == 2
    assert type_param, type_param2 in type_var_map
    assert union1.types[1], union1.types[2] in type_var_map.values()


def test_union_type_unification2():
    union = tst.UnionType([tst.NumberType(), tst.StringType()])
    assert tu.unify_types(tst.BooleanType(), union, tst.TypeScriptBuiltinFactory()) == {}

    t1 = tst.NumberType()
    t2 = tst.UnionType([tst.NumberType(), tp.TypeParameter("T")])
    res = tu.unify_types(t1, t2, tst.TypeScriptBuiltinFactory())
    assert len(res) == 1 and res[t2.types[1]] == t1

    t1 = tst.UnionType([tst.NumberType(), tst.StringType()])
    res = tu.unify_types(t1, t2, tst.TypeScriptBuiltinFactory())
    assert len(res) == 1 and res[t2.types[1]] == t1.types[1]

    t1 = tst.UnionType([tst.NumberType(), tst.StringLiteralType("foo"), tst.StringType()])
    res = tu.unify_types(t1, t2, tst.TypeScriptBuiltinFactory())
    assert len(res) == 1 and res[t2.types[1]] == t1.types[2]

    t1 = tst.UnionType([tst.NumberType(), tst.NumberLiteralType(100), tst.BooleanType(), tst.StringLiteralType("foo"), tst.StringType()])

    t_param1 = tp.TypeParameter("T", bound=tst.StringType())
    helper_union = tst.UnionType([tst.BooleanType(), tst.StringType()])
    t_param2 = tp.TypeParameter("G", bound=helper_union)
    t2 = tst.UnionType([tst.NumberType(), t_param1, t_param2])

    # Unify t1: number | 100 | boolean | "foo" | string
    # with t2: number | T extends string | G extends (boolean | string)
    # Result should be {T: StringType, G: BooleanType}
    res = tu.unify_types(t1, t2, tst.TypeScriptBuiltinFactory())
    assert (len(res) == 2 and
            res[t2.types[1]] == t1.types[4] and
            res[t2.types[2]] == t1.types[2])
