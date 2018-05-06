#!/bin/bash -e

# TODO titles
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
echo "USE_GIANT_COMP $USE_GIANT_COMP"
if [ ! -z ${DEBUG+x} ]; then    # variable gesetzt?
    export DEBUG=$DEBUG
fi

CONTRIB_VALUES=(one diff_numterms)
COAUTH_MODES=(mul jac)
COMM_METHODS=(greedy louvain)
for CONTRIB_VALUE in "${CONTRIB_VALUES[@]}"; do
    ./bash/run_history_to_contribs.sh $PREFIX $CONTRIB_VALUE $TOP_N_CONTRIBS
    CPREFIX=$PREFIX-$CONTRIB_VALUE
    TITLES=output/contribs/$CPREFIX-titles.json.bz2
    for COAUTH_MODE in "${COAUTH_MODES[@]}"; do 
        ./bash/run_contribs_to_graph.sh $CPREFIX $COAUTH_MODE $KEEP_MAX_EDGES
        CGPREFIX=$CPREFIX-$COAUTH_MODE
        for COMM_METHOD in "${COMM_METHODS[@]}"; do 
            ./bash/run_graph_to_community.sh $CGPREFIX $COMM_METHOD $USE_GIANT_COMP $TITLES
        done
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