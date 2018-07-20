#!/bin/bash -e

if (( $# != 2 )); then
    echo "Usage: $0 IPREFIX COAUTH_MODE"
    exit 1
fi
IPREFIX=$1
COAUTH_MODE=$2
OPREFIX=$IPREFIX-$COAUTH_MODE

IGRAPH_PREFIX=output/graph/$IPREFIX
OGRAPH_PREFIX=output/graph/$OPREFIX
LOG_PREFIX=output/logs/$OPREFIX

BIPARTITE_GRAPH=$IGRAPH_PREFIX-doc-auth-bipartite.graph
COAUTH_GRAPH=$OGRAPH_PREFIX-coauth.graph

LOG_GRAPH=$LOG_PREFIX-graph.log

echo "creating co-authorship graph from bipartite graph"
(time python3 -m scripts.community.bipart_to_coauth_graph --bipart-graph=$BIPARTITE_GRAPH.bz2 --coauth-graph=$COAUTH_GRAPH.bz2 --mode=$COAUTH_MODE) |& tee $LOG_GRAPH

echo "converting networkx bz2 graph to igraph gz graph"
(time python3 -m scripts.community.nwx_to_igraph --nwx=$COAUTH_GRAPH.bz2 --igraph=$COAUTH_GRAPH.gz) |& tee -a $LOG_GRAPH
rm -f $COAUTH_GRAPH.bz2





