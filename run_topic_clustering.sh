#!/bin/bash -e

# TODO aufpassen beim topicmodel laden, dass auch das richtige model geladen
# TODO mal verschiendene maße (insb jsd) ausprobieren, dafür scipy clustering nehmen
# TODO soll ich echte minibatch kmeans nehmen? is mehr zu erklären
# TODO verschiedene clusteringverfahren: trivial, k-means, hierarchisch
# TODO index wird bisher nichtgelesen, da datei mit .bz2 umbenannt -> später Performanceverlust deshalb? -> mit und ohne kompression testen
# TODO time auf stunden umrechnen / besseres zeitmesskommando finden


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

#./bash/run_articles_to_bow.sh $PREFIX $NO_BELOW $NO_ABOVE $ARTICLE_MIN_TOKENS
BOW_CORPUS_PREFIX=output/bow/$PREFIX-bow
for TOPIC_MODEL in "${TOPIC_MODELS[@]}"; do
    #./bash/run_bow_to_topic.sh $PREFIX $TOPIC_MODEL $NUM_TOPICS $PASSES $ALPHA $BETA
    TPREFIX=$PREFIX-$TOPIC_MODEL
    for CLUSTER_METHOD in "${CLUSTER_METHODS[@]}"; do
        for CLUSTER_NUM in "${CLUSTER_NUMS[@]}"; do
            ./bash/run_topic_to_cluster.sh $TPREFIX $CLUSTER_METHOD $CLUSTER_NUM $BOW_CORPUS_PREFIX
        done
    done
done


