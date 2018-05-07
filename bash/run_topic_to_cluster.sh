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

#BOW_PREFIX=output/bow/$PREFIX
TM_PREFIX=output/topic/$IPREFIX
CLUS_PREFIX=output/clusters/$OPREFIX
LOG_PREFIX=output/logs/$OPREFIX

# TODO nicht pickeln
CLUSTER_LABELS=$CLUS_PREFIX.cpickle
LOG_CLUSTER=$LOG_PREFIX.log

#NUMCLUSTERS=100
BATCHSIZE=1000
echo "computing $NUM_CLUSTERS clusters with $METHOD"
( time python scripts/topic_to_cluster.py --bow=$BOW --tm=$TM_PREFIX --cluster-labels=$CLUSTER_LABELS.bz2 --cluster-method=$METHOD --num-clusters=$NUM_CLUSTERS --batch-size=$BATCHSIZE ) |& tee $LOG_CLUSTER
#python scripts/utils/binary_to_text.py numpy $CLUS_PREFIX-kmeans-labels.cpickle.bz2 $CLUS_PREFIX-kmeans-labels.txt # TODO produktiv raus