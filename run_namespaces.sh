#!/bin/bash

set -e  # Abbruch bei Fehler
if (( $# != 1 )); then
    echo "Usage: $0 PREFIX"
    exit 1
fi
unset DEBUG
PREFIX=$1

COLL_PREFIX="collections/$PREFIX"
LOG_PREFIX="output/logs/$PREFIX"

NS_MIN_OCCURENCES=5 # TODO später erhöhen
( time bzgrep -o "<title>.*\:.*</title>" $COLL_PREFIX-pages-meta-history.xml.bz2 | awk -F: '{print substr($1,8)}' | sort | uniq -c | awk -v limit=$NS_MIN_OCCURENCES '$1 >= limit{print $2}' | tee output/$PREFIX-namespaces.txt )|& tee $LOG_PREFIX-namespaces.log