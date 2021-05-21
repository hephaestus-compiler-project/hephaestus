class Main {
    static public final void bar(BClass<Double, Integer> y) {

    }
    static public final BClass<Object, Integer> buz() {
        return new BClass<Object, Integer>();
    }
    static public final void foo1(AClass<String> k) {

    }
    static public final void foo2(AClass<Object> n) {

    }
    static public void main() {
        final var a1 = new AClass<String>("a1");
        final var a2 = new AClass<Object>("a2");
        final var a3 = new AClass<Object>("a3");
        final BClass<Object, Integer> b = new BClass<Object, Integer>();
        final BClass<Double, Integer> c = new BClass<Double, Integer>();
        Main.bar(c);
        Main.bar(new BClass<Double, Integer>());
        Main.foo1(a1);
        Main.foo2(a2);
    }
}

interface Function0<A1> {
  public A1 apply();
}

final class AClass<T> {
    public final T x;
    public AClass(T x) {
        this.x = x;
    }

    public final String tmp() {
        return "xxx";
    }
}

final class BClass<X, Y extends Object> {}
