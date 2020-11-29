// Tranformation: Remove subtype relation


open class Foo
class Bar


fun <T: Foo> foo(): T? {
    return null
}

fun main() {
    val a: Bar? = foo()
}
