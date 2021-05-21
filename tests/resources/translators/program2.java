class Main {
    static final String z = "z";
    static final String y = "y";
    static public final String bar(String y) {
        return (Main.z + y);
    }
    static public final A buz() {
        return new A("a");
    }
    static public final void main() {
        A a = new A("a");
        a.foo();
        Main.buz().foo();
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

    public void foo() {
        println(Main.bar(a));
        println(Main.bar(Main.z));
    }
}
