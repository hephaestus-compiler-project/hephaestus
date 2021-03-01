#! /bin/bash
ITERATIONS=$1
DIR=$2

if [ "$#" -ne 2 ]; then
    echo "usage: analyze-fixes.sh FILE OUTPUT_DIR"
fi
echo "Read from $ITERATIONS save to $DIR"
mkdir -p $DIR

for iter in $(ls -d $ITERATIONS/*/); do
    for f in $(ls $iter); do
        number=$(echo $iter | sed "s/.*iterations\///")
        lang=${f%.txt}
        dest=$DIR/$number$lang
        mkdir -p $dest
        COUNTER=1
        echo "Process: $iter/$f"
        for l in $(cat $iter/$f); do
            urls=(${l//,/ })
            fix=${urls[1]}
            if [[ "$fix" == *"pull"* ]]; then
                gh pr diff $fix | diffstat -t > $dest/$COUNTER.csv
            else
                if [[ "$fix" == *"groovy"* ]]; then
                    cd groovy
                elif [[ "$fix" == *"kotlin"* ]]; then
                    cd kotlin
                elif [[ "$fix" == *"dotty"* ]]; then
                    cd dotty
                elif [[ "$fix" == *"scala"* ]]; then
                    cd scala
                elif [[ "$fix" == *"openjdk/valhalla"* ]]; then
                    cd valhalla
                elif [[ "$fix" == *"openjdk/jdk16"* ]]; then
                    cd jdk16
                elif [[ "$fix" == *"openjdk/jdk"* ]]; then
                    cd jdk
                else
                    if [[ "$fix" == *"hg.openjdk.java.net"* ]]; then
                        fix_url=${fix/rev/raw-rev}
                        wget -O - $fix_url 2> /dev/null | diffstat -t \
                            > $dest/$COUNTER.csv
                    else
                        echo "Cannot find repo: $fix"
                    fi
                    COUNTER=$[$COUNTER +1]
                    continue
                fi
                commit=${fix##*/}
                git diff $commit^! | diffstat -t > ../$dest/$COUNTER.csv
                cd ../
            fi
            COUNTER=$[$COUNTER +1]
        done
    done
done

exit

