class Main {
    static final void bar(BClass<Double, Integer> y) {

    }
    static final BClass<Object, Integer> buz() {
        new BClass<Object, Integer>()
    }
    static final void foo1(AClass<String> k) {

    }
    static final void foo2(AClass<Object> n) {

    }
    public static void main() {
        final def a1 = new AClass<String>("a1")
        final def a2 = new AClass<Object>("a2")
        final def a3 = new AClass<Object>("a3")
        final BClass<Object, Integer> b = new BClass<Object, Integer>()
        final BClass<Double, Integer> c = new BClass<Double, Integer>()
        Main.bar(c)
        Main.bar(new BClass<Double, Integer>())
        Main.foo1(a1)
        Main.foo2(a2)
    }
}

final class AClass<T> {
    public final T x
    public AClass(T x) {
        this.x = x
    }

    final String tmp() {
        "xxx"
    }
}

final class BClass<X, Y extends Object> {}
