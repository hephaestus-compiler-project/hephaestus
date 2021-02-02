#! /bin/bash
#
# Find which transformation introduce the error
#

if [ $# -ne 2 ]; then
    echo $0: usage: replay.sh bugs/name iteration_number
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
FAULTS=$NAME/faults.json
TRANSFORMATIONS=$NAME/transformations/iter_$ITER
TRANSFORMATION="Generation"
LAST_I=$(ls bugs/eaknW/transformations/iter_15/ | sort -nr | head -1)
LAST_TRANS=$(cat $FAULTS | jq --arg ITER "$ITER" --argjson I "$LAST_I" \
    '.[$ITER]["transformations"][$I]')

check() {
   bin=$1
   if python3 main.py -i 1 -t 0 -R $bin -d -b replay_tmp | grep -q "faults: 1"; then
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
    bin=$TRANSFORMATIONS/$i/program.kt.bin
    if check $bin; then
        echo "$LAST_I: $LAST_TRANS"
        echo "You can use the following command to try to reproduce the bug"
        echo "python3 main.py -i 1 -t 1 -T $LAST_TRANS -R $bin -d"
        rm -rf replay_tmp
        exit
    fi
    LAST_I=$i
    LAST_TRANS=$TRANSFORMATION
done
