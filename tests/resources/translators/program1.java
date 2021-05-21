class Main {
    static public final void main() {
        B b = new B("b");
        A ba = new B("ba");
    }
}

interface Function0<A1> {
  public A1 apply();
}

class A {
    public final String a;

    public A(String a) {
        this.a = a;
    }

}

class B extends A {
    public final String a;
    public B(String a) {
        super("b");
        this.a = a;
    }
}

final class C {}
