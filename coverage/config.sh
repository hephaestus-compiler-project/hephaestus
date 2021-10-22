#!/bin/bash
MAC_BUILD=macosx-x86_64-server-release
LINUX_BUILD=linux-x86_64-server-release
JAVA_17_LINUX=$HOME/.sdkman/candidates/java/17-open/bin/java
JAVA_17_MAC=${HOME}/.sdkman/candidates/java/17.ea.27-open/bin/java
JAVA_8_LINUX=${HOME}/.sdkman/candidates/java/8.0.265-open/bin/java
JAVA_8_MAC=${HOME}/.sdkman/candidates/java/8.0.282.j9-adpt/bin/java
JAVA_11=${HOME}/.sdkman/candidates/java/11.0.2-open/bin/java
JAVA_SRC=$HOME/coverage/jdk
KOTLIN_JAR=$HOME/.sdkman/candidates/kotlin/1.5.31/lib/kotlin-compiler.jar
JACOCO=$HOME/coverage/jacoco

distro=$1

if [ "$distro" = "Linux" ]; then
    JAVA_BUILD=$LINUX_BUILD
    JAVA_17=$JAVA_17_LINUX
    JAVA_8=$JAVA_8_LINUX
else
    JAVA_BUILD=$MAC_BUILD
    JAVA_17=$JAVA_17_MAC
    JAVA_8=$JAVA_8_MAC
fi

JAVA_CLASSES=$JAVA_SRC/build/$JAVA_BUILD/buildtools/interim_langtools_modules/jdk.compiler.interim/com/sun/tools/javac/
