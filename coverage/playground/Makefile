MAC_BUILD=macosx-x86_64-server-release
LINUX_BUILD=linux-x86_64-server-release
JAVA_BUILD=${MAC_BUILD}
KOTLIN_STD=${HOME}/.sdkman/candidates/kotlin/current/lib/kotlin-stdlib.jar
JAVA_8=${HOME}/.sdkman/candidates/java/8.0.282.j9-adpt/bin/java
JAVA_17=${HOME}/.sdkman/candidates/java/17.ea.27-open/bin/java
JAVA_11=${HOME}/.sdkman/candidates/java/11.0.2-open/bin/java
KOTLIN_SRC=${HOME}/coverage/kotlin
GROOVY_SRC=${HOME}/coverage/groovy
JAVA_SRC=${HOME}/coverage/jdk
JACOCO=${HOME}/coverage/jacoco
JAVAC=$(JAVA_17) -javaagent:$(JACOCO)/lib/jacocoagent.jar=destfile=jacoco.exec \
		-XX:+UseSerialGC -Xms32M -Xmx512M -XX:TieredStopAtLevel=1 \
		-XX:+UnlockDiagnosticVMOptions -XX:-VerifySharedSpaces -Xshare:auto \
		-XX:SharedArchiveFile=$(JAVA_SRC)/build/$(JAVA_BUILD)/configure-support/classes.jsa \
		--limit-modules java.base,jdk.zipfs,java.compiler.interim,jdk.compiler.interim,jdk.javadoc.interim \
		--add-modules java.compiler.interim,jdk.compiler.interim,jdk.javadoc.interim \
		--module-path $(JAVA_SRC)/build/$(JAVA_BUILD)/buildtools/interim_langtools_modules \
		--patch-module java.base=$(JAVA_SRC)/build/$(JAVA_BUILD)/buildtools/gensrc/java.base.interim \
		--add-exports java.base/sun.reflect.annotation=jdk.compiler.interim \
		--add-exports java.base/jdk.internal.jmod=jdk.compiler.interim \
		--add-exports java.base/jdk.internal.misc=jdk.compiler.interim \
		--add-exports java.base/sun.invoke.util=jdk.compiler.interim \
		--add-exports java.base/jdk.internal.javac=java.compiler.interim \
		--add-exports java.base/jdk.internal.javac=jdk.compiler.interim \
		-m jdk.compiler.interim/com.sun.tools.javac.Main
JAVA_REPORT=$(JAVA_17) -jar $(JACOCO)/lib/jacococli.jar report jacoco.exec \
		--classfiles $(JAVA_SRC)/build/$(JAVA_BUILD)/buildtools/interim_langtools_modules/jdk.compiler.interim/com/sun/tools/javac/ \
		--html 

all: java kotlin groovy

java: 
	$(JAVAC) HelloWorld.java 
	$(JAVA_REPORT) java

kotlin:
	 $(JAVA_8) \
		-javaagent:$(JACOCO)/lib/jacocoagent.jar=destfile=jacoco-kt.exec \
		-cp $(KOTLIN_SRC)/dist/kotlinc/lib/kotlin-compiler.jar \
		org.jetbrains.kotlin.cli.jvm.K2JVMCompiler main.kt 
	$(JAVA_8) \
		-jar $(JACOCO)/lib/jacococli.jar report jacoco-kt.exec \
		--classfiles $(KOTLIN_SRC)/dist/kotlinc/lib/kotlin-compiler.jar \
		--html kotlin

kotlin-minimal:
	kotlinc-jvm main.kt -d Main.jar
	java -javaagent:$(JACOCO)/lib/jacocoagent.jar=destfile=jacoco-ktm.exec \
		-classpath Main.jar:$(KOTLIN_STD) \
		MainKt
	java -jar $(JACOCO)/lib/jacococli.jar report jacoco-ktm.exec \
		--classfiles main.jar --html kotlin-minimal

groovy:
	java -javaagent:$(JACOCO)/lib/jacocoagent.jar=destfile=jacoco-groovy.exec \
		-cp $(GROOVY_SRC)/build/libs/groovy-4.0.0-SNAPSHOT.jar \
		org.codehaus.groovy.tools.FileSystemCompiler Main.groovy
	java -jar $(JACOCO)/lib/jacococli.jar report jacoco-groovy.exec \
		--classfiles $(GROOVY_SRC)/build/libs/groovy-4.0.0-SNAPSHOT.jar \
		--html groovy

clean:
	rm -rf HelloWorld.class java jacoco.exec jacoco-kt.exec META-INF Main.jar \
		MainKt.class kotlin Main.class jacoco-groovy.exec groovy \
		jacoco-ktm.exec kotlin-minimal javac-test-suite
