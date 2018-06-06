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
LOG_PREFIX=output/logs/$PREFIX


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
echo "CONTAMINATION $CONTAMINATION"
CLUSTER_NUMS=($CLUSTER_NUMS) 
echo "CLUSTER_NUMS ${CLUSTER_NUMS[@]}"
EPSILONS=($EPSILONS)
echo "EPSILONS ${EPSILONS[@]}"
MIN_SAMPLES=($MIN_SAMPLES)
echo "MIN_SAMPLES ${MIN_SAMPLES[@]}"

# Preprocessing-Auswirkungen
STATS_PREPROP_DIR=output/stats/cluster_preprocessing
mkdir -p $STATS_PREPROP_DIR
STATS_PREPROP_PREFIX=$STATS_PREPROP_DIR/$PREFIX
# ARTICLES_DUMP=$COLL_PREFIX-pages-articles.xml.bz2
# LOG_ART_STATS=$STATS_PREPROP_PREFIX-articles-stats.log
# NAMESPACE_PREFIXES=output/$PREFIX-namespaces.txt
# TOKEN_MIN_LEN=2
# python3 -m scripts.stats.cluster.get_articles_stats --articles-dump=$ARTICLES_DUMP --no-below=$NO_BELOW --no-above=$NO_ABOVE --token-min-len=$TOKEN_MIN_LEN --article-min-tokens=$ARTICLE_MIN_TOKENS --namespace-prefixes=$NAMESPACE_PREFIXES |& tee $LOG_ART_STATS
# cat $LOG_ART_STATS | grep "stats\|density" >> $LOG_ART_STATS

# durchschnittliche Wahrscheinlichkeiten
STATS_AVG_PREFIX=output/stats/cluster_avg
mkdir -p $STATS_AVG_PREFIX
STATS_AVG_PREFIX=$STATS_AVG_PREFIX/$PREFIX
# BOW=$BOW_PREFIX-bow.mm.bz2
# TOPIC_MODEL=$TM_PREFIX-lda
# LOG_TOPIC_FILE=$STATS_AVG_PREFIX-lda-topic-avg-probs.log
# python3 -m scripts.stats.cluster.get_topic_stats --bow=$BOW --model-prefix=$TOPIC_MODEL |& tee $LOG_TOPIC_FILE

# avg-plots
DOCUMENT_TOPICS=$TM_PREFIX-lda-document-topics.npz
# TOPIC_AVG_PROBS_IMG=$STATS_AVG_PREFIX-lda-topic-avg-probs.pdf
# TOPIC_AVG_PROBS_CDF_IMG=$STATS_AVG_PREFIX-lda-topic-probs-avg-cdf.pdf
# python3 -m scripts.stats.cluster.get_document_avg_viz --document-topics=$DOCUMENT_TOPICS --topic-avg-probs=$TOPIC_AVG_PROBS_IMG --topic-avg-probs-cdf=$TOPIC_AVG_PROBS_CDF_IMG

STATS_DOC_PLOTS_DIR=output/stats/cluster_doc_plots
mkdir -p $STATS_DOC_PLOTS_DIR
STATS_DOC_PLOTS_PREFIX=$STATS_DOC_PLOTS_DIR/$PREFIX
# 2D-Transformation
DOCUMENTS_2D=$STATS_DOC_PLOTS_PREFIX-lda-documents-2d.npz
#python3 -m scripts.stats.cluster.get_document_2d_transformed --document-topics=$DOCUMENT_TOPICS --documents-2d=$DOCUMENTS_2D

# 2D-Plot Dokumente
DOC_DATA_IMG=$STATS_DOC_PLOTS_PREFIX-lda-document-data.pdf
#python3 -m scripts.stats.cluster.get_document_2d_viz --documents-2d=$DOCUMENTS_2D --img-file=$DOC_DATA_IMG 

# 2D-Plot Cluster-gelabelte Dokumente
CLUSTER_PLOTS_DIR=output/stats/cluster_plots
mkdir -p $CLUSTER_PLOTS_DIR
CLUSTER_PLOTS_PREFIX=$CLUSTER_PLOTS_DIR/$PREFIX
#for CLUSTER_METHOD in "${CLUSTER_METHODS[@]}"; do
#    CMPREFIX=$CLUS_PREFIX-lda-$CLUSTER_METHOD
#    IMGPREFIX=$CLUSTER_PLOTS_PREFIX-lda-$CLUSTER_METHOD
#    if [ $CLUSTER_METHOD == "dbscan" ]; then
#        for EPSILON in "${EPSILONS[@]}"; do
#            for MIN_SAMPLE in "${MIN_SAMPLES[@]}"; do
#                CLUSTER_LABELS=$CMPREFIX-$EPSILON-$MIN_SAMPLE.json.bz2
#                DOC_CLUSTER_IMG=$IMGPREFIX-$EPSILON-$MIN_SAMPLE.pdf
#                python3 -m scripts.stats.cluster.get_document_2d_viz --documents-2d=$DOCUMENTS_2D --cluster-labels=$CLUSTER_LABELS --img-file=$DOC_CLUSTER_IMG 
#            done
#        done
#    else
#        for CLUSTER_NUM in "${CLUSTER_NUMS[@]}"; do
#            CLUSTER_LABELS=$CMPREFIX-$CLUSTER_NUM.json.bz2
#            DOC_CLUSTER_IMG=$IMGPREFIX-$CLUSTER_NUM.pdf
#            python3 -m scripts.stats.cluster.get_document_2d_viz --documents-2d=$DOCUMENTS_2D --cluster-labels=$CLUSTER_LABELS --img-file=$DOC_CLUSTER_IMG 
#        done
#    fi
#done

