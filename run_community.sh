#!/bin/bash -e

# TODO titel nich pickeln, sondern als komprimiertes json speichern oder so

if (( $# != 1 )); then
    echo "Usage: $0 PREFIX"
    exit 1
fi
PREFIX=$1
unset DEBUG

CONTRIB_VALUES=(one diff_numterms)
BIPART_MODES=(mul jac)
for CONTRIB_VALUE in "${CONTRIB_VALUES[@]}"; do
    ./run_history_to_contribs.sh $PREFIX $CONTRIB_VALUE
    #CPREFIX=$PREFIX-$CONTRIB_VALUE
    #for BIPART_MODE in "${BIPART_MODES[@]}"; do 
    #    ./slave2.sh $CPREFIX $BIPART_MODE
    #done
done

