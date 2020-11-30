// Transformation: Smart cast

open class In<in T>
class Child<T>: In<T>()

fun test(t: In<String>) {
    if (t is Child) {
        val child: In<String> = t
    }
}

fun main() {
    test(Child<Any>())
}
