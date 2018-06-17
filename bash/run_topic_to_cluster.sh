#!/bin/bash -e

if [ $# != 4 ]; then
    echo "Usage: $0 IPREFIX BOW_CORPUS_PREFIX METHOD NUM_CLUSTERS"
    exit 1
fi

IPREFIX=$1
BOW_CORPUS_PREFIX=$2
METHOD=$3
NUM_CLUSTERS=$4
OPREFIX=$IPREFIX-$METHOD-$NUM_CLUSTERS   
    
TM_PREFIX=output/topic/$IPREFIX
CLUS_PREFIX=output/clusters/$OPREFIX
LOG_PREFIX=output/logs/$OPREFIX

BOW_TITLES=$BOW_CORPUS_PREFIX-titles.json
DOCUMENT_TOPICS=$TM_PREFIX-document-topics.npz

CLUSTER_LABELS=$CLUS_PREFIX.json
TITLE_CLUSTER_LABELS=$CLUS_PREFIX-titleclusters.json
LOG_CLUSTER=$LOG_PREFIX.log

echo "computing clusters with $METHOD"
(time python3 -m scripts.cluster.topic_to_cluster --document-topics=$DOCUMENT_TOPICS --cluster-labels=$CLUSTER_LABELS --cluster-method=$METHOD --num-clusters=$NUM_CLUSTERS) |& tee $LOG_CLUSTER
bzip2 -zf $CLUSTER_LABELS

echo "evaluating clustering"
if [[ $METHOD =~ .*cos ]]; then
    METRIC="cosine"
else
    METRIC="euclidean"
fi
(time python3 -m scripts.stats.cluster.evaluate_dense_clustering --document-topics=$DOCUMENT_TOPICS --cluster-labels=$CLUSTER_LABELS.bz2 --metric=$METRIC) |& tee -a $LOG_CLUSTER

echo "generating documenttitle->clusterlabel mappings"
python3 -m scripts.utils.get_title_communities --communities=$CLUSTER_LABELS.bz2 --titles=$BOW_TITLES.bz2 --titlecomms=$TITLE_CLUSTER_LABELS
bzip2 -zf $TITLE_CLUSTER_LABELS

