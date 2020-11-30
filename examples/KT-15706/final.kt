// Transformation: Incorrect subtype relation


open class In<in I>
class Child<T> : In<T>()

fun test(t: In<String>) {
    if (t is Child) {
        val child: Child<String> = t
    }
}

fun main() {
    val t: Child<String> = Child<Any>()
    test(Child<Any>())
}
