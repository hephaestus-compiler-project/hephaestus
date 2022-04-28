Hephaestus
==========

Hephaestus is a testing framework for validating static typing procedures
in compilers. This is done by a combination of
program generation and transformation-based compiler testing.

Currently, Hephaestus has been used to test the type checkers of
three popular programming languages: Java, Kotlin, and Groovy.


## Program Generation

Hephaestus' program generation comes with three
important characteristics.
First, it produces *semantically valid* programs;
rejecting a well-formed program produced by our
generator indicates a potential compiler bug
(test oracle).
Second,
the resulting programs rely heavily on
parametric polymorphism
(e.g., use of parameterized classes / functions,
etc.)
Third,
to test compilers of different languages
our generator yields programs at a higher-level of abstraction,
and then uses translation mechanisms to
convert the "abstract" programs into the target language.
Currently, our generator produces programs written in
three popular programming languages,
namely, Java, Kotlin, and Groovy.


## Transformation-based Compiler Testing

Beyond program generation,
Hephaestus also supports transformation-based compiler testing
by introducing two mutations,
*type erasure mutation* and *type overwriting mutation*.
Their goal is to exercise compilers' type inference algorithms
and other type-related operations.
Given an input program `P`,
the type erasure mutation removes declared types from variables and parameters,
or type arguments from parameterized constructor and method calls,
while preserving the well-formedness of `P`.
The type overwriting mutation adopts a fault-injecting approach,
and introduces a type error in `P`
by replacing a type `t1` with another incompatible type `t2`.
The type overwriting mutation updates the test oracle,
as compiling a program obtained from this mutation
indicates a potential soundness bug in the compiler under test.


# Requirements

* Python: 3.8+

# Getting Started

## Usage

```
./hephaestus.py --help
usage: hephaestus.py [-h] [-s SECONDS] [-i ITERATIONS] [-t TRANSFORMATIONS] [--batch BATCH] [-b BUGS] [-n NAME] [-T [{TypeErasure} [{TypeErasure} ...]]]
                     [--transformation-schedule TRANSFORMATION_SCHEDULE] [-R REPLAY] [-e] [-k] [-S] [-w WORKERS] [-d] [-r] [-F LOG_FILE] [-L] [-N] [--language {kotlin,groovy,java}]
                     [--max-type-params MAX_TYPE_PARAMS] [--max-depth MAX_DEPTH] [-P] [--timeout TIMEOUT] [--cast-numbers] [--disable-use-site-variance] [--disable-contravariance-use-site]
                     [--disable-bounded-type-parameters] [--disable-parameterized-functions]

optional arguments:
  -h, --help            show this help message and exit
  -s SECONDS, --seconds SECONDS
                        Timeout in seconds
  -i ITERATIONS, --iterations ITERATIONS
                        Iterations to run (default: 3)
  -t TRANSFORMATIONS, --transformations TRANSFORMATIONS
                        Number of transformations in each round (default: 0)
  --batch BATCH         Number of programs to generate before invoking the compiler
  -b BUGS, --bugs BUGS  Set bug directory (default: /home/hephaestus/bugs)
  -n NAME, --name NAME  Set name of this testing instance (default: random string)
  -T [{TypeErasure} [{TypeErasure} ...]], --transformation-types [{TypeErasure} [{TypeErasure} ...]]
                        Select specific transformations to perform
  --transformation-schedule TRANSFORMATION_SCHEDULE
                        A file containing the schedule of transformations
  -R REPLAY, --replay REPLAY
                        Give a program to use instead of a randomly generated (pickled)
  -e, --examine         Open ipdb for a program (can be used only with --replay option)
  -k, --keep-all        Save all programs
  -S, --print-stacktrace
                        When an error occurs print stack trace
  -w WORKERS, --workers WORKERS
                        Number of workers for processing test programs
  -d, --debug
  -r, --rerun           Run only the last transformation. If failed, start from the last and go back until the transformation introduces the error
  -F LOG_FILE, --log-file LOG_FILE
                        Set log file (default: /home/hephaestus/logs)
  -L, --log             Keep logs for each transformation (bugs/session/logs)
  -N, --dry-run         Do not compile the programs
  --language {kotlin,groovy,java}
                        Select specific language
  --max-type-params MAX_TYPE_PARAMS
                        Maximum number of type parameters to generate
  --max-depth MAX_DEPTH
                        Generate programs up to the given depth
  -P, --only-correctness-preserving-transformations
                        Use only correctness-preserving transformations
  --timeout TIMEOUT     Timeout for transformations (in seconds)
  --cast-numbers        Cast numeric constants to their actual type (this option is used to avoid re-occrrence of a specific Groovy bug)
  --disable-use-site-variance
                        Disable use-site variance
  --disable-contravariance-use-site
                        Disable contravariance in use-site variance
  --disable-bounded-type-parameters
                        Disable bounded type parameters
  --disable-parameterized-functions
                        Disable parameterized functions

```

