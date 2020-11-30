// Transformation: Make type constructor and instantiations

class Child<T>

fun test(t: Child<String>) {
    val child: Child<String> = t
}

fun main() {
    test(Child<String>())
}
