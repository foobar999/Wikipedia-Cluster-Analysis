#!/bin/bash -e

if (( $# != 2 )); then
    echo "Usage: $0 IPREFIX COMM_METHOD"
    exit 1
fi
IPREFIX=$1
COMM_METHOD=$2
OPREFIX=$IPREFIX-$COMM_METHOD

GRAPH_PREFIX=output/graph/$IPREFIX
mkdir -p output/communities
COMM_PREFIX=output/communities/$OPREFIX
LOG_PREFIX=output/logs/$OPREFIX

COAUTH_GRAPH=$GRAPH_PREFIX-coauth.graph.gz
COMMUNITIES=$COMM_PREFIX-communities.json

LOG_COMMUNITIES=$LOG_PREFIX-communities.log

echo "running community detection"
USE_GIANT_COMP=n
(time python scripts/coauth_to_community.py --coauth-graph=$COAUTH_GRAPH --communities=$COMMUNITIES --method=$COMM_METHOD --use-giant-comp=$USE_GIANT_COMP) |& tee $LOG_COMMUNITIES
bzip2 -zf $COMMUNITIES