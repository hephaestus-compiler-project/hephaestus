from src.ir import types as tp, kotlin_types as kt, java_types as jt, \
        groovy_types as gt


def test_parameterized_supertypes_simple():
    foo_tparam = tp.TypeParameter("T")
    foo_con = tp.TypeConstructor("Foo", [foo_tparam], [])

    type_param = tp.TypeParameter("K")

    bar_con = tp.TypeConstructor("Bar", [type_param],
                                 [foo_con.new([type_param])])
    bar = bar_con.new([kt.String])

    supertypes = bar.supertypes
    assert len(supertypes) == 1
    assert isinstance(supertypes[0], tp.ParameterizedType)
    assert supertypes[0].type_args == [kt.String]

    # Type constructor hasn't changed.
    assert bar_con.supertypes[0] == tp.ParameterizedType(
        foo_con, [type_param])


def test_parameterized_mix_type_arguments():
    foo_con = tp.TypeConstructor(
        "Foo", [tp.TypeParameter("T1"), tp.TypeParameter("T2")], [])

    type_param = tp.TypeParameter("T1")
    foo_parent = foo_con.new([kt.String,
                              type_param])
    bar_con = tp.TypeConstructor("Bar", [type_param], [foo_parent])
    bar = bar_con.new([kt.Integer])

    supertypes = bar.supertypes
    assert len(supertypes) == 1
    assert supertypes[0].type_args == [kt.String,
                                       kt.Integer]
    assert bar_con.supertypes[0] == foo_parent


def test_parameterized_nested_params():
    foo_con = tp.TypeConstructor(
        "Foo", [tp.TypeParameter("T1")], [])
    bar_con = tp.TypeConstructor(
        "Bar", [tp.TypeParameter("T2")], [])
    type_param = tp.TypeParameter("T")
    bar_parent = bar_con.new(
        [foo_con.new([type_param])])

    baz_con = tp.TypeConstructor("Baz", [type_param], [bar_parent])
    baz = baz_con.new([kt.Boolean])

    supertypes = baz.supertypes
    assert supertypes[0] == tp.ParameterizedType(
        bar_con, [tp.ParameterizedType(
            foo_con, [kt.Boolean])])

def test_parameterized_with_chain_inheritance():
    foo_con = tp.TypeConstructor(
        "Foo", [tp.TypeParameter("T1")], [])
    bar_con = tp.TypeConstructor(
        "Bar", [tp.TypeParameter("T1")],
        [foo_con.new([tp.TypeParameter("T1")])]
    )
    baz_con = tp.TypeConstructor(
        "Bar", [tp.TypeParameter("T1")],
        [bar_con.new([tp.TypeParameter("T1")])])

    baz = baz_con.new([kt.String])

    supertypes = baz.supertypes

    assert supertypes[0].name == "Bar"
    assert supertypes[0].type_args == [kt.String]
    assert supertypes[0].supertypes[0].name == "Foo"
    assert supertypes[0].supertypes[0].type_args == [kt.String]
    assert len(baz.get_supertypes()) == 3


def test_parameterized_with_chain_inheritance_and_nested():
    type_param = tp.TypeParameter("T")
    type_param2 = tp.TypeParameter("K")

    x_con = tp.TypeConstructor(
        "X", [type_param], [])
    z_con = tp.TypeConstructor(
        "Z", [type_param, type_param2], [x_con.new([type_param])])
    y_con = tp.TypeConstructor(
        "Y", [type_param], [z_con.new([kt.String,
                                       type_param])])
    w_con = tp.TypeConstructor(
        "W", [type_param], [y_con.new([type_param])])
    k_con = tp.TypeConstructor(
        "K", [type_param], [])
    r_con = tp.TypeConstructor(
        "R", [type_param], [k_con.new([type_param])])
    test_con = tp.TypeConstructor(
        "Test", [type_param, type_param2],
        [w_con.new([r_con.new([type_param2])])])

    test_type = test_con.new([kt.String,
                              kt.Boolean])

    st = test_type.supertypes[0]
    assert st.name == "W"
    assert len(st.type_args) == 1
    assert st.type_args[0].name == "R"
    assert st.type_args[0].type_args == [kt.Boolean]
    assert st.type_args[0].supertypes[0] == \
        tp.ParameterizedType(k_con, [kt.Boolean])

    st = st.supertypes[0]
    assert st.name == "Y"
    assert st.type_args[0].name == "R"
    assert st.type_args[0].type_args == [kt.Boolean]
    assert st.type_args[0].supertypes[0] == \
        tp.ParameterizedType(k_con, [kt.Boolean])

    st = st.supertypes[0]
    assert st.name == "Z"
    assert st.type_args[0] == kt.String
    assert st.type_args[1].name == "R"
    assert st.type_args[1].type_args == [kt.Boolean]
    assert st.type_args[1].supertypes[0] == \
        tp.ParameterizedType(k_con, [kt.Boolean])

    st = st.supertypes[0]
    assert st.name == "X"
    assert st.type_args == [kt.String]


