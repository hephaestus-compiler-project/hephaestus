// Transformation1: Add a supertype for a particular class.

// In this example, we created a new supertype for class InString
// Note that in order to preserve the correctness of the program
// the supertype must have the same properties as the subtype.

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
