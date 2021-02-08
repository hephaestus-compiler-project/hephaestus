@groovy.transform.CompileStatic
class Main {
    static Integer bar(Object o) {
        if (o !instanceof Integer) {
            return 0
        } else {
            return o
        }
    }
}
