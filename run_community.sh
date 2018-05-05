#!/bin/bash -e

# TODO titel nich pickeln, sondern als komprimiertes json speichern oder so
# TODO index files weg
# TODO pageid-basierte Filterung mit titel-basierter filterung vergleichen
# TODO per if-abfrage prüfen, ob pageid bereits vorhanden?

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
echo "KEEP_MAX_EDGES $KEEP_MAX_EDGES"
if [ ! -z ${DEBUG+x} ]; then    # variable gesetzt?
    export DEBUG=$DEBUG
fi

CONTRIB_VALUES=(one diff_numterms)
COAUTH_MODES=(mul jac)
for CONTRIB_VALUE in "${CONTRIB_VALUES[@]}"; do
    ./bash/run_history_to_contribs.sh $PREFIX $CONTRIB_VALUE $TOP_N_CONTRIBS
    CPREFIX=$PREFIX-$CONTRIB_VALUE
    for COAUTH_MODE in "${COAUTH_MODES[@]}"; do 
        ./bash/run_contribs_to_graph.sh $CPREFIX $COAUTH_MODE $KEEP_MAX_EDGES
    done
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