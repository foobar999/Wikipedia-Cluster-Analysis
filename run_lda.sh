#!/bin/bash

calc() { awk "BEGIN{print $*}"; }   # für Gleitkommaoperationen
set -e  # Abbruch bei Fehler
if (( $# != 1 )); then
    echo "Usage: $0 PREFIX"
    exit 1
fi
unset DEBUG
PREFIX=$1

BOW_PREFIX="output/bow/$PREFIX"
TM_PREFIX="output/topic/$PREFIX"
LOG_PREFIX="output/logs/$PREFIX"

NUMTOPICS=100
PASSES=100 # TODO größer?
ITERATIONS=10000
ALPHA=$(calc 50/$NUMTOPICS)
BETA=0.01
echo "generating lda model"
( time python scripts/bow_to_topic.py $BOW_PREFIX-corpus.mm.bz2 $BOW_PREFIX-corpus.id2word.cpickle.bz2 $TM_PREFIX-lda-model $NUMTOPICS --passes=$PASSES --iterations=$ITERATIONS --alpha=$ALPHA --beta=$BETA ) |& tee $LOG_PREFIX-lda.log
# TODO .bz2 oder nicht???