## Run Tests

To run `hephaestus` tests you should execute the following commands:

```
python setup.py test
```

The output of the previous command should be similar to the following:

```
tests/test_call_analysis.py::test_program1 PASSED                       [  0%]
...
tests/test_use_analysis.py::test_program7 PASSED                        [100%]
tests/test_use_analysis.py::test_program8 PASSED                        [100%]
============================ 154 passed in 0.55s =============================
```

## Example: Testing the Java compiler

Here, we will test `javac` by employing Hephaestus's program
generator. Specifically, we will produce 30 test programs in batches of 10
test programs using two workers with the following command.
The name of testing session is "mysession".

```
./hephaestus.py --language java --transformations 0 \
    --batch 10 --iterations 30 --workers 2 -P \
    --name mysession
```

The expected outcome is:

```
stop_cond             iterations (30)
transformations       0
transformation_types  TypeErasure
bugs                  /home/hephaestus/bugs
name                  mysession
language              java
compiler              javac 18-ea
===============================================================================================================================================================================================
Test Programs Passed 30 / 30 ✔          Test Programs Failed 0 / 30 ✘
Total faults: 0
```

Two files are generated inside `/home/hephaestus/bugs/mysession`:
`stats.json` and `faults.json`.

`stats.json` contains the following details about the testing session.

```
{
  "Info": {
    "stop_cond": "iterations",
    "stop_cond_value": 30,
    "transformations": 0,
    "transformation_types": "TypeErasure",
    "bugs": "/home/hephaestus/bugs",
    "name": "mysession",
    "language": "java",
    "compiler": "javac 18-ea"
  },
  "totals": {
    "passed": 30,
    "failed": 0
  }
}
```

In this example, `faults.json` is empty. If there were some bugs detected,
`faults.json` would look like the following JSON file.

