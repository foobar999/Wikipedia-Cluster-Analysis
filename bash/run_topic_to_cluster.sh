#!/bin/bash -e

if (( $# != 4 )); then
    echo "Usage: $0 IPREFIX METHOD NUM_CLUSTERS BOW"
    exit 1
fi

IPREFIX=$1
METHOD=$2
NUM_CLUSTERS=$3
OPREFIX=$IPREFIX-$METHOD-$NUM_CLUSTERS
BOW=$4

TM_PREFIX=output/topic/$IPREFIX
CLUS_PREFIX=output/clusters/$OPREFIX
LOG_PREFIX=output/logs/$OPREFIX

CLUSTER_LABELS=$CLUS_PREFIX.json
LOG_CLUSTER=$LOG_PREFIX.log

BATCHSIZE=1000
echo "computing $NUM_CLUSTERS clusters with $METHOD"
( time python scripts/topic_to_cluster.py --bow=$BOW --tm=$TM_PREFIX --cluster-labels=$CLUSTER_LABELS --cluster-method=$METHOD --num-clusters=$NUM_CLUSTERS --batch-size=$BATCHSIZE ) |& tee $LOG_CLUSTER
bzip2 -zf $CLUSTER_LABELS