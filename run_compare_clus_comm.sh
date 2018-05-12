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

for TOPIC_MODEL in "${TOPIC_MODELS[@]}"; do
    for CLUSTER_METHOD in "${CLUSTER_METHODS[@]}"; do
        for CLUSTER_NUM in "${CLUSTER_NUMS[@]}"; do
            CLUS_PREFIX=$PREFIX-$TOPIC_MODEL-$CLUSTER_METHOD-$CLUSTER_NUM
            # Clustering Dokumenttitel -> Clusterlabel
            TITLECLUSTERS=output/clusters/$COMM_METHOD-titleclusters.json.bz2
            for CONTRIB_VALUE in "${CONTRIB_VALUES[@]}"; do
                for COAUTH_MODE in "${COAUTH_MODES[@]}"; do 
                    for COMM_METHOD in "${COMM_METHODS[@]}"; do 
                        COMM_PREFIX=$PREFIX-$CONTRIB_VALUE-$COAUTH_MODE-$COMM_METHOD
                        # Communities Dokumenttitel -> Communitylabel
                        TITLECOMMUNITIES=output/communities/$COMM_PREFIX-titlecommunities.json.bz2
                        echo "comparing $TCC_TITLECLUSTERS and $TITLECOMMUNITIES"
                    done
                done
            done
        done
    done
done













