// Transformation: Generic function (with bounds)

open class Foo
class Bar: Foo


fun <T: Foo> foo(): T? {
    return null
}

fun main() {
    val a: Bar? = foo()
}
