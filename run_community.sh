#!/bin/bash -e

# TODO titel nich pickeln, sondern als komprimiertes json speichern oder so
# TODO index files weg

if (( $# != 1 )); then
    echo "Usage: $0 CONFIG"
    exit 1
fi
unset DEBUG
CONFIG=$1
source $CONFIG

echo "PREFIX $PREFIX"
echo "DEBUG $DEBUG"
echo "TOP_N_CONTRIBS $TOP_N_CONTRIBS"
if [ ! -z ${DEBUG+x} ]; then    # variable gesetzt?
    export DEBUG=$DEBUG
fi

CONTRIB_VALUES=(one diff_numterms)
BIPART_MODES=(mul jac)
for CONTRIB_VALUE in "${CONTRIB_VALUES[@]}"; do
    ./run_history_to_contribs.sh $PREFIX $CONTRIB_VALUE $TOP_N_CONTRIBS
    #CPREFIX=$PREFIX-$CONTRIB_VALUE
    #for BIPART_MODE in "${BIPART_MODES[@]}"; do 
    #    ./slave2.sh $CPREFIX $BIPART_MODE
    #done
done



# test_parameter_set () {
    # PARAMETER=$1
    # REQUIRED=$2
    # if [ -z "$PARAMETER" ]; then
        # echo "$PARAMETER is unset"
        # if [ "$REQUIRED" = "required" ]; then
            # echo "$PARAMETER is required -> aborting"
            # exit 1
        # fi
    # else 
        # echo "$PARAMETER is set to ${!PARAMETER}"
    # fi
# }

#test_parameter_set TOP_N_CONTRIBS required
#test_parameter_set DEBUG required