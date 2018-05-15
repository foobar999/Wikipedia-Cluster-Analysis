#!/bin/bash -e

if (( $# != 1 )); then
    echo "Usage: $0 CONFIG"
    exit 1
fi
unset DEBUG
CONFIG=$1
source $CONFIG

CONTRIB_PREFIX=output/contribs/$PREFIX
STATS_PREFIX=output/stats/$PREFIX

CONTRIB_VALUES=($CONTRIB_VALUES) # splitte String zu Array
echo "CONTRIB_VALUES ${CONTRIB_VALUES[@]}"


QUANTILE=0.95
for CONTRIB_VALUE in "${CONTRIB_VALUES[@]}"; do
    ACC_CONTRIBS=$CONTRIB_PREFIX-$CONTRIB_VALUE-acc-contribs.mm.bz2
    IMG_PREFIX=$STATS_PREFIX-$CONTRIB_VALUE-contribs
    echo "visualising stats from $ACC_CONTRIBS to oprefix $IMG_PREFIX"
    python scripts/get_contribs_stats.py --acc-contribs=$ACC_CONTRIBS --img-prefix=$IMG_PREFIX --quantile-order=$QUANTILE
done