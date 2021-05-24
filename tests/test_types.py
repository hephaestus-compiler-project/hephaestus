from src.ir import types as tp, kotlin_types as kt, java_types as jt, \
        groovy_types as gt


def test_parameterized_supertypes_simple():
    foo_tparam = tp.TypeParameter("T")
    foo_con = tp.TypeConstructor("Foo", [foo_tparam], [])

    type_param = tp.TypeParameter("K")

    bar_con = tp.TypeConstructor("Bar", [type_param],
                                 [foo_con.new([type_param.to_type_arg()])])
    bar = bar_con.new([kt.String.to_type_arg()])

    supertypes = bar.supertypes
    assert len(supertypes) == 1
    assert isinstance(supertypes[0], tp.ParameterizedType)
    assert supertypes[0].type_args == [kt.String.to_type_arg()]

    # Type constructor hasn't changed.
    assert bar_con.supertypes[0] == tp.ParameterizedType(
        foo_con, [type_param.to_type_arg()])


def test_parameterized_mix_type_arguments():
    foo_con = tp.TypeConstructor(
        "Foo", [tp.TypeParameter("T1"), tp.TypeParameter("T2")], [])

    type_param = tp.TypeParameter("T1")
    foo_parent = foo_con.new([kt.String.to_type_arg(),
                              type_param.to_type_arg()])
    bar_con = tp.TypeConstructor("Bar", [type_param], [foo_parent])
    bar = bar_con.new([kt.Integer.to_type_arg()])

    supertypes = bar.supertypes
    assert len(supertypes) == 1
    assert supertypes[0].type_args == [kt.String.to_type_arg(),
                                       kt.Integer.to_type_arg()]
    assert bar_con.supertypes[0] == foo_parent


def test_parameterized_nested_params():
    foo_con = tp.TypeConstructor(
        "Foo", [tp.TypeParameter("T1")], [])
    bar_con = tp.TypeConstructor(
        "Bar", [tp.TypeParameter("T2")], [])
    type_param = tp.TypeParameter("T")
    bar_parent = bar_con.new(
        [foo_con.new([type_param.to_type_arg()]).to_type_arg()])

    baz_con = tp.TypeConstructor("Baz", [type_param], [bar_parent])
    baz = baz_con.new([kt.Boolean.to_type_arg()])

    supertypes = baz.supertypes
    assert supertypes[0] == tp.ParameterizedType(
        bar_con, [tp.ParameterizedType(
            foo_con, [kt.Boolean.to_type_arg()]).to_type_arg()])

def test_parameterized_with_chain_inheritance():
    foo_con = tp.TypeConstructor(
        "Foo", [tp.TypeParameter("T1")], [])
    bar_con = tp.TypeConstructor(
        "Bar", [tp.TypeParameter("T1")],
        [foo_con.new([tp.TypeParameter("T1").to_type_arg()])]
    )
    baz_con = tp.TypeConstructor(
        "Bar", [tp.TypeParameter("T1")],
        [bar_con.new([tp.TypeParameter("T1").to_type_arg()])])

    baz = baz_con.new([kt.String.to_type_arg()])

    supertypes = baz.supertypes

    assert supertypes[0].name == "Bar"
    assert supertypes[0].type_args == [kt.String.to_type_arg()]
    assert supertypes[0].supertypes[0].name == "Foo"
    assert supertypes[0].supertypes[0].type_args == [kt.String.to_type_arg()]
    assert len(baz.get_supertypes()) == 3


def test_parameterized_with_chain_inheritance_and_nested():
    type_param = tp.TypeParameter("T")
    type_param2 = tp.TypeParameter("K")

    x_con = tp.TypeConstructor(
        "X", [type_param], [])
    z_con = tp.TypeConstructor(
        "Z", [type_param, type_param2], [x_con.new([type_param.to_type_arg()])])
    y_con = tp.TypeConstructor(
        "Y", [type_param], [z_con.new([kt.String.to_type_arg(),
                                       type_param.to_type_arg()])])
    w_con = tp.TypeConstructor(
        "W", [type_param], [y_con.new([type_param.to_type_arg()])])
    k_con = tp.TypeConstructor(
        "K", [type_param], [])
    r_con = tp.TypeConstructor(
        "R", [type_param], [k_con.new([type_param.to_type_arg()])])
    test_con = tp.TypeConstructor(
        "Test", [type_param, type_param2],
        [w_con.new([r_con.new([type_param2.to_type_arg()]).to_type_arg()])])

    test_type = test_con.new([kt.String.to_type_arg(),
                              kt.Boolean.to_type_arg()])

    st = test_type.supertypes[0]
    assert st.name == "W"
    assert len(st.type_args) == 1
    assert st.type_args[0].name == "R"
    assert st.type_args[0].to_type().type_args == [kt.Boolean.to_type_arg()]
    assert st.type_args[0].to_type().supertypes[0] == \
        tp.ParameterizedType(k_con, [kt.Boolean.to_type_arg()])

    st = st.supertypes[0]
    assert st.name == "Y"
    assert st.type_args[0].name == "R"
    assert st.type_args[0].to_type().type_args == [kt.Boolean.to_type_arg()]
    assert st.type_args[0].to_type().supertypes[0] == \
        tp.ParameterizedType(k_con, [kt.Boolean.to_type_arg()])

    st = st.supertypes[0]
    assert st.name == "Z"
    assert st.type_args[0] == kt.String.to_type_arg()
    assert st.type_args[1].name == "R"
    assert st.type_args[1].to_type().type_args == [kt.Boolean.to_type_arg()]
    assert st.type_args[1].to_type().supertypes[0] == \
        tp.ParameterizedType(k_con, [kt.Boolean.to_type_arg()])

    st = st.supertypes[0]
    assert st.name == "X"
    assert st.type_args == [kt.String.to_type_arg()]


