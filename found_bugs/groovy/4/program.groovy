interface I1<X, Y> {}

interface I2 extends I1<Character, Character> {}

class Foo<X, Y> implements I2 {
  public void foo(X x, Y y) {}
}

class Bar<X, Y> extends Foo<X, Y> {}

@groovy.transform.TypeChecked
class Main {
  public static void foo() {
    new Bar<Float, Integer>().foo((Float) 1.4, -1)
  }
}