# silhouetten-plot
STATS_SILHOUETTES_DIR=output/stats/cluster_silhouettes
mkdir -p $STATS_SILHOUETTES_DIR
STATS_SILHOUETTES_PREFIX=$STATS_SILHOUETTES_DIR/$PREFIX
# nur Vielfache von 25, maximal 300
for CLUSTER_METHOD in "${CLUSTER_METHODS[@]}"; do
    CLUSTER_LOG_PREFIX=$LOG_PREFIX-lda-$CLUSTER_METHOD-
    CLUSTER_SILHOUETTE_CSV=$STATS_SILHOUETTES_PREFIX-$CLUSTER_METHOD-silhouettes.csv
    # für simple-collection: erlaube kleine Werte
    # sonst: nur 25er-Schritte
    ./bash/get_silhouette_data_from_logs.sh $CLUSTER_LOG_PREFIX | awk '{if ($1 < 5 || ($1 % 25 == 0 && $1 <= 400))  {print} }' > $CLUSTER_SILHOUETTE_CSV
    CLUSTER_SILHOUETTE_PDF=$STATS_SILHOUETTES_PREFIX-$CLUSTER_METHOD-silhouettes.pdf
    python3 -m scripts.stats.cluster.get_silhouette_plot --csv-data=$CLUSTER_SILHOUETTE_CSV --img-file=$CLUSTER_SILHOUETTE_PDF
done

# absteigende Clustergrößen
STATS_CLUSTER_SIZES_DIR=output/stats/cluster_sizes
mkdir -p $STATS_CLUSTER_SIZES_DIR
STATS_CLUSTER_SIZES_PREFIX=$STATS_CLUSTER_SIZES_DIR/$PREFIX
for CLUSTER_METHOD in "${CLUSTER_METHODS[@]}"; do
   CMPREFIX=$CLUS_PREFIX-lda-$CLUSTER_METHOD
   for CLUSTER_NUM in "${CLUSTER_NUMS[@]}"; do
       CLUSTER_LABELS=$CMPREFIX-$CLUSTER_NUM.json.bz2
       CLUSTER_SIZES_IMG=$STATS_CLUSTER_SIZES_PREFIX-lda-$CLUSTER_METHOD-$CLUSTER_NUM.pdf
       python -m scripts.stats.cluster.get_cluster_stats --cluster-labels=$CLUSTER_LABELS --img=$CLUSTER_SIZES_IMG
   done
done


# zentralste Dokumente je Cluster
STATS_CENTRAL_DIR=output/stats/cluster_central
mkdir -p $STATS_CENTRAL_DIR
STATS_CENTRAL_PREFIX=$STATS_CENTRAL_DIR/$PREFIX
#K=5
#J=5
#DOCUMENT_TOPICS=$TM_PREFIX-lda-document-topics.npz
#DOCUMENT_TITLES=$BOW_PREFIX-bow-titles.json.bz2
#for CLUSTER_METHOD in "${CLUSTER_METHODS[@]}"; do
#    CMPREFIX=$CLUS_PREFIX-lda-$CLUSTER_METHOD
#    if [ $CLUSTER_METHOD == "dbscan" ]; then
#        for EPSILON in "${EPSILONS[@]}"; do
#            for MIN_SAMPLE in "${MIN_SAMPLES[@]}"; do
#                CLUSTER_LABELS=$CMPREFIX-$EPSILON-$MIN_SAMPLE.json.bz2
#                LOG_FILE=$STATS_CENTRAL_PREFIX-$CLUSTER_METHOD-$EPSILON-$MIN_SAMPLE-central-titles.log
#                python3 -m scripts.stats.cluster.get_cluster_centrality_stats --document-topics=$DOCUMENT_TOPICS --cluster-labels=$CLUSTER_LABELS --titles=$DOCUMENT_TITLES --K=$K --J=$J |& tee $LOG_FILE
#            done
#        done
#    else
#        for CLUSTER_NUM in "${CLUSTER_NUMS[@]}"; do
#            CLUSTER_LABELS=$CMPREFIX-$CLUSTER_NUM.json.bz2
#            LOG_FILE=$STATS_CENTRAL_PREFIX-$CLUSTER_METHOD-$CLUSTER_NUM-central-titles.log
#            python3 -m scripts.stats.cluster.get_cluster_centrality_stats --document-topics=$DOCUMENT_TOPICS --cluster-labels=$CLUSTER_LABELS --titles=$DOCUMENT_TITLES --K=$K --J=$J |& tee $LOG_FILE
#        done
#    fi
#done





