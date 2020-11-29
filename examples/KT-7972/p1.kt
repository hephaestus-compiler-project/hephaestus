// Tranformations: create generic function

fun <T> List<T>.addAnything(element: T) {
}

fun foo() {
    arrayListOf(1, 2).addAnything(1)
}
