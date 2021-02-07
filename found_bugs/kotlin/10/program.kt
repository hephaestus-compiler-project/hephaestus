fun main() {
	val x = if (true) 1 as Number else false // inferred type is java.io.Serializable
	x == 1
}
