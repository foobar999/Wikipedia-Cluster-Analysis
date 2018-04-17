#!/bin/bash -e

if (( $# != 2 )); then
    echo "Usage: $0 DUMP NS_MIN_OCCURENCES"
    exit 1
fi
DUMP=$1
NS_MIN_OCCURENCES=$2

bzgrep -o "<title>.*\:.*</title>" $DUMP | awk -F: '{print substr($1,8)}' | sort | uniq -c | awk -v limit=$NS_MIN_OCCURENCES '$1 >= limit{print $2}' 