def test_parameterized_with_bound_abstract():
    type_param = tp.TypeParameter("T")
    type_param2 = tp.TypeParameter("K", bound=type_param)

    x_con = tp.TypeConstructor("X", [type_param, type_param2], [])
    x = x_con.new([kt.Any, kt.String])

    assert x.supertypes == []
    assert x.t_constructor.type_parameters == \
        [type_param, tp.TypeParameter("K", bound=type_param)]


def test_subtype_type_constructor_regular():
    type_param = tp.TypeParameter("T1")
    bar = tp.Classifier("Bar")
    foo = tp.TypeConstructor("Foo", [type_param], [bar])
    assert foo.is_subtype(bar)


def test_subtype_type_constructor_paramerized():
    type_param1 = tp.TypeParameter("T1")
    type_param2 = tp.TypeParameter("T2")
    foo = tp.TypeConstructor("Foo", [type_param1, type_param2])
    bar = tp.TypeConstructor("Bar", [type_param1],
                             [foo.new([kt.String, type_param1])])

    foo_type = foo.new([kt.String, type_param1])
    assert not bar.is_subtype(foo_type)

    bar = tp.TypeConstructor("Bar", [type_param1],
                             [foo.new([kt.String, kt.Integer])])
    foo_type = foo.new([kt.String, kt.Integer])
    assert bar.is_subtype(foo_type)


def test_subtype_covariant_parameterized():
    type_param = tp.TypeParameter("T", tp.Covariant)
    type_param2 = tp.TypeParameter("K", tp.Covariant)
    foo = tp.TypeConstructor("Foo", [type_param], [])
    bar = tp.SimpleClassifier("Bar",
                              [foo.new([kt.String])])

    assert bar.is_subtype(foo.new([kt.String]))
    assert bar.is_subtype(foo.new([kt.Any]))


    foo = tp.TypeConstructor("Foo", [type_param, type_param2], [])
    bar = tp.TypeConstructor("Bar", [type_param, type_param2],
                             [foo.new([type_param,
                                       type_param2])])

    bar_str = bar.new([kt.String, kt.Long])
    bar_any = bar.new([kt.Any, kt.Long])
    foo_str = foo.new([kt.String, kt.Long])
    foo_any = foo.new([kt.Any, kt.Long])

    assert bar_str.is_subtype(foo_str)
    assert bar_str.is_subtype(bar_any)
    assert not foo_any.is_subtype(foo_str)
    assert not bar_any.is_subtype(foo_str)


def test_subtype_contravariant_parameterized():
    type_param = tp.TypeParameter("T", tp.Contravariant)
    foo = tp.TypeConstructor("Foo", [type_param], [])
    bar = tp.TypeConstructor("Bar", [type_param],
                             [foo.new([type_param])])

    bar_str = bar.new([kt.String])
    bar_any = bar.new([kt.Any])
    foo_str = foo.new([kt.String])
    foo_any = foo.new([kt.Any])

    assert bar_str.is_subtype(foo_str)
    assert not bar_str.is_subtype(bar_any)
    assert foo_any.is_subtype(foo_str)
    assert bar_any.is_subtype(foo_str)


def test_primitives_arrays():
    groovy_double_array = gt.Array.new([gt.DoubleType(primitive=True)])
    groovy_boxed_double_array = gt.Array.new([gt.Double])
    java_double_array = jt.Array.new([jt.DoubleType(primitive=True)])
    java_boxed_double_array = jt.Array.new([jt.Double])

    assert groovy_double_array.is_assignable(groovy_boxed_double_array)
    assert groovy_boxed_double_array.is_assignable(groovy_double_array)
    assert not java_double_array.is_assignable(java_boxed_double_array)
    assert not java_boxed_double_array.is_assignable(java_double_array)


