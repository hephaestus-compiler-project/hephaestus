// Transformation4: Make function parameterized.
//
// Choose some random types in a function's signature and replace them
// with type parameters.

open class NewCls<T> {
    fun foo(t: T): Unit {}
}

class InString : NewCls<String> {
    override fun foo(t: String) {
    }
}

fun <T> select(x: T, y: T): T = x


fun <T> foo(a: NewCls<T>, b: NewCls<String>) {
    select(a, b).foo("foo")
}

fun main() {
    val a = InString()
    foo(a, a)
}
