#!/bin/bash

# or we can use: https://adoptopenjdk.gitbooks.io/adoptopenjdk-getting-started-kit/content/en/advanced-steps/openjdk_code_coverage.html
KOTLIN_SRC=$HOME/coverage/kotlin
KOTLIN_JAR=$HOME/.sdkman/candidates/kotlin/1.5.31/lib/kotlin-compiler.jar
JAVA_8=$HOME/.sdkman/candidates/java/8.0.265-open/bin/java
JACOCO=$HOME/coverage/jacoco
PROGRAMS=$1


RES=kotlin-generator
mkdir -p $RES
cd $RES
RES=$(pwd)
cd ..

run_kotlinc () {
    first=$1
    last=$2
    program=program.kt
    #target=$(eval echo "iter_{$first..$last}/program.kt")
    #for t in $target; do
        #echo $t
    for iter in $(seq $first 1 $last); do
        t=iter_$iter/program.kt
        echo $t
        $JAVA_8 \
            -javaagent:$JACOCO/lib/jacocoagent.jar=destfile=$RES/jacoco-$iter.exec \
            -cp $KOTLIN_JAR \
            org.jetbrains.kotlin.cli.jvm.K2JVMCompiler $t
    done
}

cd $PROGRAMS
i=1
for counter in $(seq 30 30 10999); do
    echo $i $counter
    run_kotlinc $i $counter
    i=$counter
done
cd $RES
$JAVA_8 -jar $JACOCO/lib/jacococli.jar merge jacoco-*.exec --destfile jacoco.exec
$JAVA_8 \
    -jar $JACOCO/lib/jacococli.jar report jacoco.exec \
    --classfiles $KOTLIN_JAR \
    --html kotlin-generator
