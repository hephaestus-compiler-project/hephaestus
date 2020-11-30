// Transformation: Type substitution

open class In<in T>
class Child<T>: In<T>()

fun test(t: In<String>) {
    val child: In<String> = t
}

fun main() {
    test(Child<Any>())
}
