// Transformation1: Create a type a constructor.

// 1. Choose some random types defined in a class, and make them type parameters.
// 2. Choose some random points where this class is used, and instantiate
// the new type constructor by providing the concrrete types.

// In this example, we converted class NewCls into a type constructor.
// We then instantiated this type constructor at the following point:
// class InString : NewCls<String> 

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
