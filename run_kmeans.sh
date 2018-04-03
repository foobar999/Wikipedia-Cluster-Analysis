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

NUMCLUSTERS=100
BATCHSIZE=1000
echo "computing kmeans clusters"
time python scripts/run_kmeans.py $BOW_PREFIX-corpus.mm.bz2 $TM_PREFIX-lda-model $CLUS_PREFIX-kmeans-labels.cpickle.bz2 $NUMCLUSTERS --batch-size=$BATCHSIZE 2>&1 | tee $LOG_PREFIX-kmeans.log
python scripts/utils/binary_to_text.py numpy $CLUS_PREFIX-kmeans-labels.cpickle.bz2 $CLUS_PREFIX-kmeans-labels.txt # TODO produktiv raus