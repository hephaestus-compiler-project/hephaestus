check-type-system
=================

Installation
------------

You must have installed Java.
In Debian/Ubuntu, you can install it 
by running the following command.

```
sudo apt install default-jdk default-jre
```

#### Install Kotlin

To install kotlin you can use sdkman.

```
curl -s "https://get.sdkman.io" | bash
source "$HOME/.sdkman/bin/sdkman-init.sh"
sdk install kotlin
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
