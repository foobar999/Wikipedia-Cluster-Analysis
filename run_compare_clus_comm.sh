#!/bin/bash -e

# TODO sklearn benutzt ln statt log2 !!!

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

# zu vergleichende Parametrierungen
# Cluster-Parameter
BEST_CLUSTER_METHODS=($BEST_CLUSTER_METHODS)
echo "BEST_CLUSTER_METHODS ${BEST_CLUSTER_METHODS[@]}"
BEST_CLUSTER_NUMS=($BEST_CLUSTER_NUMS) 
echo "BEST_CLUSTER_NUMS ${BEST_CLUSTER_NUMS[@]}"
# Community-Parameter
BEST_COMM_CONTRIBS=($BEST_COMM_CONTRIBS)
echo "BEST_COMM_CONTRIBS ${BEST_COMM_CONTRIBS[@]}"
BEST_COMM_COAUTHS=($BEST_COMM_COAUTHS)
echo "BEST_COMM_COAUTHS ${BEST_COMM_COAUTHS[@]}"
BEST_COMM_METHODS=($BEST_COMM_METHODS)
echo "BEST_COMM_METHODS ${BEST_COMM_METHODS[@]}"

# Präfixe benötigter Dateien
CLUS_PREFIX=output/clusters/$PREFIX
COMM_PREFIX=output/communities/$PREFIX

# Verzeichnisse der zuvor berechneten Centrality-Daten
CLUS_CENTRAL_DOCS_STATS_DIR=output/stats/cluster_central_documents
CLUS_CENTRAL_DOCS_STATS_PREFIX=$CLUS_CENTRAL_DOCS_STATS_DIR/$PREFIX
COMM_CENTRAL_DOCS_STATS_DIR=output/stats/community_central_documents
COMM_CENTRAL_DOCS_STATS_PREFIX=$COMM_CENTRAL_DOCS_STATS_DIR/$PREFIX

# Verzeichnis für Vergleichsscores
STATS_COMP_SCORES_DIR=output/stats/comparisons_scores
mkdir -p $STATS_COMP_SCORES_DIR
STATS_COMP_SCORES_PREFIX=$STATS_COMP_SCORES_DIR/$PREFIX

# Verzeichnis für Centrality-Titel-Vergleiche
STATS_COMP_CENTRALITY_DIR=output/stats/comparisons_centrality
mkdir -p $STATS_COMP_CENTRALITY_DIR
STATS_COMP_CENTRALITY_PREFIX=$STATS_COMP_CENTRALITY_DIR/$PREFIX

# initialisiere leeres "score file", in dem nmi,#gemeinsamer cluster in kurzform enthalten
COMP_MEASURE=normalized-mutual-info
echo "clearing score files of scores $COMP_MEASURE"
SCORE_FILE=$STATS_COMP_SCORES_PREFIX-$COMP_MEASURE.txt
echo "CLUSTER_PARAMS COMMUNIITY_PARAMS SCORE INTERSECTION_SIZE" > $SCORE_FILE

for CLUS_INDEX in ${!BEST_CLUSTER_METHODS[*]}; do 

    # Clustering
    CLUSTER_METHOD=${BEST_CLUSTER_METHODS[$CLUS_INDEX]}
    CLUSTER_NUM=${BEST_CLUSTER_NUMS[$CLUS_INDEX]}
    CLUSTER_PARAMS=lda-$CLUSTER_METHOD-$CLUSTER_NUM
    TITLECLUSTERS=$CLUS_PREFIX-$CLUSTER_PARAMS-titleclusters.json.bz2
    CLUS_CENTRALITY_DATA=$CLUS_CENTRAL_DOCS_STATS_PREFIX-$CLUSTER_METHOD-$CLUSTER_NUM-centralities.json.bz2
    
    for COMM_INDEX in ${!BEST_COMM_CONTRIBS[*]}; do 
    
        # Communitystruktur
        CONTRIB_VALUE=${BEST_COMM_CONTRIBS[$COMM_INDEX]}
        COAUTH_MODE=${BEST_COMM_COAUTHS[$COMM_INDEX]}
        COMM_METHOD=${BEST_COMM_METHODS[$COMM_INDEX]}
        COMM_PARAMS=$CONTRIB_VALUE-$COAUTH_MODE-$COMM_METHOD
        TITLECOMMUNITIES=$COMM_PREFIX-$COMM_PARAMS-titlecommunities.json.bz2
        COMM_CENTRALITY_DATA=$COMM_CENTRAL_DOCS_STATS_PREFIX-$COMM_PARAMS-weighted_closeness-centralities.json.bz2
        
        echo "comparing $CLUSTER_PARAMS and $COMM_PARAMS"
        
        # Berechnung Ähnlichkeitsscores
        LOG_FILE=$STATS_COMP_SCORES_PREFIX-$CLUSTER_PARAMS-$COMM_PARAMS.log
        OUTPUT=$(python3 -m scripts.stats.compare_title_clusterings --clusterings $TITLECLUSTERS $TITLECOMMUNITIES 2>&1)
        echo "$OUTPUT" |& tee $LOG_FILE # schreibe in Logdatei
        SCORE="$(echo "$OUTPUT" | grep $COMP_MEASURE | cut -d' ' -f7-)" # speichere Score
        INTERSECT_SIZE="$(echo "$OUTPUT" | grep "number of intersect" | cut -d' ' -f10-)" # speichere Größe der Schnittmenge beider Partitionierungen
        LINE="$CLUSTER_PARAMS $COMM_PARAMS $SCORE $INTERSECT_SIZE"
        echo $LINE >> $SCORE_FILE # schreibe je Zeile: <Clusteringparameter> <Communitiesparameter> <Ähnlichkeitsscore>
        
        # Vergleich Ähnlichkeiten mittels zentraler Titel
        NUM_SAMPLE_CLUSTERS=5
        COMP_CENTRALITY_LOG_FILE=$STATS_COMP_CENTRALITY_PREFIX-$CLUSTER_PARAMS-$COMM_PARAMS-centrality-cmp.log
        python3 -m scripts.stats.find_similar_counterpart_clusterings --title-clusterings $TITLECLUSTERS $TITLECOMMUNITIES --centrality-data $CLUS_CENTRALITY_DATA $COMM_CENTRALITY_DATA --num-sample-clusters=$NUM_SAMPLE_CLUSTERS |& tee $COMP_CENTRALITY_LOG_FILE
    done
done








