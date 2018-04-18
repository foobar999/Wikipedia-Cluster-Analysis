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
( time ./bash/get_likely_namespaces.sh $COLL_PREFIX-pages-meta-history.xml.bz2 $NS_MIN_OCCURENCES | tee output/$PREFIX-namespaces.txt )|& tee $LOG_PREFIX-namespaces.log