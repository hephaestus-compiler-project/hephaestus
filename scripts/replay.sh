#! /bin/bash
#
# Find which transformation introduce the error
#

if [ $# -ne 3 ]; then
    echo $0: usage: replay.sh bugs/name iteration_number language
    exit 1
fi
if ! command -v jq &> /dev/null
then
    echo "jq could not be found"
    exit
fi
if [ ! -f "main.py" ]; then
    echo "main.py not found!"
    exit
fi
if [ -d "replay_tmp" ]; then
    echo "replay_tmp already exists"
    exit
fi

NAME=$1
ITER=$2
LANGUAGE=$3
FAULTS=$NAME/faults.json
TRANSFORMATIONS=$NAME/transformations/iter_$ITER
TRANSFORMATION="Generation"
LAST_I=$(ls $TRANSFORMATIONS | sort -nr | head -1)
LAST_TRANS=$(cat $FAULTS | jq --arg ITER "$ITER" --argjson I "$LAST_I" \
    '.[$ITER]["transformations"][$I]')

case "$LANGUAGE" in
    "kotlin")
        PROGRAM="program.kt.bin"
        ;;

    "groovy")
        PROGRAM="Main.groovy.bin"
        ;;

    "java")
        PROGRAM="Main.java.bin"
        ;;

    *)
        echo "language should be groovy, kotlin or Java"
        exit
        ;;
esac

check() {
   bin=$1
   if python3 main.py -i 1 -t 0 -R $bin -d -b replay_tmp --language $LANGUAGE | grep -q "faults: 1"; then
       return 1
   else
       return 0
   fi
}

for i in $(ls $TRANSFORMATIONS | sort -nr); do
    echo "Iteration number: $i"
    TRANSFORMATION=$(cat $FAULTS | jq \
        --arg ITER "$ITER" --argjson I "$i" \
        '.[$ITER]["transformations"][$I]')
    bin=$TRANSFORMATIONS/$i/$PROGRAM
    if check $bin; then
        echo "$LAST_I: $LAST_TRANS"
        echo "You can use the following command to try to reproduce the bug"
        echo "python3 main.py -i 1 -t 1 -T $LAST_TRANS -R $bin -d --language $LANGUAGE"
        rm -rf replay_tmp
        exit
    fi
    LAST_I=$i
    LAST_TRANS=$TRANSFORMATION
done