```
{
  "7": {
    "transformations": [
      "TypeErasure"
    ],
    "error": " 18: [Static type checking] - Incompatible generic argument types. Cannot assign src.easy.Function2<java.lang.Double, java.lang.Float, ?> to: src.easy.Function2<java.lang.Double, java.lang.Float, ? extends java.lang.Object>\n @ line 18, column 5.\n       gurgling\n       ^",
    "programs": {
      "/tmp/tmpyp4u90z5/src/easy/Main.groovy": true
    }
  },
  "11": {
    "transformations": [
        "TypeOverwriting"
    ],
    "error": "SHOULD NOT BE COMPILED: X <: N expected but Imagine <: (Playing<Function1<Boolean(groovy-builtin), Float(groovy-builtin)>>) found in node global/Reconcile/reflexes/soybeans/cellos",
    "programs": {
      "/tmp/tmpmtyy6u6q/src/spanners/Main.groovy": true,
      "/tmp/tmpmtyy6u6q/src/franker/Main.groovy": false
    }
  },
  "1050": {
    "transformations": [
      "TypeErasure"
    ],
    "error": ">>> a serious error occurred: BUG! exception in phase 'instruction selection' in source unit '/tmp/tmphj006wfu/src/wack/Main.groovy' unexpected NullPointerException\n>>> stacktrace:\nBUG! exception in phase 'instruction selection' in source unit '/tmp/tmphj006wfu/src/wack/Main.groovy' unexpected NullPointerException\n\tat org.codehaus.groovy.control.CompilationUnit$IPrimaryClassNodeOperation.doPhaseOperation(CompilationUnit.java:905)\n\tat org.codehaus.groovy.control.CompilationUnit.processPhaseOperations(CompilationUnit.java:654)\n\tat org.codehaus.groovy.control.CompilationUnit.compile(CompilationUnit.java:628)\n\tat org.codehaus.groovy.control.CompilationUnit.compile(CompilationUnit.java:609)\n\tat org.codehaus.groovy.tools.FileSystemCompiler.compile(FileSystemCompiler.java:311)\n\tat org.codehaus.groovy.tools.FileSystemCompiler.doCompilation(FileSystemCompiler.java:240)\n\tat org.codehaus.groovy.tools.FileSystemCompiler.commandLineCompile(FileSystemCompiler.java:165)\n\tat org.codehaus.groovy.tools.FileSystemCompiler.commandLineCompileWithErrorHandling(FileSystemCompiler.java:205)\n\tat org.codehaus.groovy.tools.FileSystemCompiler.main(FileSystemCompiler.java:189)\n\tat java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)\n\tat java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:77)\n\tat java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)\n\tat java.base/java.lang.reflect.Method.invoke(Method.java:568)\n\tat org.codehaus.groovy.tools.GroovyStarter.rootLoader(GroovyStarter.java:112)\n\tat org.codehaus.groovy.tools.GroovyStarter.main(GroovyStarter.java:130)\nCaused by: java.lang.NullPointerException: Cannot invoke \"org.codehaus.groovy.ast.stmt.Statement.visit(org.codehaus.groovy.ast.GroovyCodeVisitor)\" because the return value of \"org.codehaus.groovy.ast.MethodNode.getCode()\" is null\n\tat org.codehaus.groovy.transform.stc.StaticTypeCheckingVisitor.isTypeSource(StaticTypeCheckingVisitor.java:4189)\n\tat org.codehaus.groovy.transform.stc.StaticTypeCheckingVisitor.checkForTargetType(StaticTypeCheckingVisitor.java:4160)\n\tat org.codehaus.groovy.transform.stc.StaticTypeCheckingVisitor.visitTernaryExpression(StaticTypeCheckingVisitor.java:4136)\n\tat org.codehaus.groovy.ast.expr.TernaryExpression.visit(TernaryExpression.java:44)\n\tat org.codehaus.groovy.transform.stc.StaticTypeCheckingVisitor.visitMethodCallExpression(StaticTypeCheckingVisitor.java:3303)\n\tat org.codehaus.groovy.transform.sc.StaticCompilationVisitor.visitMethodCallExpression(StaticCompilationVisitor.java:421)\n\tat org.codehaus.groovy.ast.expr.MethodCallExpression.visit(MethodCallExpression.java:77)\n\tat org.codehaus.groovy.ast.CodeVisitorSupport.visitExpressionStatement(CodeVisitorSupport.java:117)\n\tat org.codehaus.groovy.ast.ClassCodeVisitorSupport.visitExpressionStatement(ClassCodeVisitorSupport.java:204)\n\tat org.codehaus.groovy.transform.stc.StaticTypeCheckingVisitor.visitExpressionStatement(StaticTypeCheckingVisitor.java:2188)\n\tat org.codehaus.groovy.ast.stmt.ExpressionStatement.visit(ExpressionStatement.java:41)\n\tat org.codehaus.groovy.ast.CodeVisitorSupport.visitBlockStatement(CodeVisitorSupport.java:86)\n\tat org.codehaus.groovy.ast.ClassCodeVisitorSupport.visitBlockStatement(ClassCodeVisitorSupport.java:168)\n\tat org.codehaus.groovy.transform.stc.StaticTypeCheckingVisitor.visitBlockStatement(StaticTypeCheckingVisitor.java:3895)\n\tat org.codehaus.groovy.ast.stmt.BlockStatement.visit(BlockStatement.java:70)\n\tat org.codehaus.groovy.ast.CodeVisitorSupport.visitBlockStatement(CodeVisitorSupport.java:86)\n\tat org.codehaus.groovy.ast.ClassCodeVisitorSupport.visitBlockStatement(ClassCodeVisitorSupport.java:168)\n\tat org.codehaus.groovy.transform.stc.StaticTypeCheckingVisitor.visitBlockStatement(StaticTypeCheckingVisitor.java:3895)\n\tat org.codehaus.groovy.ast.stmt.BlockStatement.visit(BlockStatement.java:70)\n\tat org.codehaus.groovy.ast.CodeVisitorSupport.visitClosureExpression(CodeVisitorSupport.java:239)\n\tat org.codehaus.groovy.transform.stc.StaticTypeCheckingVisitor.visitClosureExpression(StaticTypeCheckingVisitor.java:2402)\n\tat org.codehaus.groovy.ast.expr.ClosureExpression.visit(ClosureExpression.java:110)\n\tat org.codehaus.groovy.transform.stc.StaticTypeCheckingVisitor.visitCastExpression(StaticTypeCheckingVisitor.java:4074)\n\tat org.codehaus.groovy.ast.expr.CastExpression.visit(CastExpression.java:96)\n\tat org.codehaus.groovy.transform.stc.StaticTypeCheckingVisitor.visitInitialExpression(StaticTypeCheckingVisitor.java:1931)\n\tat org.codehaus.groovy.transform.stc.StaticTypeCheckingVisitor.visitDefaultParameterArguments(StaticTypeCheckingVisitor.java:2616)\n\tat org.codehaus.groovy.transform.stc.StaticTypeCheckingVisitor.visitConstructorOrMethod(StaticTypeCheckingVisitor.java:2588)\n\tat org.codehaus.groovy.ast.ClassCodeVisitorSupport.visitMethod(ClassCodeVisitorSupport.java:110)\n\tat org.codehaus.groovy.transform.stc.StaticTypeCheckingVisitor.startMethodInference(StaticTypeCheckingVisitor.java:2573)\n\tat org.codehaus.groovy.transform.stc.StaticTypeCheckingVisitor.visitMethod(StaticTypeCheckingVisitor.java:2552)\n\tat org.codehaus.groovy.transform.sc.StaticCompilationVisitor.visitConstructorOrMethod(StaticCompilationVisitor.java:236)\n\tat org.codehaus.groovy.transform.sc.StaticCompilationVisitor.visitMethod(StaticCompilationVisitor.java:251)\n\tat org.codehaus.groovy.ast.ClassNode.visitMethods(ClassNode.java:1135)\n\tat org.codehaus.groovy.ast.ClassNode.visitContents(ClassNode.java:1128)\n\tat org.codehaus.groovy.ast.ClassCodeVisitorSupport.visitClass(ClassCodeVisitorSupport.java:52)\n\tat org.codehaus.groovy.transform.stc.StaticTypeCheckingVisitor.visitClass(StaticTypeCheckingVisitor.java:437)\n\tat org.codehaus.groovy.transform.sc.StaticCompilationVisitor.visitClass(StaticCompilationVisitor.java:197)\n\tat org.codehaus.groovy.transform.sc.StaticCompileTransformation.visit(StaticCompileTransformation.java:68)\n\tat org.codehaus.groovy.control.customizers.ASTTransformationCustomizer.call(ASTTransformationCustomizer.groovy:298)\n\tat org.codehaus.groovy.control.CompilationUnit$IPrimaryClassNodeOperation.doPhaseOperation(CompilationUnit.java:900)\n\t... 14 more\n",
    "programs": {
      "/tmp/tmphj006wfu/src/yarn/Main.groovy": true
    }
  }
}
```

