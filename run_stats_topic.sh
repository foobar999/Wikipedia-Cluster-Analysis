#!/bin/bash -e

if (( $# != 1 )); then
    echo "Usage: $0 CONFIG"
    exit 1
fi
unset DEBUG
CONFIG=$1
source $CONFIG
if [ ! -z ${DEBUG+x} ]; then
    export DEBUG=$DEBUG
fi

COLL_PREFIX=collections/$PREFIX
BOW_PREFIX=output/bow/$PREFIX
TM_PREFIX=output/topic/$PREFIX
CLUS_PREFIX=output/clusters/$PREFIX
LOG_PREFIX=output/logs/$PREFIX

echo "PREFIX $PREFIX"
echo "NO_BELOW $NO_BELOW"
echo "NO_ABOVE $NO_ABOVE"
echo "ARTICLE_MIN_TOKENS $ARTICLE_MIN_TOKENS"
CLUSTER_METHODS=($CLUSTER_METHODS)
echo "CLUSTER_METHODS ${CLUSTER_METHODS[@]}"
echo "CONTAMINATION $CONTAMINATION"
CLUSTER_NUMS=($CLUSTER_NUMS) 
echo "CLUSTER_NUMS ${CLUSTER_NUMS[@]}"
echo "MALLET_HOME $MALLET_HOME"
export MALLET_HOME=$MALLET_HOME

# Statistiken zum Artikeldump
STATS_PREPROP_DIR=output/stats/cluster_preprocessing
mkdir -p $STATS_PREPROP_DIR
STATS_PREPROP_PREFIX=$STATS_PREPROP_DIR/$PREFIX
# Histogramm der Dokument-Tokenanzahlen
ARTICLES_DUMP=$COLL_PREFIX-pages-articles.xml.bz2
NAMESPACE_PREFIXES=output/$PREFIX-namespaces.txt
LOG_ART_TOKENS_DIST=$STATS_PREPROP_PREFIX-articles-tokens-dist.log
IMG_ART_TOKENS_DIST=$STATS_PREPROP_PREFIX-articles-tokens-dist.pdf
QUANTILE=0.95
python3 -m scripts.stats.cluster.plot_articles_tokens_dist --articles-dump=$ARTICLES_DUMP --namespace-prefixes=$NAMESPACE_PREFIXES --token-nums-dist=$IMG_ART_TOKENS_DIST --quantile-order=$QUANTILE |& tee $LOG_ART_TOKENS_DIST
# Preprocessing-Auswirkungen
LOG_ART_STATS=$STATS_PREPROP_PREFIX-articles-stats.log
TOKEN_MIN_LEN=2
python3 -m scripts.stats.cluster.get_articles_bow_stats --articles-dump=$ARTICLES_DUMP --no-below=$NO_BELOW --no-above=$NO_ABOVE --token-min-len=$TOKEN_MIN_LEN --article-min-tokens=$ARTICLE_MIN_TOKENS --namespace-prefixes=$NAMESPACE_PREFIXES |& tee $LOG_ART_STATS
cat $LOG_ART_STATS | grep "stats\|density" >> $LOG_ART_STATS

# durchschnittliche Wahrscheinlichkeiten der Topics
STATS_AVG_DIR=output/stats/cluster_avg
mkdir -p $STATS_AVG_DIR
STATS_AVG_PREFIX=$STATS_AVG_DIR/$PREFIX
BOW=$BOW_PREFIX-bow.mm.bz2
TOPIC_MODEL=$TM_PREFIX-lda
LOG_TOPIC_FILE=$STATS_AVG_PREFIX-lda-topic-avg-probs.log
python3 -m scripts.stats.cluster.get_topics_avg_probs_stats --bow=$BOW --model-prefix=$TOPIC_MODEL |& tee $LOG_TOPIC_FILE

# Plots der durchschnittlichen Anteile
DOCUMENT_TOPICS=$TM_PREFIX-lda-document-topics.npz
TOPIC_AVG_PROBS_IMG=$STATS_AVG_PREFIX-lda-topic-avg-probs.pdf
TOPIC_AVG_PROBS_CDF_IMG=$STATS_AVG_PREFIX-lda-topic-probs-avg-cdf.pdf
python3 -m scripts.stats.cluster.plot_topics_avg_probs --document-topics=$DOCUMENT_TOPICS --topic-avg-probs=$TOPIC_AVG_PROBS_IMG --topic-avg-probs-cdf=$TOPIC_AVG_PROBS_CDF_IMG

# 2D-Transformation Topicvektoren
STATS_DOC_PLOTS_DIR=output/stats/cluster_doc_plots
mkdir -p $STATS_DOC_PLOTS_DIR
STATS_DOC_PLOTS_PREFIX=$STATS_DOC_PLOTS_DIR/$PREFIX
DOCUMENT_TOPICS=$TM_PREFIX-lda-document-topics.npz
DOCUMENTS_2D=$STATS_DOC_PLOTS_PREFIX-lda-documents-2d.npz
python3 -m scripts.stats.cluster.transform_documents_2d --document-topics=$DOCUMENT_TOPICS --documents-2d=$DOCUMENTS_2D

# 2D-Plot Dokumente
DOC_DATA_IMG=$STATS_DOC_PLOTS_PREFIX-lda-document-data.pdf
python3 -m scripts.stats.cluster.plot_documents_2d --documents-2d=$DOCUMENTS_2D --img-file=$DOC_DATA_IMG 

# 2D-Plot clustergelabelte Dokumente
CLUSTER_PLOTS_DIR=output/stats/cluster_plots
mkdir -p $CLUSTER_PLOTS_DIR
CLUSTER_PLOTS_PREFIX=$CLUSTER_PLOTS_DIR/$PREFIX
for CLUSTER_METHOD in "${CLUSTER_METHODS[@]}"; do
   CMPREFIX=$CLUS_PREFIX-lda-$CLUSTER_METHOD
   IMGPREFIX=$CLUSTER_PLOTS_PREFIX-lda-$CLUSTER_METHOD
    for CLUSTER_NUM in "${CLUSTER_NUMS[@]}"; do
       CLUSTER_LABELS=$CMPREFIX-$CLUSTER_NUM.json.bz2
       DOC_CLUSTER_IMG=$IMGPREFIX-$CLUSTER_NUM.pdf
       python3 -m scripts.stats.cluster.plot_documents_2d --documents-2d=$DOCUMENTS_2D --cluster-labels=$CLUSTER_LABELS --img-file=$DOC_CLUSTER_IMG 
    done
done

# Silhouetten-plot
STATS_SILHOUETTES_DIR=output/stats/cluster_silhouettes
mkdir -p $STATS_SILHOUETTES_DIR
STATS_SILHOUETTES_PREFIX=$STATS_SILHOUETTES_DIR/$PREFIX
for CLUSTER_METHOD in "${CLUSTER_METHODS[@]}"; do
    CLUSTER_SILHOUETTE_CSV=$STATS_SILHOUETTES_PREFIX-$CLUSTER_METHOD-silhouettes.csv
    # erzeuge aus Logs CSV-Datei: jede Zeile enthält einen Eintrag "#Cluster Silhouettenkoeffizient", jede Datei bezieht sich auf 1 Clusterverfahren
    truncate -s 0 $CLUSTER_SILHOUETTE_CSV
    for CLUSTER_NUM in "${CLUSTER_NUMS[@]}"; do
        CLUSTER_LOG_FILE=$LOG_PREFIX-lda-$CLUSTER_METHOD-$CLUSTER_NUM.log
        SIL_COEFF=$(cat $CLUSTER_LOG_FILE | grep "silhouette coefficient" | sed -E 's/.*silhouette coefficient: //')
        echo "$CLUSTER_NUM $SIL_COEFF" >> $CLUSTER_SILHOUETTE_CSV
    done
    # plotte Silhouettenkoeffizienten der CSV-Datei
    CLUSTER_SILHOUETTE_PDF=$STATS_SILHOUETTES_PREFIX-$CLUSTER_METHOD-silhouettes.pdf
    python3 -m scripts.stats.cluster.plot_document_silhouettes --csv-data=$CLUSTER_SILHOUETTE_CSV --img-file=$CLUSTER_SILHOUETTE_PDF
done

# plotte Clustergrößen, absteigend sortiert
STATS_CLUSTER_SIZES_DIR=output/stats/cluster_sizes
mkdir -p $STATS_CLUSTER_SIZES_DIR
STATS_CLUSTER_SIZES_PREFIX=$STATS_CLUSTER_SIZES_DIR/$PREFIX
for CLUSTER_METHOD in "${CLUSTER_METHODS[@]}"; do
   CMPREFIX=$CLUS_PREFIX-lda-$CLUSTER_METHOD
   for CLUSTER_NUM in "${CLUSTER_NUMS[@]}"; do
       CLUSTER_LABELS=$CMPREFIX-$CLUSTER_NUM.json.bz2
       CLUSTER_SIZES_IMG=$STATS_CLUSTER_SIZES_PREFIX-lda-$CLUSTER_METHOD-$CLUSTER_NUM.pdf
       python -m scripts.stats.cluster.plot_cluster_sizes --cluster-labels=$CLUSTER_LABELS --img=$CLUSTER_SIZES_IMG
   done
done

# Reinheiten der cluster
DOCUMENT_TOPICS=$TM_PREFIX-lda-document-topics.npz
STATS_CLUSTER_PURITIES_DIR=output/stats/cluster_purities
mkdir -p $STATS_CLUSTER_PURITIES_DIR
STATS_CLUSTER_PURITIES_PREFIX=$STATS_CLUSTER_PURITIES_DIR/$PREFIX
for CLUSTER_METHOD in "${CLUSTER_METHODS[@]}"; do
   for CLUSTER_NUM in "${CLUSTER_NUMS[@]}"; do
       CLUSTER_LABELS=$CLUS_PREFIX-lda-$CLUSTER_METHOD-$CLUSTER_NUM.json.bz2
       PURITIES_PLOT_FILE=$STATS_CLUSTER_PURITIES_PREFIX-lda-$CLUSTER_METHOD-$CLUSTER_NUM-purities.pdf
       python3 -m scripts.stats.cluster.plot_cluster_purities --document-topics=$DOCUMENT_TOPICS --cluster-labels=$CLUSTER_LABELS --plot=$PURITIES_PLOT_FILE
   done
done





