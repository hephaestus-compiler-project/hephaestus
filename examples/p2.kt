open class NewCls<T> {
    open fun foo(t: T): Unit {}
}

class InString : NewCls<String> {
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
