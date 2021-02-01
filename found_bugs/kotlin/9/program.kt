open class A<T: Char>(open var x: T)
open class B<T: Char>(open override var x: T): A<T>(x)
class C(override var x: Char): B<Char>('x')
