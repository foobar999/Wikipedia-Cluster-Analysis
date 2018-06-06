#!/bin/bash -e


if (( $# != 1 )); then
    echo "Usage: $0 CONFIG"
    exit 1
fi
unset DEBUG
CONFIG=$1
source $CONFIG

echo "PREFIX $PREFIX"
echo "DEBUG $DEBUG"
if [ ! -z ${DEBUG+x} ]; then # variable gesetzt?
    export DEBUG=$DEBUG
fi
echo "NO_BELOW $NO_BELOW"
echo "NO_ABOVE $NO_ABOVE"
echo "ARTICLE_MIN_TOKENS $ARTICLE_MIN_TOKENS"
echo "PASSES $PASSES"
TOPIC_MODELS=($TOPIC_MODELS) # splitte String zu Array
echo "TOPIC_MODELS ${TOPIC_MODELS[@]}"
echo "NUM_TOPICS $NUM_TOPICS"
echo "ALPHA $ALPHA"
echo "BETA $BETA"
CLUSTER_METHODS=($CLUSTER_METHODS)
echo "CLUSTER_METHODS ${CLUSTER_METHODS[@]}"
CLUSTER_NUMS=($CLUSTER_NUMS) 
echo "CLUSTER_NUMS ${CLUSTER_NUMS[@]}"


BOW_CORPUS_PREFIX=output/bow/$PREFIX-bow
# ./bash/run_articles_to_bow.sh $PREFIX $NO_BELOW $NO_ABOVE $ARTICLE_MIN_TOKENS
for TOPIC_MODEL in "${TOPIC_MODELS[@]}"; do
    # ./bash/run_bow_to_topic.sh $PREFIX $TOPIC_MODEL $NUM_TOPICS $PASSES $ALPHA $BETA
    TPREFIX=$PREFIX-$TOPIC_MODEL
    for CLUSTER_METHOD in "${CLUSTER_METHODS[@]}"; do
        if [ $CLUSTER_METHOD == "dbscan" ]; then
            for EPSILON in "${EPSILONS[@]}"; do
                for MIN_SAMPLE in "${MIN_SAMPLES[@]}"; do
                    ./bash/run_topic_to_cluster.sh $TPREFIX $BOW_CORPUS_PREFIX $CLUSTER_METHOD $EPSILON $MIN_SAMPLE
                done
            done
        else
            for CLUSTER_NUM in "${CLUSTER_NUMS[@]}"; do
                ./bash/run_topic_to_cluster.sh $TPREFIX $BOW_CORPUS_PREFIX $CLUSTER_METHOD $CLUSTER_NUM 
            done
        fi
    done
done


