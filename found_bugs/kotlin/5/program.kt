open class A
class B: A()


fun foo(a: B) = {}

fun main() {
    var x: A = B()
    foo(x) // does not compile

    x = B()
    foo(x) // this works
}
