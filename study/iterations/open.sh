#! /bin/bash
FILE=$1
echo $FILE
links=""
for l in $(cat $FILE); do
    urls=(${l//,/ })
    links="${links} ${urls[0]} ${urls[1]}"
done
firefox $links
