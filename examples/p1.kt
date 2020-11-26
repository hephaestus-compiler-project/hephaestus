open class NewCls {
    open fun foo(t: String): Unit {}
}

class InString : NewCls {
    override fun foo(t: String) {
    }
}

fun select(x: InString, y: InString): InString = x


fun foo(a: InString, b: InString) {
    select(a, b).foo("foo")
}

fun main() {
    val a = InString()
    foo(a, a)
}
