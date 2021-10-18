#!/bin/bash

# or we can use: https://adoptopenjdk.gitbooks.io/adoptopenjdk-getting-started-kit/content/en/advanced-steps/openjdk_code_coverage.html
KOTLIN_SRC=$HOME/coverage/kotlin
KOTLIN_JAR=$HOME/.sdkman/candidates/kotlin/1.5.31/lib/kotlin-compiler.jar
JAVA_8=$HOME/.sdkman/candidates/java/8.0.265-open/bin/java
JACOCO=$HOME/coverage/jacoco
KOTLINC_TEST=$(find $KOTLIN_SRC/compiler $(find $KOTLIN_SRC -not -path "./tests-spec/*" -type d -name "testData") -name "*.kt" -exec grep -Li '<!' {} \;)

TEST_SUITE_RES=kotlin-test-suite
mkdir -p $TEST_SUITE_RES
cd $TEST_SUITE_RES
TEST_SUITE_RES=$(pwd)
cd ..

run_kotlinc () {
    work_dir=$(pwd)
    iter=$1
    dir=$(dirname $2)
    program=$(basename $2)
    echo $dir
    echo $program
    cd $dir
	$JAVA_8 \
    	-javaagent:$JACOCO/lib/jacocoagent.jar=destfile=$TEST_SUITE_RES/jacoco-$iter.exec \
		-cp $KOTLIN_JAR \
		org.jetbrains.kotlin.cli.jvm.K2JVMCompiler $program
    cd $work_dir
}

counter=0
for program in $KOTLINC_TEST; do
    counter=$((counter+1))
    run_kotlinc $counter $program
done
cd $TEST_SUITE_RES
$JAVA_8 -jar $JACOCO/lib/jacococli.jar merge jacoco-*.exec --destfile jacoco.exec
$JAVA_8 \
    -jar $JACOCO/lib/jacococli.jar report jacoco-kt.exec \
    --classfiles $KOTLIN_JAR \
    --html kotlin
