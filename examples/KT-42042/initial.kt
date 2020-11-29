class Trivial {
	fun cast(value: String): Any = value
}

fun unsafeCast(value: String): Any {
    val proof: Trivial = Trivial()
    return proof.cast(value)
}

fun main() {
  val d: Any = unsafeCast("foo")
}
