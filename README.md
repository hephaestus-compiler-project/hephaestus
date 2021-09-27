check-type-system
=================

Reported Bugs
-------------

#### Kotlin

* <https://youtrack.jetbrains.com/issues?q=%23theosotr%20%23stefanoshaliassos%20>

#### Groovy

* <https://issues.apache.org/jira/browse/GROOVY-9945?filter=-2&jql=reporter%20%3D%20%22Thodoris%20Sotiropoulos%22%20OR%20reporter%20%3D%20schaliasos>

#### Java

* <https://github.com/theosotr/check-type-system/issues/37>

Installation
------------

You must have installed Java.
In Debian/Ubuntu, you can install it
by running the following command.

```
sudo apt install default-jdk default-jre
```

#### Install sdkman

To install all targeted languages you can use sdkman.

```
curl -s "https://get.sdkman.io" | bash
source "$HOME/.sdkman/bin/sdkman-init.sh"
```

#### Install Kotlin

```
sdk install kotlin
```

#### Install Groovy

```
sdk install groovy
```

Run
---

To execute the tests run:

```
python setup.py test
```

To get a help message about options run:

```
python main.py -h
```

To run `check-types` for 10 iterations and 20 transformations,
 with 4 cores, and to only compile the last program run:

```
python main.py -i 10 -t 20 -w 4 -l
```

Command line linters
--------------------

* kotlin

```
wget -P /usr/local/bin/ "https://github.com/pinterest/ktlint/releases/download/0.39.0/ktlint" && chmod a+x /usr/local/bin/ktlint

ktlint --format program.kt
```

* GRoovy

```
npm install -g npm-groovy-lint

npm-groovy-lint --format Main.groovy
```
