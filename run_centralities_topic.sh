#!/bin/bash -e

if (( $# != 1 )); then
    echo "Usage: $0 CONFIG"
    exit 1
fi
unset DEBUG
CONFIG=$1
source $CONFIG
if [ ! -z ${DEBUG+x} ]; then
    export DEBUG=$DEBUG
fi

BOW_PREFIX=output/bow/$PREFIX
TM_PREFIX=output/topic/$PREFIX
CLUS_PREFIX=output/clusters/$PREFIX

CLUSTER_METHODS=($CLUSTER_METHODS)
CLUSTER_NUMS=($CLUSTER_NUMS) 

# bestimmte von allen Clustern zentralste Dokumente
STATS_CENTRAL_DOCS_DIR=output/stats/cluster_central_documents
mkdir -p $STATS_CENTRAL_DOCS_DIR
STATS_CENTRAL_DOCS_PREFIX=$STATS_CENTRAL_DOCS_DIR/$PREFIX
MAX_DOCS_PER_COMM=5 # maximale Anzahl der berücksichtigten, zentralsten Dokumente je Cluster
DOCUMENT_TOPICS=$TM_PREFIX-lda-document-topics.npz
DOCUMENT_TITLES=$BOW_PREFIX-bow-titles.json.bz2
echo "calculating centrality data of clusterings"
for CLUSTER_METHOD in "${CLUSTER_METHODS[@]}"; do 
    if [[ $CLUSTER_METHOD =~ .*cos ]]; then
        METRIC="cosine"
    else
        METRIC="euclidean"
    fi
    CMPREFIX=$CLUS_PREFIX-lda-$CLUSTER_METHOD
    for CLUSTER_NUM in "${CLUSTER_NUMS[@]}"; do
        CLUSTER_LABELS=$CMPREFIX-$CLUSTER_NUM.json.bz2
        CENTRALITY_DATA=$STATS_CENTRAL_DOCS_PREFIX-$CLUSTER_METHOD-$CLUSTER_NUM-centralities.json
        LOG_FILE=$STATS_CENTRAL_DOCS_PREFIX-$CLUSTER_METHOD-$CLUSTER_NUM-centralities.log
        python3 -m scripts.stats.cluster.get_cluster_central_documents --document-topics=$DOCUMENT_TOPICS --cluster-labels=$CLUSTER_LABELS --titles=$DOCUMENT_TITLES --centrality-data=$CENTRALITY_DATA --max-docs-per-clus=$MAX_DOCS_PER_COMM --metric=$METRIC |& tee $LOG_FILE
        bzip2 -zf $CENTRALITY_DATA
    done
done

# zeige von ausgewählten, äidistanten Communities die zentralsten Titel an
STATS_CENTRAL_DOCS_SAMPLE_DIR=output/stats/cluster_central_documents_sample
mkdir -p $STATS_CENTRAL_DOCS_SAMPLE_DIR
STATS_CENTRAL_DOCS_SAMPLE_PREFIX=$STATS_CENTRAL_DOCS_SAMPLE_DIR/$PREFIX
NUM_SAMPLE_COMMUNITIES=5 # maximale Anzahl angezeigter Cluster
echo "displaying titles of sample clusters"
for CLUSTER_METHOD in "${CLUSTER_METHODS[@]}"; do 
    for CLUSTER_NUM in "${CLUSTER_NUMS[@]}"; do
        CENTRALITY_DATA=$STATS_CENTRAL_DOCS_PREFIX-$CLUSTER_METHOD-$CLUSTER_NUM-centralities.json.bz2
        LOG_SAMPLES=$STATS_CENTRAL_DOCS_SAMPLE_PREFIX-$CLUSTER_METHOD-$CLUSTER_NUM-sample-titles.log
        python3 -m scripts.stats.get_sample_central_titles --centrality-data=$CENTRALITY_DATA --num-parts=$NUM_SAMPLE_COMMUNITIES |& tee $LOG_SAMPLES
    done
done
