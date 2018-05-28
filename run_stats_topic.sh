#!/bin/bash -e

if (( $# != 1 )); then
    echo "Usage: $0 CONFIG"
    exit 1
fi
unset DEBUG
CONFIG=$1
source $CONFIG

COLL_PREFIX=collections/$PREFIX
TM_PREFIX=output/topic/$PREFIX
CLUS_PREFIX=output/clusters/$PREFIX
STATS_PREFIX=output/stats/$PREFIX

echo "PREFIX $PREFIX"
echo "DEBUG $DEBUG"
if [ ! -z ${DEBUG+x} ]; then # variable gesetzt?
    export DEBUG=$DEBUG
fi
echo "NO_BELOW $NO_BELOW"
echo "NO_ABOVE $NO_ABOVE"
echo "ARTICLE_MIN_TOKENS $ARTICLE_MIN_TOKENS"
CLUSTER_METHODS=($CLUSTER_METHODS)
echo "CLUSTER_METHODS ${CLUSTER_METHODS[@]}"
CLUSTER_NUMS=($CLUSTER_NUMS) 
echo "CLUSTER_NUMS ${CLUSTER_NUMS[@]}"
EPSILONS=($EPSILONS)
echo "EPSILONS ${EPSILONS[@]}"
MIN_SAMPLES=($MIN_SAMPLES)
echo "MIN_SAMPLES ${MIN_SAMPLES[@]}"


ARTICLES_DUMP=$COLL_PREFIX-pages-articles.xml.bz2
LOG_ART_STATS=$STATS_PREFIX-articles-stats.log
NAMESPACE_PREFIXES=output/$PREFIX-namespaces.txt
TOKEN_MIN_LEN=2
python3 scripts/get_articles_stats.py --articles-dump=$ARTICLES_DUMP --no-below=$NO_BELOW --no-above=$NO_ABOVE --token-min-len=$TOKEN_MIN_LEN --article-min-tokens=$ARTICLE_MIN_TOKENS --namespace-prefixes=$NAMESPACE_PREFIXES |& tee  $LOG_ART_STATS
cat $LOG_ART_STATS | grep "stats\|density"

DOCUMENT_TOPICS=$TM_PREFIX-lda-document-topics.npz
DOC_DATA_IMG=$STATS_PREFIX-lda-document-data.pdf
TOPIC_AVG_PROBS_IMG=$STATS_PREFIX-lda-topic-avg-probs.pdf
TOPIC_AVG_PROBS_CDF_IMG=$STATS_PREFIX-lda-topic-probs-avg-cdf.pdf
python3 scripts/get_document_viz.py --document-topics=$DOCUMENT_TOPICS --doc-data=$DOC_DATA_IMG --topic-avg-probs=$TOPIC_AVG_PROBS_IMG --topic-avg-probs-cdf=$TOPIC_AVG_PROBS_CDF_IMG

for CLUSTER_METHOD in "${CLUSTER_METHODS[@]}"; do
    CMPREFIX=$CLUS_PREFIX-lda-$CLUSTER_METHOD
    IMGPREFIX=$STATS_PREFIX-lda-$CLUSTER_METHOD
    if [ $CLUSTER_METHOD == "dbscan" ]; then
        for EPSILON in "${EPSILONS[@]}"; do
            for MIN_SAMPLE in "${MIN_SAMPLES[@]}"; do
                CLUS_FILE=$CMPREFIX-$EPSILON-$MIN_SAMPLE.json.bz2
                IMG_FILE=$IMGPREFIX-$EPSILON-$MIN_SAMPLE.pdf
                python3 scripts/get_document_clustering_viz.py --document-topics=$DOCUMENT_TOPICS --cluster-labels=$CLUS_FILE --img-file=$IMG_FILE
            done
        done
    else
        for CLUSTER_NUM in "${CLUSTER_NUMS[@]}"; do
            CLUS_FILE=$CMPREFIX-$CLUSTER_NUM.json.bz2
            IMG_FILE=$IMGPREFIX-$CLUSTER_NUM.pdf
            python3 scripts/get_document_clustering_viz.py --document-topics=$DOCUMENT_TOPICS --cluster-labels=$CLUS_FILE --img-file=$IMG_FILE
        done
    fi
done







