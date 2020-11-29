// Tranformations: Create type constructors and
// their instatiations.

sealed class Subtype<A, B> {
    abstract fun cast(value: A): B
    class Trivial<A: B, B> : Subtype<A, B>() {
        override fun cast(value: A): B = value
    }
}


fun unsafeCast(value: String): Any {
    val proof: Subtype<String, Any> = Subtype.Trivial()
    return proof.cast(value)
}

fun main() {
  val d: Any = unsafeCast("foo")
}
