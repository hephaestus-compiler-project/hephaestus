open class A
open class B: A()
class X<T: A>(val x: T)

fun foo(x: X<A>) = {}

val tmp = if (true) X<A>(A()) else X(B())

fun main() {
   foo(tmp)
}
