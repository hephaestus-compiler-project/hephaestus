// Tranformation: Type arguments that do not respect
// type parameters bounds.


sealed class Subtype<A, B> {
    abstract fun cast(value: A): B
    class Trivial<A: B, B> : Subtype<A, B>() {
        override fun cast(value: A): B = value
    }
}

class B

fun unsafeCast(value: String): B {
    val proof: Subtype<String, B> = Subtype.Trivial()
    return proof.cast(value)
}


fun main() {
  val d: B = unsafeCast("foo")
}
