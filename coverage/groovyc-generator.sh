#!/bin/bash
GROOVY_SRC=${HOME}/coverage/groovy
JAVA_11=${HOME}/.sdkman/candidates/java/11.0.2-open/bin/java
JACOCO=$HOME/coverage/jacoco
PROGRAMS=$1
MUTANTS=$2

RES=groovy-generator
mkdir -p $RES
cd $RES
RES=$(pwd)
cd ..

RES_INF=groovy-generator-inference
if [ ! -z "$MUTANTS" ]; then
    mkdir -p $RES_INF
    cd $RES_INF
    RES_INF=$(pwd)
    cd ..
fi

run_groovyc () {
    first=$1
    last=$2
    res=$3
    p=$4
    #target=$(eval echo "iter_{$first..$last}/Main.groovy")
    #for t in $target; do
        #echo $t
    for iter in $(seq $first 1 $last); do
        t=iter_$iter/$p/Main.groovy
        echo $t
        $JAVA_11 -javaagent:$JACOCO/lib/jacocoagent.jar=destfile=$res/jacoco-$iter.exec \
            -cp $GROOVY_SRC/build/libs/groovy-4.0.0-SNAPSHOT.jar \
            org.codehaus.groovy.tools.FileSystemCompiler --compile-static $t
    done
}

i=1
cd $PROGRAMS
for counter in $(seq 30 30 499); do
    echo $i $counter
    run_groovyc $i $counter $RES
    i=$counter
done
if [ ! -z "$MUTANTS" ]; then
    cd $MUTANTS
    for counter in $(seq 30 30 499); do
        echo $i $counter
        run_groovyc $i $counter $RES_INF 0
        i=$counter
    done
    cd $RES_INF
    $JAVA_11 -jar $JACOCO/lib/jacococli.jar merge jacoco-*.exec --destfile jacoco.exec
    $JAVA_11 -jar $JACOCO/lib/jacococli.jar report jacoco.exec \
        --classfiles $GROOVY_SRC/build/libs/groovy-4.0.0-SNAPSHOT.jar \
        --html groovy-generator-inf
fi
cd $RES
$JAVA_11 -jar $JACOCO/lib/jacococli.jar merge jacoco-*.exec --destfile jacoco.exec
$JAVA_11 -jar $JACOCO/lib/jacococli.jar report jacoco.exec \
    --classfiles $GROOVY_SRC/build/libs/groovy-4.0.0-SNAPSHOT.jar \
    --html groovy-generator
