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

echo "computing author contributions"
( time python3 -m scripts.community.history_to_contribs --history-dump=$HISTORY.bz2 --id2author=$ID2AUTHOR.bz2 --contribs=$RAW_CONTRIBS --contribution-value=$CONTRIBUTION_VALUE --namespace-prefixes=$NAMESPACE_PREFIXES ) |& tee $LOG_CONTRIBS

echo "creating JSON docid->doctitle mapping file"
python3 -m scripts.utils.metadata_to_doc_id_titles --metadata=$RAW_CONTRIBS.metadata.cpickle --titles=$TITLES
rm -f $RAW_CONTRIBS.metadata.cpickle # gepickelte Dokumenttitel-Datei entfernen
bzip2 -zf $RAW_CONTRIBS $TITLES # komprimiere Beiträge, Artikeltitel

echo "accmulating contributions"
( time python3 -m scripts.community.accumulate_contribs --raw-contribs=$RAW_CONTRIBS.bz2 --acc-contribs=$ACC_CONTRIBS ) |& tee -a $LOG_CONTRIBS
bzip2 -zf $ACC_CONTRIBS 

echo "creating bipartite graph from contributions"
( time python3 -m scripts.community.contribs_to_bipart_graph --contribs=$ACC_CONTRIBS.bz2 --bipart-graph=$BIPARTITE_GRAPH.bz2 --top-n-contribs=$TOP_N_CONTRIBS) |& tee  -a $LOG_CONTRIBS























