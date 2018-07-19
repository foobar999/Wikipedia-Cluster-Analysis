#!/bin/bash -e

if (( $# != 2 )); then
    echo "Usage: $0 CONFIG MIN_OCCURENCES"
    exit 1
fi
CONFIG=$1
MIN_OCCURENCES=$2
source $CONFIG

echo "PREFIX $PREFIX"
echo "MIN_OCCURENCES $MIN_OCCURENCES"

COLL_PREFIX=collections/$PREFIX
LOG_PREFIX=output/logs/$PREFIX

COLLECTION=$COLL_PREFIX-pages-meta-history.xml.bz2
NAMESPACES_LIST=output/$PREFIX-namespaces.txt
LOG_FILE=$LOG_PREFIX-namespaces.log

echo "extracting title prefixes from $COLLECTION appearing at least $MIN_OCCURENCES times"
( time ./bash/get_likely_namespaces.sh $COLLECTION $MIN_OCCURENCES | tee $NAMESPACES_LIST )|& tee $LOG_FILE