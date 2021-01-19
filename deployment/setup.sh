#! /bin/bash
COMMON_PKGS="vim software-properties-common git tmux cron"
SDKMAN_DEPS="curl unzip zip"
export DEBIAN_FRONTEND=noninteractive

update_and_install_common_pks() {
    apt -yqq update && apt -yqq upgrade
    add-apt-repository ppa:deadsnakes/ppa
    apt -yqq update
    apt install python3.9 python3.9-pip
    apt -yqq install $COMMON_PKGS
}

install_sdkman() {
    apt -yqq install $SDKMAN_DEPS
    curl -s https://get.sdkman.io | /bin/bash
    chmod a+x "$HOME/.sdkman/bin/sdkman-init.sh"
    source "$HOME/.sdkman/bin/sdkman-init.sh"
}

install_deps() {
    update_and_install_common_pks
    install_sdkman
}

install_java() {
    sdk install java 8.0.265-open
}

install_kotlin_from_source() {
    sdk install java 9.0.4-open
    sdk install java 8.0.265-open
    sdk install gradle
    echo "export JAVA_HOME=$HOME/.sdkman/candidates/java/8.0.265-open/" >> $HOME/.bashrc
    echo "export JDK_16=$HOME/.sdkman/candidates/java/8.0.265-open/" >> $HOME/.bashrc
    echo "export JDK_17=$HOME/.sdkman/candidates/java/8.0.265-open/" >> $HOME/.bashrc
    echo "export JDK_18=$HOME/.sdkman/candidates/java/8.0.265-open/" >> $HOME/.bashrc
    echo "export JDK_9=$HOME/.sdkman/candidates/java/9.0.4-open/" >> $HOME/.bashrc
    source $HOME/.bashrc
    git clone https://github.com/JetBrains/kotlin.git
    cd kotlin
    ./gradlew -Dhttp.socketTimeout=60000 -Dhttp.connectionTimeout=60000 dist
    echo "export PATH=\"\$PATH:$HOME/kotlin/dist/bin\"" >> $HOME/.bashrc
    echo "export KOTLIN_INSTALLATION=$HOME/kotlin/dist/bin" >> $HOME/.bashrc
    cd ..
    source $HOME/.bashrc
}

install_kotlin() {
    install_java
    sdk install kotlin
}

install_kotlin_all() {
    install_java
    sdk install kotlin 1.4.21  && \
    sdk install kotlin 1.4.20  && \
    sdk install kotlin 1.4.10  && \
    sdk install kotlin 1.4.0   && \
    sdk install kotlin 1.3.72  && \
    sdk install kotlin 1.3.71  && \
    sdk install kotlin 1.3.70  && \
    sdk install kotlin 1.3.61  && \
    sdk install kotlin 1.3.60  && \
    sdk install kotlin 1.3.50  && \
    sdk install kotlin 1.3.41  && \
    sdk install kotlin 1.3.40  && \
    sdk install kotlin 1.3.31  && \
    sdk install kotlin 1.3.30  && \
    sdk install kotlin 1.3.21  && \
    sdk install kotlin 1.3.20  && \
    sdk install kotlin 1.3.11  && \
    sdk install kotlin 1.3.10  && \
    sdk install kotlin 1.3.0   && \
    sdk install kotlin 1.2.71  && \
    sdk install kotlin 1.2.70  && \
    sdk install kotlin 1.2.61  && \
    sdk install kotlin 1.2.60  && \
    sdk install kotlin 1.2.51  && \
    sdk install kotlin 1.2.50  && \
    sdk install kotlin 1.2.41  && \
    sdk install kotlin 1.2.40  && \
    sdk install kotlin 1.2.31  && \
    sdk install kotlin 1.2.30  && \
    sdk install kotlin 1.2.21  && \
    sdk install kotlin 1.2.20  && \
    sdk install kotlin 1.2.10  && \
    sdk install kotlin 1.2.0   && \
    sdk install kotlin 1.1.61  && \
    sdk install kotlin 1.1.60  && \
    sdk install kotlin 1.1.51  && \
    sdk install kotlin 1.1.50  && \
    sdk install kotlin 1.1.4-3 && \
    sdk install kotlin 1.1.4-2 && \
    sdk install kotlin 1.1.4   && \
    sdk install kotlin 1.1.3-2 && \
    sdk install kotlin 1.1.3   && \
    sdk install kotlin 1.1.2-5 && \
    sdk install kotlin 1.1.2-2 && \
    sdk install kotlin 1.1.2   && \
    sdk install kotlin 1.1.1   && \
    sdk install kotlin 1.1     && \
    sdk install kotlin 1.0.7   && \
    sdk install kotlin 1.0.6   && \
    sdk install kotlin 1.0.5-2 && \
    sdk install kotlin 1.0.5   && \
    sdk install kotlin 1.0.4   && \
    sdk install kotlin 1.0.3   && \
    sdk install kotlin 1.0.2   && \
    sdk install kotlin 1.0.1-2 && \
    sdk install kotlin 1.0.1-1 && \
    sdk install kotlin 1.0.1   && \
    sdk install kotlin 1.0.0
}

install_check_type_systems() {
    git clone git@github.com:theosotr/check-type-system.git
    cd check-type-system
    git fetch && git pull
    git checkout stable
    git pull
    echo "export CHECK_TYPE_SYSTEMS=$(pwd)" >> $HOME/.bashrc
    cd ..
}

add_run_script_to_path() {
    mkdir bin
    cp run.sh bin
    echo "export PATH=\"\$PATH:$HOME/bin\"" >> $HOME/.bashrc
}

if [ $# -eq 0 ]
then
        echo "Missing options!"
        echo "(run $0 -h for help)"
        echo ""
        exit 0
fi

while getopts "hska" OPTION; do
        case $OPTION in

                k)
                        install_deps
                        install_kotlin
                        install_check_type_systems
                        add_run_script_to_path
                        ;;

                s)
                        install_deps
                        install_kotlin_from_source
                        install_check_type_systems
                        add_run_script_to_path
                        ;;

                a)
                        install_deps
                        install_kotlin_all
                        install_check_type_systems
                        add_run_script_to_path
                        ;;

                h)
                        echo "Usage:"
                        echo "init.sh -k "
                        echo "init.sh -s "
                        echo "init.sh -a "
                        echo ""
                        echo "   -k     Install latest kotlin version"
                        echo "   -s     Install kotlin from source"
                        echo "   -a     Install all kotlin versions"
                        echo "   -h     help (this output)"
                        exit 0
                        ;;

        esac
done
