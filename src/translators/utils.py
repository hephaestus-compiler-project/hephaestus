from src.ir import kotlin_types as kt, groovy_types as gt, java_types as jt


def get_type_name(t, get_boxed_void=False):
    t_constructor = getattr(t, 't_constructor', None)
    if not t_constructor:
        if get_boxed_void and isinstance(t, jt.VoidType):
            return "Void"
        return t.get_name()
    if isinstance(t_constructor, gt.ArrayType):
        return "{}[]".format(get_type_name(t.type_args[0].to_type()))
    if isinstance(t_constructor, kt.SpecializedArrayType):
        return "{}Array".format(get_type_name(t.type_args[0].to_type()))
    if isinstance(t_constructor, jt.ArrayType):
        return "{}[]".format(get_type_name(t.type_args[0].to_type()))
    return "{}<{}>".format(t.name, ", ".join([get_type_name(ta.to_type(), True)
                                              for ta in t.type_args]))
