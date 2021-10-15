#!/bin/bash

# or we can use: https://adoptopenjdk.gitbooks.io/adoptopenjdk-getting-started-kit/content/en/advanced-steps/openjdk_code_coverage.html
MAC_BUILD=macosx-x86_64-server-release
LINUX_BUILD=linux-x86_64-server-release
JAVA_BUILD=$MAC_BUILD
JAVA_17=$HOME/.sdkman/candidates/java/17.ea.27-open/bin/java
JAVA_SRC=$HOME/coverage/jdk
JACOCO=$HOME/coverage/jacoco
JAVAC_TEST=$(find $JAVA_SRC/test/langtools/tools/javac -type f -name "*.java")

TEST_SUITE_RES=jacoco-test-suite
mkdir -p $TEST_SUITE_RES
cd $TEST_SUITE_RES
TEST_SUITE_RES=$(pwd)
cd ..

run_javac () {
    work_dir=$(pwd)
    iter=$1
    dir=$(dirname $2)
    program=$(basename $2)
    cd $dir
    $JAVA_17 -javaagent:$JACOCO/lib/jacocoagent.jar=destfile=$TEST_SUITE_RES/jacoco-$iter.exec \
		-XX:+UseSerialGC -Xms32M -Xmx512M -XX:TieredStopAtLevel=1 \
		-XX:+UnlockDiagnosticVMOptions -XX:-VerifySharedSpaces -Xshare:auto \
		-XX:SharedArchiveFile=$JAVA_SRC/build/$JAVA_BUILD/configure-support/classes.jsa \
		--limit-modules java.base,jdk.zipfs,java.compiler.interim,jdk.compiler.interim,jdk.javadoc.interim \
		--add-modules java.compiler.interim,jdk.compiler.interim,jdk.javadoc.interim \
		--module-path $JAVA_SRC/build/$JAVA_BUILD/buildtools/interim_langtools_modules \
		--patch-module java.base=$JAVA_SRC/build/$JAVA_BUILD/buildtools/gensrc/java.base.interim \
		--add-exports java.base/sun.reflect.annotation=jdk.compiler.interim \
		--add-exports java.base/jdk.internal.jmod=jdk.compiler.interim \
		--add-exports java.base/jdk.internal.misc=jdk.compiler.interim \
		--add-exports java.base/sun.invoke.util=jdk.compiler.interim \
		--add-exports java.base/jdk.internal.javac=java.compiler.interim \
		--add-exports java.base/jdk.internal.javac=jdk.compiler.interim \
		-m jdk.compiler.interim/com.sun.tools.javac.Main $program
    cd $work_dir
}

counter=0
for program in $JAVAC_TEST; do
    counter=$((counter+1))
    run_javac $counter $program
done
cd $TEST_SUITE_RES
$JAVA_17 -jar $JACOCO/lib/jacococli.jar merge jacoco-*.exec --destfile jacoco.exec
$JAVA_17 -jar $JACOCO/lib/jacococli.jar report jacoco.exec \
	--classfiles $JAVA_SRC/build/$JAVA_BUILD/buildtools/interim_langtools_modules/jdk.compiler.interim/com/sun/tools/javac/ \
	--html javac-test-suite
