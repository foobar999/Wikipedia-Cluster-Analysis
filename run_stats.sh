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
STATS_PREFIX=output/stats/$PREFIX

CONTRIB_VALUES=($CONTRIB_VALUES) # splitte String zu Array
echo "CONTRIB_VALUES ${CONTRIB_VALUES[@]}"

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

 
