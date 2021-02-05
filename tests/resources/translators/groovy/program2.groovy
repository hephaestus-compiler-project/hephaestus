class Main {
    static final String z = "z"
    static final String y = "y"
    static final String bar(String y) {
        (Main.z + y)
    }
    static final A buz() {
        new A("a")
    }
    public static final void main() {
        A a = new A("a")
        a.foo()
        Main.buz().foo()
    }
}

class A {
    public final String a

    public A(String a) {
        this.a = a
    }

    void foo() {
        println(Main.bar(a))
        println(Main.bar(Main.z))
    }
}
