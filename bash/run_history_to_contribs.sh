#!/bin/bash -e

if (( $# != 3 )); then
    echo "Usage: $0 IPREFIX CONTRIBUTION_VALUE TOP_N_CONTRIBS"
    exit 1
fi
IPREFIX=$1
CONTRIBUTION_VALUE=$2
TOP_N_CONTRIBS=$3
OPREFIX=$IPREFIX-$CONTRIBUTION_VALUE

COLL_PREFIX=collections/$IPREFIX
mkdir -p output/contribs
CONTRIB_PREFIX=output/contribs/$OPREFIX
mkdir -p output/graph
GRAPH_PREFIX=output/graph/$OPREFIX
mkdir -p output/logs
LOG_PREFIX=output/logs/$OPREFIX

NAMESPACE_PREFIXES=output/$IPREFIX-namespaces.txt
HISTORY=$COLL_PREFIX-pages-meta-history.xml
ID2AUTHOR=$CONTRIB_PREFIX-id2author.txt
RAW_CONTRIBS=$CONTRIB_PREFIX-raw-contribs.mm
TITLES=$CONTRIB_PREFIX-titles.json
ACC_CONTRIBS=$CONTRIB_PREFIX-acc-contribs.mm

BIPARTITE_GRAPH=$GRAPH_PREFIX-doc-auth-bipartite.graph

LOG_CONTRIBS=$LOG_PREFIX-contribs.log

#echo "extracting likely namespaces from XML dump"
#NS_MIN_OCCURENCES=1
#( time ./bash/get_likely_namespaces.sh $HISTORY.bz2 $NS_MIN_OCCURENCES | tee $NAMESPACE_PREFIXES )|& tee $LOG_PREFIX-namespaces.log

# TODO wieder rein
echo "computing author contributions"
( time python3 scripts/history_to_contribs.py --history-dump=$HISTORY.bz2 --id2author=$ID2AUTHOR.bz2 --contribs=$RAW_CONTRIBS --contribution-value=$CONTRIBUTION_VALUE --namespace-prefixes=$NAMESPACE_PREFIXES ) |& tee $LOG_CONTRIBS
python3 ./scripts/utils/binary_to_text.py pickle $RAW_CONTRIBS.metadata.cpickle $TITLES # Dokumenttitel-Datei zu JSON konvertierne & umbenennen
rm -f $RAW_CONTRIBS.metadata.cpickle # gepickelte Dokumenttitel-Datei entfernen
bzip2 -zf $RAW_CONTRIBS $TITLES # komprimiere Beiträge, Artikeltitel

# TODO wieder rein
echo "accmulating contributions"
( time python3 scripts/accumulate_contribs.py --raw-contribs=$RAW_CONTRIBS.bz2 --acc-contribs=$ACC_CONTRIBS ) |& tee -a $LOG_CONTRIBS
bzip2 -zf $ACC_CONTRIBS # komprimiere kumulierte Beiträge

echo "creating bipartite graph from contributions"
( time python3 scripts/contribs_to_bipart_graph.py --contribs=$ACC_CONTRIBS.bz2 --bipart-graph=$BIPARTITE_GRAPH.bz2 --top-n-contribs=$TOP_N_CONTRIBS) |& tee  -a $LOG_CONTRIBS























