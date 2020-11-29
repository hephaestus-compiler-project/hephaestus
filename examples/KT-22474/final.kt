// Transformation5 (Fault Injection): Replace value with a value that is not
// subtype of the expected type.

// In this example, we replace a string value with a value of type AnyClass.


open class NewCls<in T> {
    open fun foo(t: T): Unit {}
}

class InString : NewCls<String>() {
    override fun foo(t: String) {
        println(t.length)
    }
}

fun <T> select(x: T, y: T): T = x

class AnyClass

fun <T> foo(a: NewCls<T>, b: NewCls<String>) {
    select(a, b).foo(AnyClass())
}

fun main() {
    val a = InString()
    foo(a, a)
}