def test_use_site_variance():
    type_param = tp.TypeParameter("T")
    foo = tp.TypeConstructor("Foo", [type_param], [])
    foo_any_co = foo.new([tp.WildCardType(kt.Any, tp.Covariant)])

    foo_any = foo.new([kt.Any])
    foo_string = foo.new([kt.String])
    assert foo_any.is_subtype(foo_any_co)
    assert foo_string.is_subtype(foo_any_co)
    assert not foo_any_co.is_subtype(foo_any)

    foo_number_contra = foo.new([tp.WildCardType(
        kt.Number, tp.Contravariant)])
    foo_number = foo.new([kt.Number])
    foo_integer = foo.new([kt.Integer])

    assert foo_number.is_subtype(foo_number_contra)
    assert foo_any.is_subtype(foo_number_contra)
    assert not foo_integer.is_subtype(foo_number_contra)
    assert not foo_string.is_subtype(foo_number_contra)
    assert not foo_any_co.is_subtype(foo_number_contra)
    assert not foo_number_contra.is_subtype(foo_any_co)


def test_use_site_variance_type_vars():
    type_param1 = tp.TypeParameter("T1")
    type_param2 = tp.TypeParameter("T2")
    foo = tp.TypeConstructor("Foo", [type_param1, type_param2])
    type_param3 = tp.TypeParameter("T3", bound=kt.String)
    foo_t = foo.new([type_param3, type_param3])
    foo_c = foo.new([type_param3, tp.WildCardType(type_param3, tp.Covariant)])

    assert not foo_c.is_subtype(foo_t)
    assert not foo_t.is_subtype(foo_c)


def test_use_site_variance_covariant_decl():
    type_param = tp.TypeParameter("T", tp.Covariant)
    foo = tp.TypeConstructor("Foo", [type_param], [])
    foo_any_co = foo.new([tp.WildCardType(kt.Any, tp.Covariant)])

    foo_any = foo.new([kt.Any])
    foo_string = foo.new([kt.String])
    foo_string_co = foo.new([tp.WildCardType(kt.String, tp.Covariant)])
    assert foo_any.is_subtype(foo_any_co)
    assert foo_string.is_subtype(foo_any_co)
    assert foo_any_co.is_subtype(foo_any)
    assert foo_string_co.is_subtype(foo_any_co)


def test_use_site_variance_contravariant_decl():
    type_param = tp.TypeParameter("T", tp.Contravariant)
    foo = tp.TypeConstructor("Foo", [type_param], [])
    foo_number_contra = foo.new([tp.WildCardType(kt.Number, tp.Contravariant)])

    foo_any = foo.new([kt.Any])
    foo_number = foo.new([kt.Number])
    foo_integer = foo.new([kt.Integer])
    foo_integer_co = foo.new([tp.WildCardType(kt.Integer, tp.Contravariant)])
    print('HEEERE')
    assert foo_any.is_subtype(foo_number_contra)
    assert not foo_integer.is_subtype(foo_number_contra)
    assert foo_number_contra.is_subtype(foo_number)
    assert not foo_integer.is_subtype(foo_number_contra)
    assert not foo_integer_co.is_subtype(foo_number_contra)


def test_get_type_variables():
    factory = kt.KotlinBuiltinFactory()
    type_param1 = tp.TypeParameter("T1")
    type_param2 = tp.TypeParameter("T2")
    foo = tp.TypeConstructor("Foo", [type_param1, type_param2])
    foo1 = foo.new([kt.String, kt.Integer])
    assert not foo1.get_type_variables(factory)

    foo2 = foo.new([type_param1, kt.String])
    type_vars = foo2.get_type_variables(factory)
    assert len(type_vars) == 1
    assert type_vars[type_param1] == {None}

    bar = tp.TypeConstructor("Bar", [type_param2])
    foo3 = foo.new([type_param1,
                    bar.new([type_param2])])
    type_vars = foo3.get_type_variables(factory)
    assert len(type_vars) == 2
    assert type_vars[type_param1] == {None}
    assert type_vars[type_param2] == {None}


    # with wildcard type
    foo4 = foo.new([type_param1, tp.WildCardType(type_param2, tp.Covariant)])
    type_vars = foo4.get_type_variables(factory)
    assert len(type_vars) == 2
    assert type_vars[type_param1] == {None}
    assert type_vars[type_param2] == {None}


