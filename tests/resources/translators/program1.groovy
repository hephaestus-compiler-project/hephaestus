class Main {
    public static final void main() {
        B b = new B("b")
        A ba = new B("ba")
    }
}

class A {
    public final String a

    public A(String a) {
        this.a = a
    }

}

class B extends A {
    public final String a
    public B(String a) {
        this.a = a
    }
}

final class C {}
