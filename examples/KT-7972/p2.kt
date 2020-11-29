// Tranformations: Cast to subtype


fun <T> List<T>.addAnything(element: T) {
    if (this is MutableList<T>) {

    }
}

fun foo() {
    arrayListOf(1, 2).addAnything(1)
}