def test_type_substitution():
    type_param1 = tp.TypeParameter("T1")
    type_param2 = tp.TypeParameter("T2")
    type_param3 = tp.TypeParameter("T3")
    type_param4 = tp.TypeParameter("T4")

    foo = tp.TypeConstructor("Foo", [type_param1, type_param2])
    foo_p = foo.new([kt.Integer, type_param3])

    ptype = tp.substitute_type(foo_p, {type_param3: type_param4})
    assert ptype.type_args[0] == kt.Integer
    assert ptype.type_args[1] == type_param4


def test_type_substitution_type_var_bound():
    type_param1 = tp.TypeParameter("T1")
    type_param2 = tp.TypeParameter("T2", bound=type_param1)
    type_map = {type_param1: kt.String}

    ptype = tp.substitute_type(type_param2, type_map)
    assert ptype.name == type_param2.name
    assert ptype.variance == type_param2.variance
    assert ptype.bound == kt.String

    ptype = tp.substitute_type(type_param2, {})
    assert ptype == type_param2

def test_type_substitution_wildcards():
    type_param1 = tp.TypeParameter("T1")
    type_param2 = tp.TypeParameter("T2")
    wildcard = tp.WildCardType(type_param1, tp.Covariant)
    type_map = {type_param1: type_param2}

    ptype = tp.substitute_type(wildcard, type_map)

    assert ptype.variance.is_covariant()
    assert ptype.bound == type_param2

    # case 2: substitute a parameterized type with wildcards
    foo = tp.TypeConstructor("Foo", [type_param1, type_param2])
    foo_t = foo.new([type_param1, tp.WildCardType(type_param1,
                                                  tp.Covariant)])
    t = tp.WildCardType(type_param2, tp.Covariant)
    type_map = {type_param1: t}

    ptype = tp.substitute_type(foo_t, type_map)
    assert ptype.type_args[0] == t
    assert ptype.type_args[1] == tp.WildCardType(t, tp.Covariant)


def test_to_type_variable_free():
    type_param1 = tp.TypeParameter("T1")
    type_param2 = tp.TypeParameter("T2")
    foo = tp.TypeConstructor("Foo", [type_param1])
    foo_t = foo.new([type_param2])

    foo_n = foo_t.to_type_variable_free(kt.KotlinBuiltinFactory())
    assert foo_n.type_args[0] == tp.WildCardType(kt.Any, variance=tp.Covariant)

    type_param2.bound = kt.Number
    foo_t = foo.new([type_param2])

    foo_n = foo_t.to_type_variable_free(kt.KotlinBuiltinFactory())
    assert foo_n.type_args[0] == tp.WildCardType(kt.Number, variance=tp.Covariant)

    bar = tp.TypeConstructor("Bar", [tp.TypeParameter("T")])
    bar_p = bar.new([type_param2])
    foo_t = foo.new([bar_p])

    foo_n = foo_t.to_type_variable_free(kt.KotlinBuiltinFactory())
    assert foo_n.type_args[0] == bar.new(
        [tp.WildCardType(kt.Number, variance=tp.Covariant)])


def test_wildcard_types():
    t1 = tp.WildCardType()
    t2 = tp.WildCardType()

    assert not t1.is_subtype(t2)
    assert not t2.is_subtype(t1)

    t1 = tp.WildCardType(kt.Any, tp.Covariant)
    t2 = tp.WildCardType(kt.Number, tp.Covariant)

    assert t2.is_subtype(t1)
    assert not t1.is_subtype(t2)

    t1 = tp.WildCardType(kt.Any, tp.Covariant)
    t2 = tp.WildCardType(kt.Any, tp.Contravariant)

    assert not t1.is_subtype(t2)
    assert not t2.is_subtype(t1)


def test_get_bound_rec_wildcards():
    type_param = tp.TypeParameter("T")
    wildcard = tp.WildCardType(type_param, tp.Covariant)
    assert wildcard.get_bound_rec() == type_param
