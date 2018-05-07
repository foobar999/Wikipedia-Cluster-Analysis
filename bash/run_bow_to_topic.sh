#!/bin/bash -e

# TODO at einbaubar machen

if (( $# != 5 )); then
    echo "Usage: $0 PREFIX NUM_TOPICS PASSES ALPHA BETA"
    exit 1
fi
unset DEBUG
PREFIX=$1
NUM_TOPICS=$2
PASSES=$3
ALPHA=$4
BETA=$5

BOW_PREFIX=output/bow/$PREFIX
TM_PREFIX=output/topic/$PREFIX
LOG_PREFIX=output/logs/$PREFIX

BOW_CORPUS_PREFIX=$BOW_PREFIX-bow
BOW_MODEL=$BOW_CORPUS_PREFIX.mm
BOW_ID2WORD=$BOW_CORPUS_PREFIX-id2word.txt 

MODEL_PREFIX=$TM_PREFIX-lda
LOG_TOPIC=$LOG_PREFIX-lda.log

ITERATIONS=$(( 10*$PASSES ))
echo "generating lda model"
( time python scripts/bow_to_topic.py --bow=$BOW_MODEL.bz2 --id2word=$BOW_ID2WORD.bz2 --model-prefix=$MODEL_PREFIX --num-topics=$NUM_TOPICS --passes=$PASSES --iterations=$ITERATIONS --alpha=$ALPHA --beta=$BETA ) |& tee $LOG_TOPIC
# TODO .bz2 oder nicht???