The first error is an unexpected compile-time error detected using the
`TypeErasure` mutation. The second is a compiler bug where the compiler accepts
an ill-typed program. Finally, the third one is an internal error of `groovyc`.
When finding a bug, Hephaestus will store the bug-revealing test case inside
the directory of the current testing session (e.g., `bugs/mysession`).

```
|-- 7
|   |-- Main.groovy
|   `-- Main.groovy.bin
|-- 11
|   |-- incorrect.groovy
|   |-- incorrect.groovy.bin
|   |-- Main.groovy
|   `-- Main.groovy.bin
|-- 1050
|   |-- Main.groovy
|   `-- Main.groovy.bin
|-- faults.json
`-- stats.json
```

# Supported Languages

Currently, Hephaestus generates programs written in
three popular programming languages, namely,
Java, Kotlin, and Groovy. You should the
option `--language` to specify the target language.

To support a new language,
you need to implement the following:

* A translator that converts a program written in Hephaestus'
IR into a program written in the target language.
To to so, you have to extend the
[src.translators.base.BaseTranslator](https://github.com/hephaestus-compiler-project/hephaestus/blob/main/src/translators/base.py)
class.

* A class that reads compiler messages and distinguishes
compiler crashes from compiler diagnostic error messages.
To do so, you must extend the 
[src.compilers.base.BaseCompiler](https://github.com/hephaestus-compiler-project/hephaestus/blob/main/src/compilers/base.py)
class.

* (Optionally) Any built-in types supported by the language, e.g., see
[Java types](https://github.com/hephaestus-compiler-project/hephaestus/blob/main/src/ir/java_types.py) for guidance.


# Supported Language Features

Hephaestus generates programs written in an intermediate representation (IR),
a simple object-oriented language that supports parametric polymorphism
and type inference.
Specifically, the programs generated by Hephaestus involve:

* Standard language features (conditionals, method calls, assignments, constants,
  binary operations)

* Standard object-oriented features (inheritance, overriding, class fields, object initialization)

* Parametric polymorphism features (parameterized classes,
  parameterized functions, bounded type parameters, wildcard types,
  declaration-site variance)

* Functional programming features (higher-order functions, lambdas, method references)

* Type inference features (type argument inference, local variable type inference,
  return type inference).


Arithmetic expressions, loops, exceptions,
access modifiers (e.g., `public`, `private`)
are not supported.

# Related publications

* Stefanos Chaliasos, Thodoris Sotiropoulos, Diomidis Spinellis, Arthur Gervais, Benjamin Livshits, and Dimitris Mitropoulos. [Finding Typing Compiler Bugs](https://doi.org/10.1145/3519939.3523427). In Proceedings of the 43rd ACM SIGPLAN Conference on Programming Language Design and Implementation, PLDI '22. ACM, June 2022.
* Stefanos Chaliasos, Thodoris Sotiropoulos, Georgios-Petros Drosos, Charalambos Mitropoulos, Dimitris Mitropoulos, and Diomidis Spinellis. [Well-typed programs can go wrong: A study of typing-related bugs in JVM compilers](https://doi.org/10.1145/3485500). In Proceedings of the ACM on Programming Languages, OOPSLA '21. ACM, October 2021.

# Related Artifacts

* [Replication Package for Article: Finding Typing Compiler Bugs](https://zenodo.org/record/6410434) March 2022 software.
* [Replication Package for Article: "Well-Typed Programs Can Go Wrong: A Study of Typing-Related Bugs in JVM Compilers"](https://doi.org/10.5281/zenodo.5411667) October 2021 software.
