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

TOPIC_MODELS=($TOPIC_MODELS) # splitte String zu Array
echo "TOPIC_MODELS ${TOPIC_MODELS[@]}"
CLUSTER_METHODS=($CLUSTER_METHODS)
echo "CLUSTER_METHODS ${CLUSTER_METHODS[@]}"
CLUSTER_NUMS=($CLUSTER_NUMS) 
echo "CLUSTER_NUMS ${CLUSTER_NUMS[@]}"
CONTRIB_VALUES=($CONTRIB_VALUES)
echo "CONTRIB_VALUES ${CONTRIB_VALUES[@]}"
COAUTH_MODES=($COAUTH_MODES)
echo "COAUTH_MODES ${COAUTH_MODES[@]}"
COMM_METHODS=($COMM_METHODS)
echo "COMM_METHODS ${COMM_METHODS[@]}"
COMP_MEASURES=($COMP_MEASURES)
echo "COMP_MEASURES ${COMP_MEASURES[@]}"

mkdir -p output/comparisons
COMP_PREFIX=output/comparisons/$PREFIX

echo "clearing score files of scores ${COMP_MEASURES[@]}"
for COMP_MEASURE in "${COMP_MEASURES[@]}"; do 
    SCORE_FILE=$COMP_PREFIX-$COMP_MEASURE.txt
    truncate -s 0 $SCORE_FILE
done

for TOPIC_MODEL in "${TOPIC_MODELS[@]}"; do
    for CLUSTER_METHOD in "${CLUSTER_METHODS[@]}"; do
        for CLUSTER_NUM in "${CLUSTER_NUMS[@]}"; do
            CLUS_PARAMS=$TOPIC_MODEL-$CLUSTER_METHOD-$CLUSTER_NUM
            CLUS_PREFIX=$PREFIX-$CLUS_PARAMS
            # Clustering Dokumenttitel -> Clusterlabel
            TITLECLUSTERS=output/clusters/$CLUS_PREFIX-titleclusters.json.bz2
            for CONTRIB_VALUE in "${CONTRIB_VALUES[@]}"; do
                for COAUTH_MODE in "${COAUTH_MODES[@]}"; do 
                    for COMM_METHOD in "${COMM_METHODS[@]}"; do 
                        COMM_PARAMS=$CONTRIB_VALUE-$COAUTH_MODE-$COMM_METHOD
                        COMM_PREFIX=$PREFIX-$COMM_PARAMS
                        # Communities Dokumenttitel -> Communitylabel
                        TITLECOMMUNITIES=output/communities/$COMM_PREFIX-titlecommunities.json.bz2
                        echo "comparing $CLUS_PARAMS and $COMM_PARAMS"
                        #COMP_FILE=$COMP_PREFIX-$TOPIC_MODEL-$CLUSTER_METHOD-$CLUSTER_NUM-$CONTRIB_VALUE-$COAUTH_MODE-$COMM_METHOD
                        OUTPUT=$(python scripts/compare_title_clusterings.py --clusterings $TITLECLUSTERS $TITLECOMMUNITIES)
                        for COMP_MEASURE in "${COMP_MEASURES[@]}"; do 
                            SCORE="$(echo "${OUTPUT}" | grep $COMP_MEASURE | cut -d' ' -f2-)"
                            SCORE_FILE=$COMP_PREFIX-$COMP_MEASURE.txt
                            LINE="$CLUS_PARAMS $COMM_PARAMS $SCORE"
                            echo $LINE >> $SCORE_FILE # schreibe je Zeile: <Clusteringparameter> <Communitiesparameter> <Ähnlichkeitsscore>
                        done
                    done
                done
            done
        done
    done
done













