KOTLIN_STD=~/.sdkman/candidates/kotlin/current/lib/kotlin-stdlib.jar
JAVA_8=~/.sdkman/candidates/java/8.0.282.j9-adpt/bin/java
KOTLIN_SRC=~/coverage/kotlin
GROOVY_SRC=~/coverage/groovy

all: java kotlin

java:
	javac HelloWorld.java
	java -javaagent:../jacoco/lib/jacocoagent.jar HelloWorld
	java -jar ../jacoco/lib/jacococli.jar report jacoco.exec --classfiles HelloWorld.class --html java

kotlin:
	 $(JAVA_8) \
		-javaagent:../jacoco/lib/jacocoagent.jar=destfile=jacoco-kt.exec \
		-cp $(KOTLIN_SRC)/dist/kotlinc/lib/kotlin-preloader.jar \
		org.jetbrains.kotlin.preloading.Preloader \
		-cp $(KOTLIN_SRC)/kotlin/dist/kotlinc/lib/kotlin-compiler.jar \
		org.jetbrains.kotlin.cli.jvm.K2JVMCompiler main.kt
	$(JAVA_8) \
		-jar ../jacoco/lib/jacococli.jar report jacoco-kt.exec \
		--classfiles $(KOTLIN_SRC)/dist/kotlinc/lib/kotlin-compiler.jar \
		--html kotlin

kotlin-minimal:
	kotlinc-jvm main.kt -d Main.jar
	java -javaagent:../jacoco/lib/jacocoagent.jar=destfile=jacoco-ktm.exec \
		-classpath Main.jar:$(KOTLIN_STD) \
		MainKt
	java -jar ../jacoco/lib/jacococli.jar report jacoco-ktm.exec \
		--classfiles main.jar --html kotlin-minimal

groovy:
	java -javaagent:../jacoco/lib/jacocoagent.jar=destfile=jacoco-groovy.exec \
		-cp $(GROOVY_SRC)/build/libs/groovy-4.0.0-SNAPSHOT.jar \
		org.codehaus.groovy.tools.FileSystemCompiler Main.groovy
	java -jar ../jacoco/lib/jacococli.jar report jacoco-groovy.exec \
		--classfiles $(GROOVY_SRC)/build/libs/groovy-4.0.0-SNAPSHOT.jar \
		--html groovy

clean:
	rm -rf HelloWorld.class java jacoco.exec jacoco-kt.exec META-INF Main.jar \
		MainKt.class kotlin Main.class jacoco-groovy.exec groovy \
		jacoco-ktm.exec kotlin-minimal
