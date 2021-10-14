@groovy.transform.TypeChecked
public class Main {
  public static void foo() {
    int x
    if (true) {
      x = 1
    } else {
      x = 0
    }
  }
  public void bar() {}
  public static void main(String[] args) {
    foo()
  }
}
