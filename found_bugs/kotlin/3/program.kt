fun foo(x: Any): String {
    if (x is String) {
        val thunk = {x}
        return thunk()
    } else
        return "str"
}