def test_parameterized_with_bound_abstract():
    type_param = tp.TypeParameter("T")
    type_param2 = tp.TypeParameter("K", bound=type_param)

    x_con = tp.TypeConstructor("X", [type_param, type_param2], [])
    x = x_con.new([kt.Any.to_type_arg(), kt.String.to_type_arg()])

    assert x.supertypes == []
    assert x.t_constructor.type_parameters == \
        [type_param, tp.TypeParameter("K", bound=type_param)]


def test_subtype_covariant_parameterized():
    type_param = tp.TypeParameter("T", tp.Covariant)
    type_param2 = tp.TypeParameter("K", tp.Covariant)
    foo = tp.TypeConstructor("Foo", [type_param], [])
    bar = tp.SimpleClassifier("Bar",
                              [foo.new([kt.String.to_type_arg()])])

    assert bar.is_subtype(foo.new([kt.String.to_type_arg()]))
    assert bar.is_subtype(foo.new([kt.Any.to_type_arg()]))


    foo = tp.TypeConstructor("Foo", [type_param, type_param2], [])
    bar = tp.TypeConstructor("Bar", [type_param, type_param2],
                             [foo.new([type_param.to_type_arg(),
                                       type_param2.to_type_arg()])])

    bar_str = bar.new([kt.String.to_type_arg(), kt.Long.to_type_arg()])
    bar_any = bar.new([kt.Any.to_type_arg(), kt.Long.to_type_arg()])
    foo_str = foo.new([kt.String.to_type_arg(), kt.Long.to_type_arg()])
    foo_any = foo.new([kt.Any.to_type_arg(), kt.Long.to_type_arg()])

    assert bar_str.is_subtype(foo_str)
    assert bar_str.is_subtype(bar_any)
    assert not foo_any.is_subtype(foo_str)
    assert not bar_any.is_subtype(foo_str)


def test_subtype_contravariant_parameterized():
    type_param = tp.TypeParameter("T", tp.Contravariant)
    foo = tp.TypeConstructor("Foo", [type_param], [])
    bar = tp.TypeConstructor("Bar", [type_param],
                             [foo.new([type_param.to_type_arg()])])

    bar_str = bar.new([kt.String.to_type_arg()])
    bar_any = bar.new([kt.Any.to_type_arg()])
    foo_str = foo.new([kt.String.to_type_arg()])
    foo_any = foo.new([kt.Any.to_type_arg()])

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
    foo_any_co = foo.new([kt.Any.to_type_arg(tp.Covariant)])

    foo_any = foo.new([kt.Any.to_type_arg()])
    foo_string = foo.new([kt.String.to_type_arg()])
    assert foo_any.is_subtype(foo_any_co)
    assert foo_string.is_subtype(foo_any_co)
    assert not foo_any_co.is_subtype(foo_any)

    foo_number_contra = foo.new([kt.Number.to_type_arg(tp.Contravariant)])
    foo_number = foo.new([kt.Number.to_type_arg()])
    foo_integer = foo.new([kt.Integer.to_type_arg()])

    assert foo_number.is_subtype(foo_number_contra)
    assert foo_any.is_subtype(foo_number_contra)
    assert not foo_integer.is_subtype(foo_number_contra)
    assert not foo_string.is_subtype(foo_number_contra)
    assert not foo_any_co.is_subtype(foo_number_contra)
    assert not foo_number_contra.is_subtype(foo_any_co)


def test_use_site_variance_covariant_decl():
    type_param = tp.TypeParameter("T", tp.Covariant)
    foo = tp.TypeConstructor("Foo", [type_param], [])
    foo_any_co = foo.new([kt.Any.to_type_arg(tp.Covariant)])

    foo_any = foo.new([kt.Any.to_type_arg()])
    foo_string = foo.new([kt.String.to_type_arg()])
    foo_string_co = foo.new([kt.String.to_type_arg(tp.Covariant)])
    assert foo_any.is_subtype(foo_any_co)
    assert foo_string.is_subtype(foo_any_co)
    assert foo_any_co.is_subtype(foo_any)
    assert foo_string_co.is_subtype(foo_any_co)


def test_use_site_variance_contravariant_decl():
    type_param = tp.TypeParameter("T", tp.Contravariant)
    foo = tp.TypeConstructor("Foo", [type_param], [])
    foo_number_contra = foo.new([kt.Number.to_type_arg(tp.Contravariant)])

    foo_any = foo.new([kt.Any.to_type_arg()])
    foo_number = foo.new([kt.Number.to_type_arg()])
    foo_integer = foo.new([kt.Integer.to_type_arg()])
    foo_integer_co = foo.new([kt.Integer.to_type_arg(tp.Contravariant)])
    assert foo_any.is_subtype(foo_number_contra)
    assert not foo_integer.is_subtype(foo_number_contra)
    assert foo_number_contra.is_subtype(foo_number)
    assert not foo_integer.is_subtype(foo_number_contra)
    assert not foo_integer_co.is_subtype(foo_number_contra)
