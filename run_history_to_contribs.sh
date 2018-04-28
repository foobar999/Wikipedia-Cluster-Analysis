#!/bin/bash -e

if (( $# != 1 )); then
    echo "Usage: $0 PREFIX"
    exit 1
fi
PREFIX=$1
unset DEBUG

COLL_PREFIX=collections/$PREFIX
mkdir -p output/contribs
CONTRIB_PREFIX=output/contribs/$PREFIX
mkdir -p output/graph
GRAPH_PREFIX=output/graph/$PREFIX
mkdir -p output/stats
STATS_PREFIX=output/stats/$PREFIX
mkdir -p output/logs
LOG_PREFIX=output/logs/$PREFIX

NAMESPACE_PREFIXES=output/$PREFIX-namespaces.txt
HISTORY=$COLL_PREFIX-pages-meta-history.xml
ID2AUTHOR=$CONTRIB_PREFIX-id2author.cpickle
RAW_CONTRIBS=$CONTRIB_PREFIX-raw-contribs.mm
TITLES=$CONTRIB_PREFIX.titles.cpickle
ACC_CONTRIBS=$CONTRIB_PREFIX-acc-contribs.mm
DOC_AUTH_CONTRIBS=$CONTRIB_PREFIX-doc-auth-contribs.mm
AUTH_DOC_CONTRIBS=$CONTRIB_PREFIX-auth-doc-contribs.mm

LOG_CONTRIBS=$LOG_PREFIX-contribs.log

#echo "extracting likely namespaces from XML dump"
#NS_MIN_OCCURENCES=1
#( time ./bash/get_likely_namespaces.sh $HISTORY.bz2 $NS_MIN_OCCURENCES | tee $NAMESPACE_PREFIXES )|& tee $LOG_PREFIX-namespaces.log

echo "computing author contributions"
CONTRIBUTION_VALUE=one
MIN_AUTH_DOCS=1
MIN_DOC_AUTHS=1
#( time python scripts/history_to_contribs.py --history-dump=$HISTORY.bz2 --id2author=$ID2AUTHOR.bz2 --contribs=$RAW_CONTRIBS --contribution-value=$CONTRIBUTION_VALUE --min-auth-docs=$MIN_AUTH_DOCS --min-doc-auths=$MIN_DOC_AUTHS --namespace-prefixes=$NAMESPACE_PREFIXES ) |& tee $LOG_CONTRIBS
#mv $RAW_CONTRIBS.metadata.cpickle $TITLES # Artikeltitel-Datei umbennen
#bzip2 -zf $RAW_CONTRIBS $TITLES # komprimiere Beiträge, Artikeltitel

echo "accmulating contributions"
( time python scripts/accumulate_contribs.py --raw-contribs=$RAW_CONTRIBS.bz2 --acc-contribs=$ACC_CONTRIBS ) |& tee -a $LOG_CONTRIBS

echo "pruning top-N contributions"
TOP_N_CONTRIBS=50000
./bash/get_top_n_contribs.sh $ACC_CONTRIBS $TOP_N_CONTRIBS > $DOC_AUTH_CONTRIBS
NUM_CONTRIBS_BEFORE=$(cat $ACC_CONTRIBS | awk 'END {print NR-2}')
NUM_CONTRIBS_AFTER=$(cat $DOC_AUTH_CONTRIBS | awk 'END {print NR-2}')
echo "extracted $TOP_N_CONTRIBS contribs of max. value: from $NUM_CONTRIBS_BEFORE to $NUM_CONTRIBS_AFTER lines" | tee -a $LOG_CONTRIBS
bzip2 -zf $ACC_CONTRIBS $DOC_AUTH_CONTRIBS # komprimiere kumulierte Beiträge, Top-N-Beiträge





