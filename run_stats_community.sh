#!/bin/bash -e

if (( $# != 1 )); then
    echo "Usage: $0 CONFIG"
    exit 1
fi
unset DEBUG
CONFIG=$1
source $CONFIG

CONTRIB_PREFIX=output/contribs/$PREFIX
GRAPH_PREFIX=output/graph/$PREFIX
COMM_PREFIX=output/communities/$PREFIX
STATS_PREFIX=output/stats/$PREFIX

CONTRIB_VALUES=($CONTRIB_VALUES)
echo "CONTRIB_VALUES ${CONTRIB_VALUES[@]}"
COAUTH_MODES=($COAUTH_MODES)
echo "COAUTH_MODES ${COAUTH_MODES[@]}"
COMM_METHODS=($COMM_METHODS)
echo "COMM_METHODS ${COMM_METHODS[@]}"


QUANTILE=0.95
for CONTRIB_VALUE in "${CONTRIB_VALUES[@]}"; do
    ACC_CONTRIBS=$CONTRIB_PREFIX-$CONTRIB_VALUE-acc-contribs.mm.bz2
    IMG_PREFIX=$STATS_PREFIX-$CONTRIB_VALUE-contribs
    echo "visualising stats from $ACC_CONTRIBS to oprefix $IMG_PREFIX"
    python3 scripts/get_contribs_stats.py --acc-contribs=$ACC_CONTRIBS --img-prefix=$IMG_PREFIX --quantile-order=$QUANTILE
done

QUANTILE=0.99
for CONTRIB_VALUE in "${CONTRIB_VALUES[@]}"; do
    # beschränkung hier auf "mul", da eh immer das gleiche
    COAUTH_MODE=mul
    GRAPH_FILE=$GRAPH_PREFIX-$CONTRIB_VALUE-$COAUTH_MODE-coauth.graph.gz
    IMG_FILE=$STATS_PREFIX-$CONTRIB_VALUE-$COAUTH_MODE-components.pdf
    echo "visualising stats from $ACC_CONTRIBS to oprefix $IMG_PREFIX"
    python3 scripts/get_graph_comp_stats.py --graph=$GRAPH_FILE --img=$IMG_FILE --quantile-order=$QUANTILE
done

for CONTRIB_VALUE in "${CONTRIB_VALUES[@]}"; do
    for COAUTH_MODE in "${COAUTH_MODES[@]}"; do
        for COMM_METHOD in "${COMM_METHODS[@]}"; do
            COMM_FILE=$COMM_PREFIX-$CONTRIB_VALUE-$COAUTH_MODE-$COMM_METHOD-communities.json.bz2
            IMG_FILE=$STATS_PREFIX-$CONTRIB_VALUE-$COAUTH_MODE-$COMM_METHOD-community-sizes.pdf
            python3 scripts/get_community_stats.py --communities=$COMM_FILE --img=$IMG_FILE
        done
    done
done

NUM_COMMS_EQUIDIST=5
NUM_MAX_CEN_NODES_PER_COMM=5
COMM_METHOD="louvain"
echo "calculating centrality stats"
for CONTRIB_VALUE in "${CONTRIB_VALUES[@]}"; do
    TITLES=$CONTRIB_PREFIX-$CONTRIB_VALUE-titles.json.bz2
    for COAUTH_MODE in "${COAUTH_MODES[@]}"; do
        COAUTH_GRAPH=$GRAPH_PREFIX-$CONTRIB_VALUE-$COAUTH_MODE-coauth.graph.gz
        COMM=$COMM_PREFIX-$CONTRIB_VALUE-$COAUTH_MODE-$COMM_METHOD-communities.json.bz2
        LOG_CENTRALITIES=$STATS_PREFIX-$CONTRIB_VALUE-$COAUTH_MODE-$COMM_METHOD-centralities.log
        python3 scripts/get_community_centrality_stats.py --coauth-graph=$COAUTH_GRAPH --communities=$COMM --titles=$TITLES --K=$NUM_COMMS_EQUIDIST --J=$NUM_MAX_CEN_NODES_PER_COMM |& tee $LOG_CENTRALITIES
    done
done 


