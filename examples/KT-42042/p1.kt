// Transformation. Create supertype interface

sealed class Subtype {
    abstract fun cast(value: String): Any
    class Trivial : Subtype() {
        override fun cast(value: String): Any = value
    }
}


fun unsafeCast(value: String): Any {
    val proof: Subtype = Subtype.Trivial()
    return proof.cast(value)
}

fun main() {
  val d: Any = unsafeCast("foo")
}
