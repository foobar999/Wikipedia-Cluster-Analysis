#!/bin/bash -e

if (( $# != 1 )); then
    echo "Usage: $0 CONFIG"
    exit 1
fi
unset DEBUG
CONFIG=$1
source $CONFIG
echo "DEBUG $DEBUG"
if [ ! -z ${DEBUG+x} ]; then # variable gesetzt?
    export DEBUG=$DEBUG
fi

echo "PREFIX $PREFIX"
echo "NO_BELOW $NO_BELOW"
echo "NO_ABOVE $NO_ABOVE"
echo "ARTICLE_MIN_TOKENS $ARTICLE_MIN_TOKENS"
echo "MALLET_HOME $MALLET_HOME"
export MALLET_HOME=$MALLET_HOME
echo "NUM_TOPICS $NUM_TOPICS"
echo "NUM_ITERATIONS $NUM_ITERATIONS"
echo "ALPHA $ALPHA"
CLUSTER_METHODS=($CLUSTER_METHODS)
echo "CLUSTER_METHODS ${CLUSTER_METHODS[@]}"
CLUSTER_NUMS=($CLUSTER_NUMS) 
echo "CLUSTER_NUMS ${CLUSTER_NUMS[@]}"

mkdir -p output/logs
mkdir -p output/bow
mkdir -p output/topic
mkdir -p output/clusters

BOW_CORPUS_PREFIX=output/bow/$PREFIX-bow
./bash/run_articles_to_bow.sh $PREFIX $NO_BELOW $NO_ABOVE $ARTICLE_MIN_TOKENS
./bash/run_bow_to_topic.sh $PREFIX $MALLET_HOME $NUM_TOPICS $NUM_ITERATIONS $ALPHA
TPREFIX=$PREFIX-lda
for CLUSTER_METHOD in "${CLUSTER_METHODS[@]}"; do
    for CLUSTER_NUM in "${CLUSTER_NUMS[@]}"; do
        ./bash/run_topic_to_cluster.sh $TPREFIX $BOW_CORPUS_PREFIX $CLUSTER_METHOD $CLUSTER_NUM 
    done
done


