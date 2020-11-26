interface In<in T> {
    fun foo(t: T)
}

class InString : In<String> {
    override fun foo(t: String) {
    }
}

fun <S> select(x: S, y: S): S = x

object AnyObject

fun <T> foo(a: In<T>, b: In<String>) {
    select(a, b).foo(AnyObject)
}

fun main() {
    val a = InString()
    foo(a, a)
}
