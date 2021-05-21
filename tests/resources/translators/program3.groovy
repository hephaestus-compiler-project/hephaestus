class Main {
    public static final void main() {
        A a = new A("a")
        a.foo()
    }
}

class A {
    public final String a

    public A(String a) {
        this.a = a
    }

    void foo() {
        Closure<String> clos = { String i -> {
            String s = "s"
            s
        }}
        println(clos(a))
    }
}
