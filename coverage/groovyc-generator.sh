#!/bin/bash
GROOVY_SRC=${HOME}/coverage/groovy
JAVA_11=${HOME}/.sdkman/candidates/java/11.0.2-open/bin/java
JACOCO=$HOME/coverage/jacoco
PROGRAMS=$1


RES=groovy-generator
mkdir -p $RES
cd $RES
RES=$(pwd)
cd ..

run_groovyc () {
    first=$1
    last=$2
    #target=$(eval echo "iter_{$first..$last}/Main.groovy")
    #for t in $target; do
        #echo $t
    for iter in $(seq $first 1 $last); do
        t=iter_$iter/Main.groovy
        echo $t
        $JAVA_11 -javaagent:$JACOCO/lib/jacocoagent.jar=destfile=$RES/jacoco-$iter.exec \
            -cp $GROOVY_SRC/build/libs/groovy-4.0.0-SNAPSHOT.jar \
            org.codehaus.groovy.tools.FileSystemCompiler $t
    done
}

i=1
cd $PROGRAMS
for counter in $(seq 30 30 10998); do
    echo $i $counter
    run_groovyc $i $counter
    i=$counter
done
cd $RES
$JAVA_11 -jar $JACOCO/lib/jacococli.jar merge jacoco-*.exec --destfile jacoco.exec
$JAVA_11 -jar $JACOCO/lib/jacococli.jar report jacoco.exec \
    --classfiles $GROOVY_SRC/build/libs/groovy-4.0.0-SNAPSHOT.jar \
    --html groovy-generator
