#!/usr/bin/env bash
TIME_TO_RUN=$((23 * 60 * 60))
HOUR=$((60 * 60))
CORES=$(cat /proc/cpuinfo | grep processor | wc -l)
CORES=$(($CORES - 2))
TRANSFORMATIONS=1
VERSIONS="1.4.21 1.4.20 1.4.10 1.4.0 1.3.72 1.3.71 1.3.70 1.3.61 1.3.60 1.3.50 1.3.41 1.3.40 1.3.31 1.3.30 1.3.21 1.3.20 1.3.11 1.3.10 1.3.0 1.2.71 1.2.70 1.2.61 1.2.60 1.2.51 1.2.50 1.2.41 1.2.40 1.2.31 1.2.30 1.2.21 1.2.20 1.2.10 1.2.0 1.1.61 1.1.60 1.1.51 1.1.50 1.1.4-3 1.1.4-2 1.1.4 1.1.3-2 1.1.3 1.1.2-5 1.1.2-2 1.1.2 1.1.1 1.1 1.0.7 1.0.6 1.0.5-2 1.0.5 1.0.4 1.0.3 1.0.2 1.0.1-2 1.0.1-1 1.0.1 1.0.0"
source /root/.bashrc
source /root/.bash_profile


simple_run_groovy() {
    source "$HOME/.sdkman/bin/sdkman-init.sh"
    # sdk install groovy
    cd $CHECK_TYPE_SYSTEMS
    git pull
    python3 hephaestus.py -s $TIME_TO_RUN -t $TRANSFORMATIONS -w $CORES --batch 30 -P \
        --language groovy --cast-numbers
}

simple_run() {
    source "$HOME/.sdkman/bin/sdkman-init.sh"
    sdk install kotlin
    cd $CHECK_TYPE_SYSTEMS
    git pull
    python3 hephaestus.py -s $TIME_TO_RUN -t $TRANSFORMATIONS -w $CORES --batch 30 -P
}

run_from_source() {
    cd $KOTLIN_INSTALLATION
    git pull
    ./gradlew clean
    ./gradlew -Dhttp.socketTimeout=60000 -Dhttp.connectionTimeout=60000 dist
    cd $CHECK_TYPE_SYSTEMS
    git pull
    python3 hephaestus.py -s $TIME_TO_RUN -t $TRANSFORMATIONS -w $CORES --batch 30 -P
}

run_groovy_from_source() {
    source "$HOME/.sdkman/bin/sdkman-init.sh"
    cd $GROOVY_INSTALLATION
    git pull
    ./gradlew clean dist --continue
    cd $CHECK_TYPE_SYSTEMS
    git pull
    python3 hephaestus.py -s $TIME_TO_RUN -t $TRANSFORMATIONS -w $CORES --batch 30 -P \
        --language groovy --cast-numbers
}

run_multiple_versions() {
    cd $CHECK_TYPE_SYSTEMS
    git pull
    source "$HOME/.sdkman/bin/sdkman-init.sh"
    for i in {1..22}; do
        length=$(echo "$VERSIONS" | wc -w)
        rnum=$((1 + $RANDOM%$length+1));
        version=$(echo $VERSIONS | cut -d " " -f $rnum)
        sdk use kotlin $version
        python3 hephaestus.py -s $HOUR -t $TRANSFORMATIONS -w $CORES --batch 30 -P
    done
}

if [ $# -eq 0 ]
then
        echo "Missing options!"
        echo "(run $0 -h for help)"
        echo ""
        exit 0
fi

while getopts "hksagS" OPTION; do
        case $OPTION in

                k)
                        simple_run
                        ;;

                s)
                        run_from_source
                        ;;

                a)
                        run_multiple_versions
                        ;;

                g)
                        simple_run_groovy
                        ;;

                S)
                        run_groovy_from_source
                        ;;

                h)
                        echo "Usage:"
                        echo "init.sh -k "
                        echo "init.sh -s "
                        echo "init.sh -a "
                        echo "init.sh -g "
                        echo "init.sh -S "
                        echo ""
                        echo "   -k     Simple run"
                        echo "   -s     Run from source"
                        echo "   -a     Run multiple versions"
                        echo "   -g     Simple run groovy"
                        echo "   -S     Run groovy from source"
                        echo "   -h     help (this output)"
                        exit 0
                        ;;

        esac
done
