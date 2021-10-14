Perform coverage experiments
============================

Install Java
------------

```
git clone https://github.com/openjdk/jdk.git
cd jdk
bash configure
make jdk
```

Install Kotlin
--------------

```
git clone https://github.com/JetBrains/kotlin.git
# set JAVA_PATHS as in deployment/setup.py script
./gradlew -Dhttp.socketTimeout=60000 -Dhttp.connectionTimeout=60000 clean dist
```

Install Groovy
--------------

```
git clone https://github.com/apache/groovy.git
./gradle -p bootstrap
./gradlew clean dist
```

Install Jacoco
--------------

```
mkdir jacoco
wget https://search.maven.org/remotecontent\?filepath\=org/jacoco/jacoco/0.8.7/jacoco-0.8.7.zip -O jacoco-0.8.7.zip
unzip jacoco-0.8.7.zip
```
