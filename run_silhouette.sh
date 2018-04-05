#!/bin/bash

set -e  # Abbruch bei Fehler
if (( $# != 1 )); then
    echo "Usage: $0 PREFIX"
    exit 1
fi
unset DEBUG
PREFIX=$1

BOW_PREFIX="output/bow/$PREFIX"
TM_PREFIX="output/topic/$PREFIX"
CLUS_PREFIX="output/clusters/$PREFIX"
LOG_PREFIX="logs/$PREFIX"

echo "calculating silhouette score"
( time python scripts/evaluate_dense.py $BOW_PREFIX-corpus.mm.bz2 $TM_PREFIX-lda-model $CLUS_PREFIX-kmeans-labels.cpickle.bz2 ) |& tee $LOG_PREFIX-silhouette.log