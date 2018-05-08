#!/bin/bash -e

# TODO ich sollte das mit der max. komponente eher machen
# TODO normierung raus, da winzige werte und newman eh nicht normiert?

if (( $# != 1 )); then
    echo "Usage: $0 CONFIG"
    exit 1
fi
unset DEBUG
CONFIG=$1
source $CONFIG

echo "PREFIX $PREFIX"
echo "DEBUG $DEBUG"
CONTRIB_VALUES=($CONTRIB_VALUES) # splitte String zu Array
echo "CONTRIB_VALUES ${CONTRIB_VALUES[@]}"
echo "TOP_N_CONTRIBS $TOP_N_CONTRIBS"
COAUTH_MODES=($COAUTH_MODES)
echo "COAUTH_MODES ${COAUTH_MODES[@]}"
echo "KEEP_MAX_EDGES $KEEP_MAX_EDGES"
COMM_METHODS=($COMM_METHODS)
echo "COMM_METHODS ${COMM_METHODS[@]}"
echo "USE_GIANT_COMP $USE_GIANT_COMP"
if [ ! -z ${DEBUG+x} ]; then    # variable gesetzt?
    export DEBUG=$DEBUG
fi

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


##CONTRIB_VALUES=(one diff_numterms)
#CONTRIB_VALUES=(one )
#COAUTH_MODES=(mul jac coll)
##COMM_METHODS=(greedy louvain)
#COMM_METHODS=(louvain)
