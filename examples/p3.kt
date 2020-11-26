// Transformation3: Replace expected types with their supertypes.
//
// Some some random type declarations and replace them with their supertype.
// Note: The corectness of the program is preserved because during transformation1
// (when we created supertypes), we moved all properties of the subtype to the
// created supertype.


open class NewCls<T> {
    fun foo(t: T): Unit {}
}

class InString : NewCls<String> {
    override fun foo(t: String) {
    }
}

fun select(x: InString, y: InString): InString = x


fun foo(a: NewCls<String>, b: NewCls<String>) {
    select(a, b).foo("foo")
}

fun main() {
    val a = InString()
    foo(a, a)
}
