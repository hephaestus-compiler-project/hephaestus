#! /bin/bash
#
# Combine the results of two Jacoco coverage files (.exec)
#

if [ $# -ne 5 ]; then
    echo $0: usage: combine.sh language jacoco_exec_1 jacoco_exec_2 output_dir output_name
    exit 1
fi

language=$1
jacoco_1=$2
jacoco_2=$3
output_dir=$4
output_name=$5

unameOut="$(uname -s)"
case "${unameOut}" in
    Linux*)     distro=Linux;;
    Darwin*)    distro=Mac;;
    *)          echo "$unameOut: is not supported" && exit 1
esac

. config.sh $distro

if [ "$language" = "java" ]; then
    SOURCES=$JAVA_CLASSES
    JAVA=$JAVA_17
elif [ "$language" = "kotlin" ]; then
    SOURCES=$KOTLIN_JAR
    JAVA=$JAVA_8
elif [ "$language" = "groovy" ]; then
    JAVA=$JAVA_11
else
    echo "language must be: java, kotlin, or groovy"
fi

mkdir -p $output_dir
# merge
jacoco_final=$output_dir/$output_name.exec
$JAVA -jar $JACOCO/lib/jacococli.jar merge $jacoco_1 $jacoco_2 \
    --destfile $jacoco_final

# produce
cd $output_dir
$JAVA \
    -jar $JACOCO/lib/jacococli.jar report $output_name.exec \
    --classfiles $SOURCES \
    --html $output_name
