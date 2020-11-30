// Transformation: Create supertype

open class Foo
class Bar: Foo


fun foo(): Bar? {
    return null
}

fun main() {
    val a: Foo? = foo()
}
