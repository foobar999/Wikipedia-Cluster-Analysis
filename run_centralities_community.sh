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

CONTRIB_PREFIX=output/contribs/$PREFIX
GRAPH_PREFIX=output/graph/$PREFIX
COMM_PREFIX=output/communities/$PREFIX

CONTRIB_VALUES=($CONTRIB_VALUES)
echo "CONTRIB_VALUES ${CONTRIB_VALUES[@]}"
COAUTH_MODES=($COAUTH_MODES)
echo "COAUTH_MODES ${COAUTH_MODES[@]}"


# bestimme von allen Communities die zentralsten Dokumente mit ihren Titel
CENTRAL_DOCS_STATS_DIR=output/stats/community_central_documents
mkdir -p $CENTRAL_DOCS_STATS_DIR
CENTRAL_DOCS_STATS_PREFIX=$CENTRAL_DOCS_STATS_DIR/$PREFIX
MAX_DOCS_PER_COMM=5 # maximale Anzahl der berücksichtigten, zentralsten Dokumente je Community
COMM_METHOD="louvain"
CENTRALITY_MEASURE="weighted_closeness"
echo "calculating most central documents of each community"
for CONTRIB_VALUE in "${CONTRIB_VALUES[@]}"; do
    TITLES=$CONTRIB_PREFIX-$CONTRIB_VALUE-titles.json.bz2
    for COAUTH_MODE in "${COAUTH_MODES[@]}"; do
        COAUTH_GRAPH=$GRAPH_PREFIX-$CONTRIB_VALUE-$COAUTH_MODE-coauth.graph.gz
        COMM=$COMM_PREFIX-$CONTRIB_VALUE-$COAUTH_MODE-$COMM_METHOD-communities.json.bz2
        LOG_CENTRALITY_DATA=$CENTRAL_DOCS_STATS_PREFIX-$CONTRIB_VALUE-$COAUTH_MODE-$COMM_METHOD-centralities.log
        CENTRALITY_DATA=$CENTRAL_DOCS_STATS_PREFIX-$CONTRIB_VALUE-$COAUTH_MODE-$COMM_METHOD-$CENTRALITY_MEASURE-centralities.json
        python3 -m scripts.stats.community.get_community_central_documents --coauth-graph=$COAUTH_GRAPH --communities=$COMM --titles=$TITLES --max-docs-per-com=$MAX_DOCS_PER_COMM --centrality-measure=$CENTRALITY_MEASURE --centrality-data=$CENTRALITY_DATA |& tee $LOG_CENTRALITY_DATA
        bzip2 -zf $CENTRALITY_DATA
    done
done 

# zeige von ausgewählten, äquidistanten Communities die zentralsten Titel an
CENTRAL_DOCS_SAMPLE_STATS_DIR=output/stats/community_central_documents_sample
mkdir -p $CENTRAL_DOCS_SAMPLE_STATS_DIR
CENTRAL_DOCS_SAMPLE_STATS_PREFIX=$CENTRAL_DOCS_SAMPLE_STATS_DIR/$PREFIX
NUM_SAMPLE_COMMUNITIES=5 # maximale Anzahl angezeigter Communities
COMM_METHOD="louvain"
CENTRALITY_MEASURE="weighted_closeness"
echo "determining most central documents of sample communities"
for CONTRIB_VALUE in "${CONTRIB_VALUES[@]}"; do
    for COAUTH_MODE in "${COAUTH_MODES[@]}"; do
        CENTRALITY_DATA=$CENTRAL_DOCS_STATS_PREFIX-$CONTRIB_VALUE-$COAUTH_MODE-$COMM_METHOD-$CENTRALITY_MEASURE-centralities.json.bz2
        LOG_SAMPLES=$CENTRAL_DOCS_SAMPLE_STATS_PREFIX-$CONTRIB_VALUE-$COAUTH_MODE-$COMM_METHOD-$CENTRALITY_MEASURE-sample-titles.log
        python3 -m scripts.stats.get_sample_central_titles --centrality-data=$CENTRALITY_DATA --num-parts=$NUM_SAMPLE_COMMUNITIES |& tee $LOG_SAMPLES
    done
done 
