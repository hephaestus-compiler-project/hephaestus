#!/bin/bash
GROOVY_SRC=${HOME}/coverage/groovy
JAVA_11=${HOME}/.sdkman/candidates/java/11.0.2-open/bin/java
JACOCO=$HOME/coverage/jacoco
STC=$GROOVY_SRC/src/test/groovy/transform/stc

template='''
abstract class BBASEE { \n
    def counter = 0 \n

    protected void process(String code) { \n
        String path = this.class.getSimpleName() \n

        File directory = new File(path); \n
        if (! directory.exists()){ \n
            directory.mkdir(); \n
        } \n

        File file = new File(path + "/Test" + this.counter + ".groovy"); \n
        try{ \n
            FileWriter fw = new FileWriter(file.getAbsoluteFile()); \n
            BufferedWriter bw = new BufferedWriter(fw); \n
            bw.write(code); \n
            bw.close(); \n
        }
        catch (IOException e){ \n
            e.printStackTrace(); \n
            System.exit(-1); \n
        } \n
    } \n
    protected void assertScript(String script) { \n
        process(script) \n
    } \n

    protected void assertScript(String script, Long x) { \n
        process(script) \n
    } \n

    protected void shouldCompile(String script) { \n
        process(script) \n
    } \n

    protected void shouldFail(String script) { \n
        process(script) \n
    } \n

    protected Class assertClass(String classCode) { \n
        process(classCode) \n
    } \n

    protected void shouldFailWithMessages(String code, String... messages) { \n
        process(code) \n
    } \n

    static void main(String[] args) { \n
        def obj = new CCLASSS() \n
        def name = "CCLASSS" \n
        def methods = CCLASSS.declaredMethods.findAll { \n
            !it.synthetic && !it.getAnnotation(groovy.transform.Internal) \n
        }.name \n

        for(m in methods){ \n
            obj.counter += 1 \n
            obj."$m"() \n
        } \n
    } \n
} \n
'''

TEST_SUITE_RES=groovyc-test-suite
mkdir -p $TEST_SUITE_RES
cd $TEST_SUITE_RES
TEST_SUITE_RES=$(pwd)
cd ..

instrument_file() {
    f=$1
    filename=$2
    keyword=$3
    code=$(sed "s/CCLASSS/$filename/" <<< "$template")
    code=$(sed "s/BBASEE/$keyword/" <<< "$code")
    sed -i "/import.*StaticTypeCheckingTestCase/d" $f
    sed -i "/import.*CompilableTestSupport/d" $f
    sed -i "/import.*GroovyTestCase/d" $f
    sed -i "/def constructor = fooClass.getDeclaredConstructor()/d" $f
    sed -i "/assert constructor.declaredAnnotations.size() == 0/d" $f
    sed -i "/import.*groovy.test.NotYetImplemented/d" $f
    sed -i "/import.*groovy.transform.CompileStatic/d" $f
    sed -i "/import.*doInFork/d" $f
    sed -i "/import.*org.codehaus.groovy.control.CompilerConfiguration/d" $f
    sed -i "/import.*org.codehaus.groovy.control.customizers.ImportCustomizer/d" $f
    sed -i "/import.*org.junit.Test/d" $f
    sed -i "/import.*assertScript/d" $f
    sed -i "/import.*shouldFail/d" $f
    sed -i "s/assertScript shell,/assertScript /" $f
    sed -i "s/shouldFail shell,/shouldFail /" $f
    sed -i "s/shouldFail GroovyCastException,/shouldFail /" $f
    sed -i "s/shouldFail NotSerializableException,/shouldFail /" $f
    sed -i "s/shouldFail MissingMethodException,/shouldFail /" $f
    sed -i "s/shouldFail UnsupportedOperationException,/shouldFail /" $f
    sed -i "s/doInFork .*,/assertScript /" $f
    sed -i "/\@Test/d" $f
    sed -i "/\@NotYetImplemented/d" $f
    sed -i "/\@CompileStatic/d" $f
    echo -e $code >> $f
}


directory=$STC
cd $directory
git checkout *.groovy
keywords="StaticTypeCheckingTestCase CompilableTestSupport GroovyTestCase"
for i in $(ls $directory/*.groovy); do
    echo $i
    flag=false
    filename=$(basename -- "$i")
    filename="${filename%.*}"
    dir=$(dirname $i)
    if [ "$filename" = "CustomErrorCollectorSTCTest" ]; then
        continue
    fi
    for keyword in $keywords; do
        if grep -q $keyword $i; then
            flag=true
            instrument_file $i $filename $keyword
            if [ "$filename" = "GenericsSTCTest" ]; then
                sed -i '993,1037d;1585,1628d;2348,2393d;2696,2758d;3321,3350d;3532,3564d;3600,3634d' $i
                mkdir -p $dir/$filename
                cp $i $dir/$filename
            fi
            if [ "$filename" = "MethodCallsSTCTest" ]; then
                sed -i '28,35d' $i
            fi
            if [ "$filename" = "STCwithTransformationsTest" ]; then
                sed -i '37,46d;71,79d' $i
            fi
            if [ "$filename" = "TypeCheckingExtensionsTest" ]; then
                sed -i '29,38d;61d;65d;67d;462,467d' $i
                sed -i '28i    def extension' $i
            fi
            if [ "$filename" = "TypeInferenceSTCTest" ]; then
                sed -i '649,656d;664,668d;677,678d;686,687d;696d;1023,1076d' $i
            fi
            if [ "$filename" = "MethodCallsSTCTest" ]; then
                sed -i '322d;331d' $i
            fi
            groovy $i
            break
        fi
    done
    if [ "$filename" = "LambdaTest" ] || [ "$filename" = "MethodReferenceTest" ]; then
        sed -i "/assert err.*/d" $i
        sed -i "s/final class LambdaTest {/class LambdaTest extends StaticTypeCheckingTestCase {/" $i
        sed -i "s/final class MethodReferenceTest {/class MethodReferenceTest extends StaticTypeCheckingTestCase {/" $i
        sed -i '/private final GroovyShell shell/,+3d' $i
        instrument_file $i $filename "StaticTypeCheckingTestCase"
        groovy $i
        flag=true
    fi
    if [ "$flag" = false ]; then
        mkdir -p $dir/$filename
        cp $i $dir/$filename
    fi
done

TEST_SUITE_PROGRAMS=$(ls $STC/*/*.groovy)

run_groovyc () {
    iter=$1
    dir=$(dirname $2)
    program=$(basename $2)
    cd $dir
	$JAVA_11 -javaagent:$JACOCO/lib/jacocoagent.jar=destfile=$TEST_SUITE_RES/jacoco-$iter.exec \
		-cp $GROOVY_SRC/build/libs/groovy-4.0.0-SNAPSHOT.jar \
		org.codehaus.groovy.tools.FileSystemCompiler $program
}

counter=0
for program in $TEST_SUITE_PROGRAMS; do
    counter=$((counter+1))
    run_groovyc $counter $program
done

cd $TEST_SUITE_RES

$JAVA_11 -jar $JACOCO/lib/jacococli.jar merge jacoco-*.exec --destfile jacoco.exec
$JAVA_11 -jar $JACOCO/lib/jacococli.jar report jacoco.exec \
    --classfiles $GROOVY_SRC/build/libs/groovy-4.0.0-SNAPSHOT.jar \
    --html groovy
