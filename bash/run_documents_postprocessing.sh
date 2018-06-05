#!/bin/bash -e

if (( $# != 4 )); then
    echo "Usage: $0 PREFIX KMIN KMAX CONTAMINATION"
    exit 1
fi

PREFIX=$1
KMIN=$2
KMAX=$3
CONTAMINATION=$4

TM_PREFIX=output/topic/$PREFIX
mkdir -p output/doc_filtered
DOC_FILTERED_PREFIX=output/doc_filtered/$PREFIX
LOG_PREFIX=output/logs/$PREFIX

DOCUMENT_TOPICS=$TM_PREFIX-lda-document-topics.npz

METRICS=(euclidean cosine)
for METRIC in "${METRICS[@]}"; do
    DOC_OUTLIER_SCORES=$DOC_FILTERED_PREFIX-lda-document-outlier-scores-$METRIC.json
    LOG_OUTLIER=$LOG_PREFIX-outlier-$METRIC.log

    (time python3 -m scripts.cluster.detect_outlier_documents --document-topics=$DOCUMENT_TOPICS --outlier-scores=$DOC_OUTLIER_SCORES --k-min=$KMIN --k-max=$KMAX --metric=$METRIC) |& tee $LOG_OUTLIER
    bzip2 -zf $DOC_OUTLIER_SCORES
    
    DOCUMENT_TOPICS_FILTERED=$DOC_FILTERED_PREFIX-document-topics-filtered-$METRIC.npz
    (time python3 -m scripts.cluster.remove_outlier_documents --documents=$DOCUMENT_TOPICS --outlier-scores=$DOC_OUTLIER_SCORES.bz2 --filtered-documents=$DOCUMENT_TOPICS_FILTERED --contamination=$CONTAMINATION) |& tee -a $LOG_OUTLIER
    
done




