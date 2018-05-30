#!/bin/bash -e

if (( $# != 1 )); then
    echo "Usage: $0 CONFIG"
    exit 1
fi
unset DEBUG
CONFIG=$1
source $CONFIG

COLL_PREFIX=collections/$PREFIX
BOW_PREFIX=output/bow/$PREFIX
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

# Preprocessing-Auswirkungen
# ARTICLES_DUMP=$COLL_PREFIX-pages-articles.xml.bz2
# LOG_ART_STATS=$STATS_PREFIX-articles-stats.log
# NAMESPACE_PREFIXES=output/$PREFIX-namespaces.txt
# TOKEN_MIN_LEN=2
# python3 scripts/get_articles_stats.py --articles-dump=$ARTICLES_DUMP --no-below=$NO_BELOW --no-above=$NO_ABOVE --token-min-len=$TOKEN_MIN_LEN --article-min-tokens=$ARTICLE_MIN_TOKENS --namespace-prefixes=$NAMESPACE_PREFIXES |& tee $LOG_ART_STATS
# cat $LOG_ART_STATS | grep "stats\|density"

# durchschnittliche Wahrscheinlichkeiten
# BOW=$BOW_PREFIX-bow.mm.bz2
# TOPIC_MODEL=$TM_PREFIX-lda
# LOG_TOPIC_FILE=$STATS_PREFIX-lda-topic-avg-probs.log
# python3 scripts/get_topic_stats.py --bow=$BOW --model-prefix=$TOPIC_MODEL |& tee $LOG_TOPIC_FILE

# avg-plots
DOCUMENT_TOPICS=$TM_PREFIX-lda-document-topics.npz
TOPIC_AVG_PROBS_IMG=$STATS_PREFIX-lda-topic-avg-probs.pdf
TOPIC_AVG_PROBS_CDF_IMG=$STATS_PREFIX-lda-topic-probs-avg-cdf.pdf
python3 scripts/get_document_avg_viz.py --document-topics=$DOCUMENT_TOPICS --topic-avg-probs=$TOPIC_AVG_PROBS_IMG --topic-avg-probs-cdf=$TOPIC_AVG_PROBS_CDF_IMG

# 2D-Transformation
DOCUMENTS_2D=$STATS_PREFIX-documents-2d.npz
python3 scripts/get_document_2d_transformed.py --document-topics=$DOCUMENT_TOPICS --documents-2d=$DOCUMENTS_2D

# 2D-Plot Dokumente
DOC_DATA_IMG=$STATS_PREFIX-lda-document-data.pdf
python3 scripts/get_document_2d_viz.py --documents-2d=$DOCUMENTS_2D --img-file=$DOC_DATA_IMG 

# 2D-Plot Cluster-gelabelte Dokumente
for CLUSTER_METHOD in "${CLUSTER_METHODS[@]}"; do
    CMPREFIX=$CLUS_PREFIX-lda-$CLUSTER_METHOD
    IMGPREFIX=$STATS_PREFIX-lda-$CLUSTER_METHOD
    if [ $CLUSTER_METHOD == "dbscan" ]; then
        for EPSILON in "${EPSILONS[@]}"; do
            for MIN_SAMPLE in "${MIN_SAMPLES[@]}"; do
                CLUSTER_LABELS=$CMPREFIX-$EPSILON-$MIN_SAMPLE.json.bz2
                DOC_CLUSTER_IMG=$IMGPREFIX-$EPSILON-$MIN_SAMPLE.pdf
                python3 scripts/get_document_2d_viz.py --documents-2d=$DOCUMENTS_2D --cluster-labels=$CLUSTER_LABELS --img-file=$DOC_CLUSTER_IMG 
            done
        done
    else
        for CLUSTER_NUM in "${CLUSTER_NUMS[@]}"; do
            CLUSTER_LABELS=$CMPREFIX-$CLUSTER_NUM.json.bz2
            DOC_CLUSTER_IMG=$IMGPREFIX-$CLUSTER_NUM.pdf
            python3 scripts/get_document_2d_viz.py --documents-2d=$DOCUMENTS_2D --cluster-labels=$CLUSTER_LABELS --img-file=$DOC_CLUSTER_IMG 
        done
    fi
done







