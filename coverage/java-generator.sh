#!/bin/bash

# or we can use: https://adoptopenjdk.gitbooks.io/adoptopenjdk-getting-started-kit/content/en/advanced-steps/openjdk_code_coverage.html
MAC_BUILD=macosx-x86_64-server-release
LINUX_BUILD=linux-x86_64-server-release
JAVA_BUILD=$LINUX_BUILD
JAVA_17=$HOME/.sdkman/candidates/java/17-open/bin/java
JAVA_SRC=$HOME/coverage/jdk
JACOCO=$HOME/coverage/jacoco
PROGRAMS=$1
MUTANTS=$2


RES=java-generator
mkdir -p $RES
cd $RES
RES=$(pwd)
cd ..

RES_INF=java-generator-inference
if [ ! -z "$MUTANTS" ]; then
    mkdir -p $RES_INF
    cd $RES_INF
    RES_INF=$(pwd)
    cd ..
fi

run_javac () {
    first=$1
    last=$2
    res=$3
    p=$4
    #target=$(eval echo "iter_{$first..$last}/Main.java")
    #for t in $target; do
        #echo $t
    for iter in $(seq $first 1 $last); do
        t=iter_$iter/$p/Main.java
        echo $t
        $JAVA_17 -javaagent:$JACOCO/lib/jacocoagent.jar=destfile=$res/jacoco-$iter.exec \
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
            -m jdk.compiler.interim/com.sun.tools.javac.Main -nowarn $t
    done
}

i=1
cd $PROGRAMS
for counter in $(seq 30 30 499); do
    echo $i $counter
    run_javac $i $counter $RES
    i=$counter
done

if [ ! -z "$MUTANTS" ]; then
    cd $MUTANTS
    for counter in $(seq 30 30 499); do
        echo $i $counter
        run_javac $i $counter $RES_INF 0
        i=$counter
    done
    cd $RES_INF
    $JAVA_17 -jar $JACOCO/lib/jacococli.jar merge jacoco-*.exec --destfile jacoco.exec
    $JAVA_17 -jar $JACOCO/lib/jacococli.jar report jacoco.exec \
        --classfiles $JAVA_SRC/build/$JAVA_BUILD/buildtools/interim_langtools_modules/jdk.compiler.interim/com/sun/tools/javac/ \
        --html javac-generator-inf
fi

cd $RES
$JAVA_17 -jar $JACOCO/lib/jacococli.jar merge jacoco-*.exec --destfile jacoco.exec
$JAVA_17 -jar $JACOCO/lib/jacococli.jar report jacoco.exec \
	--classfiles $JAVA_SRC/build/$JAVA_BUILD/buildtools/interim_langtools_modules/jdk.compiler.interim/com/sun/tools/javac/ \
	--html javac-generator
