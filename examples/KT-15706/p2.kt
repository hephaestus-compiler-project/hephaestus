// Transformation: Make supertype

open class In<in T>
class Child<T>: In<T>()

fun test(t: Child<String>) {
    val child: Child<String> = t
}

fun main() {
    test(Child<String>())
}
