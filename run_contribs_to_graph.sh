#!/bin/bash -e

if (( $# != 1 )); then
    echo "Usage: $0 PREFIX"
    exit 1
fi
PREFIX=$1
unset DEBUG

mkdir -p output/contribs
CONTRIB_PREFIX=output/contribs/$PREFIX
mkdir -p output/graph
GRAPH_PREFIX=output/graph/$PREFIX
mkdir -p output/logs
LOG_PREFIX=output/logs/$PREFIX

DOC_AUTH_CONTRIBS=$CONTRIB_PREFIX-doc-auth-contribs.mm

BIPARTITE_GRAPH=$GRAPH_PREFIX-doc-auth-bipartite.graph
COAUTH_GRAPH=$GRAPH_PREFIX-coauth.graph

LOG_CONTRIBS=$LOG_PREFIX-contribs.log
LOG_GRAPH=$LOG_PREFIX-graph.log

echo "creating bipartite graph from contributions"
WEIGHTED=y
( time python scripts/contribs_to_bipart_graph.py --contribs=$DOC_AUTH_CONTRIBS.bz2 --bipart-graph=$BIPARTITE_GRAPH.gz --weighted=$WEIGHTED) |& tee $LOG_GRAPH

echo "creating co-authorship graph from bipartite graph"
MODE=mul
KEEP_MAX_EDGES=2000000
(time python scripts/bipart_to_coauth_graph.py --bipart-graph=$BIPARTITE_GRAPH.gz --coauth-graph=$COAUTH_GRAPH.gz --mode=$MODE --keep-max-edges=$KEEP_MAX_EDGES) |& tee -a $LOG_GRAPH







