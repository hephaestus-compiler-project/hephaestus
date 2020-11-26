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
