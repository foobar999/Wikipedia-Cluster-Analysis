#!/bin/bash -e


if (( $# != 4 )); then
    echo "Usage: $0 IPREFIX COMM_METHOD CONSIDER_ONLY_COMMUNITIES TITLES"
    exit 1
fi
IPREFIX=$1
COMM_METHOD=$2
CONSIDER_ONLY_COMMUNITIES=$3
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
(time python3 -m scripts.community.coauth_to_community --coauth-graph=$COAUTH_GRAPH --communities=$COMMUNITIES --method=$COMM_METHOD --consider-only-communities=$CONSIDER_ONLY_COMMUNITIES) |& tee $LOG_COMMUNITIES
bzip2 -zf $COMMUNITIES

echo "generating documenttitle->communitylabel mappings"
python3 -m scripts.utils.get_title_partitions --partitions=$COMMUNITIES.bz2 --titles=$TITLES --title-partitions=$TITLE_COMMUNITIES
bzip2 -zf $TITLE_COMMUNITIES




