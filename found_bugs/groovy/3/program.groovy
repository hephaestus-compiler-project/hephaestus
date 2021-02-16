@groovy.transform.TypeChecked
class Foo {
  static Number foo() {
    def i = 10  // If I use: `Integer i = 10` it works
    return i
  }
}
