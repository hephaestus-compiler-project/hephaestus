class Main {
    static public final void main() {
        Object b = new B("b");
        A ba = new B("ba");
        A bb = ((b instanceof A b_is) ?
                 b_is :
                  ((Function0<A>)  (() -> {
                    A bc = new B("bc");
                    return bc;
                 })).apply());
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
