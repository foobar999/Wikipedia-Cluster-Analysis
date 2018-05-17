#!/bin/bash -e


if (( $# != 4 )); then
    echo "Usage: $0 IPREFIX COMM_METHOD USE_GIANT_COMP TITLES"
    exit 1
fi
IPREFIX=$1
COMM_METHOD=$2
USE_GIANT_COMP=$3
TITLES=$4
OPREFIX=$IPREFIX-$COMM_METHOD

CONTRIB_PREFIX=output/contribs/$IPREFIX
GRAPH_PREFIX=output/graph/$IPREFIX
mkdir -p output/communities
COMM_PREFIX=output/communities/$OPREFIX
LOG_PREFIX=output/logs/$OPREFIX

COAUTH_GRAPH=$GRAPH_PREFIX-coauth.graph.gz
COMMUNITIES=$COMM_PREFIX-communities.json
TITLE_COMMUNITIES=$COMM_PREFIX-titlecommunities.json

LOG_COMMUNITIES=$LOG_PREFIX-communities.log

echo "running community detection"
(time python3 scripts/coauth_to_community.py --coauth-graph=$COAUTH_GRAPH --communities=$COMMUNITIES --method=$COMM_METHOD --use-giant-comp=$USE_GIANT_COMP) |& tee $LOG_COMMUNITIES
bzip2 -zf $COMMUNITIES

echo "creating title->communitylabel mapping file"
python3 ./scripts/utils/get_title_communities.py  --communities=$COMMUNITIES.bz2 --titles=$TITLES --titlecomms=$TITLE_COMMUNITIES
bzip2 -zf $TITLE_COMMUNITIES

