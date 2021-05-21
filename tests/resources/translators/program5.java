class Main {
    static public final void main() {
        Object b = new B("b");
        B ba = new B("ba");
        B bb = ((b instanceof A b_is) ?
                ((b_is instanceof B b_is_is) ?
                 b_is_is :
                 ba) :
                ba);
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
