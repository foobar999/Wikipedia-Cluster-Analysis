#!/bin/bash -e

if (( $# != 5 )); then
    #echo "Usage: $0 IPREFIX TOPIC_MODEL NUM_TOPICS PASSES ALPHA BETA"
    echo "Usage: $0 PREFIX MALLET_HOME NUM_TOPICS NUM_ITERATIONS ALPHA"
    exit 1
fi

IPREFIX=$1
OPREFIX=$IPREFIX-lda
MALLET_HOME=$2
NUM_TOPICS=$3
NUM_ITERATIONS=$4
ALPHA=$5

BOW_PREFIX=output/bow/$IPREFIX
TM_PREFIX=output/topic/$OPREFIX
LOG_PREFIX=output/logs/$OPREFIX

BOW_CORPUS_PREFIX=$BOW_PREFIX-bow
BOW_MODEL=$BOW_CORPUS_PREFIX.mm
BOW_ID2WORD=$BOW_CORPUS_PREFIX-id2word.txt 
MALLET_EXECUTABLE=$MALLET_HOME/bin/mallet

MODEL_PREFIX=$TM_PREFIX
DOC_TOPICS_FILE=$TM_PREFIX-document-topics.npz
LOG_TOPIC=$LOG_PREFIX.log

echo "generating mallet lda model"
( time python3 -m scripts.cluster.bow_to_topic --bow=$BOW_MODEL.bz2 --id2word=$BOW_ID2WORD.bz2 --mallet=$MALLET_EXECUTABLE --model-prefix=$MODEL_PREFIX --num-topics=$NUM_TOPICS --num-iterations=$NUM_ITERATIONS --alpha=$ALPHA ) |& tee $LOG_TOPIC
 
echo "generating dense document-topic-file"
( time python3 -m scripts.cluster.get_dense_document_topics --bow=$BOW_MODEL.bz2 --model-prefix=$MODEL_PREFIX --document-topics=$DOC_TOPICS_FILE ) |& tee -a $LOG_TOPIC




