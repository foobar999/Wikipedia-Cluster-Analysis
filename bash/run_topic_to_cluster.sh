#!/bin/bash -e

if (( $# != 4 )); then
    echo "Usage: $0 IPREFIX METHOD NUM_CLUSTERS BOW_CORPUS_PREFIX"
    exit 1
fi

IPREFIX=$1
METHOD=$2
NUM_CLUSTERS=$3
OPREFIX=$IPREFIX-$METHOD-$NUM_CLUSTERS
BOW_CORPUS_PREFIX=$4

TM_PREFIX=output/topic/$IPREFIX
CLUS_PREFIX=output/clusters/$OPREFIX
LOG_PREFIX=output/logs/$OPREFIX

BOW_MODEL=$BOW_CORPUS_PREFIX.mm
BOW_TITLES=$BOW_CORPUS_PREFIX-titles.json

CLUSTER_LABELS=$CLUS_PREFIX.json
TITLE_CLUSTER_LABELS=$CLUS_PREFIX-titleclusters.json
LOG_CLUSTER=$LOG_PREFIX.log

BATCHSIZE=1000
echo "computing $NUM_CLUSTERS clusters with $METHOD"
(time python scripts/topic_to_cluster.py --bow=$BOW_MODEL.bz2 --tm=$TM_PREFIX --cluster-labels=$CLUSTER_LABELS --cluster-method=$METHOD --num-clusters=$NUM_CLUSTERS --batch-size=$BATCHSIZE) |& tee $LOG_CLUSTER

echo "evaluating clustering"
(time python scripts/evaluate_dense_clustering.py --bow=$BOW_MODEL.bz2 --tm=$TM_PREFIX --cluster-labels=$CLUSTER_LABELS) |& tee -a $LOG_CLUSTER
bzip2 -zf $CLUSTER_LABELS

echo "generating documenttitle->clusterlabel mappings"
python scripts/utils/get_title_communities.py --communities=$CLUSTER_LABELS.bz2 --titles=$BOW_TITLES.bz2 --titlecomms=$TITLE_CLUSTER_LABELS
bzip2 -zf $TITLE_CLUSTER_LABELS



