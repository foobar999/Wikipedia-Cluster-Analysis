#!/bin/bash -e

if (( $# != 6 )); then
    echo "Usage: $0 IPREFIX TOPIC_MODEL NUM_TOPICS PASSES ALPHA BETA"
    exit 1
fi

IPREFIX=$1
TOPIC_MODEL=$2
OPREFIX=$IPREFIX-$TOPIC_MODEL
NUM_TOPICS=$3
PASSES=$4
ALPHA=$5
BETA=$6

BOW_PREFIX=output/bow/$IPREFIX
TM_PREFIX=output/topic/$OPREFIX
LOG_PREFIX=output/logs/$OPREFIX

BOW_CORPUS_PREFIX=$BOW_PREFIX-bow
BOW_MODEL=$BOW_CORPUS_PREFIX.mm
BOW_ID2WORD=$BOW_CORPUS_PREFIX-id2word.txt 

MODEL_PREFIX=$TM_PREFIX
DOC_TOPICS_FILE=$TM_PREFIX-document-topics.npz
LOG_TOPIC=$LOG_PREFIX.log

ITERATIONS=$(( 10*$PASSES ))
echo "generating $TOPIC_MODEL model"
( time python3 -m scripts.cluster.bow_to_topic --bow=$BOW_MODEL.bz2 --id2word=$BOW_ID2WORD.bz2 --model-type=$TOPIC_MODEL --model-prefix=$MODEL_PREFIX --num-topics=$NUM_TOPICS --passes=$PASSES --iterations=$ITERATIONS --alpha=$ALPHA --beta=$BETA ) |& tee $LOG_TOPIC
# TODO .bz2 oder nicht???

echo "generating dense document-topic-file"
( time python3 -m scripts.cluster.get_dense_document_topics --bow=$BOW_MODEL.bz2 --model-prefix=$MODEL_PREFIX --document-topics=$DOC_TOPICS_FILE ) |& tee -a $LOG_TOPIC




