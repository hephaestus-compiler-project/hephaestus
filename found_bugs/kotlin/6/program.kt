class X<T> (val x: T)


open class A {
    open fun foo(): X<A> =
       X(A())
}

class B: A() {
    override fun foo() =
      X(B())
}
