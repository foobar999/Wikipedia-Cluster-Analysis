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

BEST_CLUSTER_METHODS=($BEST_CLUSTER_METHODS)
echo "BEST_CLUSTER_METHODS ${BEST_CLUSTER_METHODS[@]}"
BEST_CLUSTER_NUMS=($BEST_CLUSTER_NUMS) 
echo "BEST_CLUSTER_NUMS ${BEST_CLUSTER_NUMS[@]}"
BEST_COMM_CONTRIBS=($BEST_COMM_CONTRIBS)
echo "BEST_COMM_CONTRIBS ${BEST_COMM_CONTRIBS[@]}"
BEST_COMM_COAUTHS=($BEST_COMM_COAUTHS)
echo "BEST_COMM_COAUTHS ${BEST_COMM_COAUTHS[@]}"
BEST_COMM_METHODS=($BEST_COMM_METHODS)
echo "BEST_COMM_METHODS ${BEST_COMM_METHODS[@]}"

CLUS_PREFIX=output/clusters/$PREFIX
COMM_PREFIX=output/communities/$PREFIX
mkdir -p output/logs/comparisons
LOG_PREFIX=output/logs/comparisons/$PREFIX

STATS_COMP_DIR=output/stats/comparisons
mkdir -p $STATS_COMP_DIR
STATS_COMP_PREFIX=$STATS_COMP_DIR/$PREFIX

COMP_MEASURE=normalized-mutual-info
echo "clearing score files of scores $COMP_MEASURE"
SCORE_FILE=$STATS_COMP_PREFIX-$COMP_MEASURE.txt
truncate -s 0 $SCORE_FILE

for CLUS_INDEX in ${!BEST_CLUSTER_METHODS[*]}; do 
    # Clustering
    CLUSTER_METHOD=${BEST_CLUSTER_METHODS[$CLUS_INDEX]}
    CLUSTER_NUM=${BEST_CLUSTER_NUMS[$CLUS_INDEX]}
    CLUSTER_PARAMS=lda-$CLUSTER_METHOD-$CLUSTER_NUM
    TITLECLUSTERS=$CLUS_PREFIX-$CLUSTER_PARAMS-titleclusters.json.bz2
    for COMM_INDEX in ${!BEST_COMM_CONTRIBS[*]}; do 
        # Communitystruktur
        CONTRIB_VALUE=${BEST_COMM_CONTRIBS[$COMM_INDEX]}
        COAUTH_MODE=${BEST_COMM_COAUTHS[$COMM_INDEX]}
        COMM_METHOD=${BEST_COMM_METHODS[$COMM_INDEX]}
        COMM_PARAMS=$CONTRIB_VALUE-$COAUTH_MODE-$COMM_METHOD
        TITLECOMMUNITIES=$COMM_PREFIX-$COMM_PARAMS-titlecommunities.json.bz2
        
        # Vergleich
        echo "comparing $CLUSTER_PARAMS and $COMM_PARAMS"
        LOG_FILE=$LOG_PREFIX-$CLUSTER_PARAMS-$COMM_PARAMS.log
        OUTPUT=$(python3 -m scripts.stats.compare_title_clusterings --clusterings $TITLECLUSTERS $TITLECOMMUNITIES 2>&1)
        echo "$OUTPUT" |& tee $LOG_FILE # schreibe in Logdatei
        SCORE="$(echo "$OUTPUT" | grep $COMP_MEASURE | cut -d' ' -f6-)" # speichere Score
        INTERSECT_SIZE="$(echo "$OUTPUT" | grep "number of intersect" | cut -d' ' -f6-)" # speichere Größe der Schnittmenge beider Partitionierungen
        LINE="$CLUS_PARAMS $COMM_PARAMS $SCORE $INTERSECT_SIZE"
        echo $LINE >> $SCORE_FILE # schreibe je Zeile: <Clusteringparameter> <Communitiesparameter> <Ähnlichkeitsscore>
    done
done








