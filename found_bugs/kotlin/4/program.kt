interface R<T>
interface W
interface J
open class A
open class B: A(), R<W>
open class E: A(), R<J>
open class C {
    open fun foo(): A = B()    
}
class D: C() {
    override fun foo() = if (true) B() else E()
}
