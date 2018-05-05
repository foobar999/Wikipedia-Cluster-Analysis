#!/bin/bash -e

if (( $# != 2 )); then
    echo "Usage: $0 IPREFIX COAUTH_MODE"
    exit 1
fi
IPREFIX=$1
COAUTH_MODE=$2
OPREFIX=$IPREFIX-$COAUTH_MODE

mkdir -p output/contribs
CONTRIB_PREFIX=output/contribs/$IPREFIX
mkdir -p output/graph
GRAPH_PREFIX=output/graph/$OPREFIX
mkdir -p output/logs
LOG_PREFIX=output/logs/$OPREFIX

PRUNED_CONTRIBS=$CONTRIB_PREFIX-pruned-contribs.mm

BIPARTITE_GRAPH=$GRAPH_PREFIX-doc-auth-bipartite.graph
COAUTH_GRAPH=$GRAPH_PREFIX-coauth.graph

LOG_GRAPH=$LOG_PREFIX-graph.log

echo "creating bipartite graph from contributions"
WEIGHTED=y
( time python scripts/contribs_to_bipart_graph.py --contribs=$PRUNED_CONTRIBS.bz2 --bipart-graph=$BIPARTITE_GRAPH.gz --weighted=$WEIGHTED) |& tee $LOG_GRAPH

echo "creating co-authorship graph from bipartite graph"
KEEP_MAX_EDGES=1000000
(time python scripts/bipart_to_coauth_graph.py --bipart-graph=$BIPARTITE_GRAPH.gz --coauth-graph=$COAUTH_GRAPH.gz --mode=$COAUTH_MODE --keep-max-edges=$KEEP_MAX_EDGES) |& tee -a $LOG_GRAPH







