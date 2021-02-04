class Main {
    public static final void main(String[] args) {
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
        super(a)
        this.a = a
    }
}

final class C {}
