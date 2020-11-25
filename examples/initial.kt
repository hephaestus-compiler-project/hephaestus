class InString {
    fun foo(t: String): Unit {

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
