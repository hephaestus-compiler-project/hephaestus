@groovy.transform.TypeChecked
class Test {
  public static void main(String[] args) {
    println(foo("10"));
  }

  static Integer foo(Object x) {
    if (x instanceof Integer) {
      def bar = {x};
      return bar();
    }
    return 100;
    
  }
}
