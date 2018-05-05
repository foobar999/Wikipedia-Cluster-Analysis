#!/bin/bash -e

if (( $# != 2 )); then
    echo "Usage: $0 IPREFIX CONTRIBUTION_VALUE"
    exit 1
fi
IPREFIX=$1
CONTRIBUTION_VALUE=$2
OPREFIX=$IPREFIX-$CONTRIBUTION_VALUE

COLL_PREFIX=collections/$IPREFIX
mkdir -p output/contribs
CONTRIB_PREFIX=output/contribs/$OPREFIX
#mkdir -p output/stats
#STATS_PREFIX=output/stats/$PREFIX
mkdir -p output/logs
LOG_PREFIX=output/logs/$OPREFIX

NAMESPACE_PREFIXES=output/$IPREFIX-namespaces.txt
HISTORY=$COLL_PREFIX-pages-meta-history.xml
ID2AUTHOR=$CONTRIB_PREFIX-id2author.txt
RAW_CONTRIBS=$CONTRIB_PREFIX-raw-contribs.mm
TITLES=$CONTRIB_PREFIX.titles.cpickle
ACC_CONTRIBS=$CONTRIB_PREFIX-acc-contribs.mm
ACC_AUTH_DOC_CONTRIBS=$CONTRIB_PREFIX-acc-auth-doc-contribs.mm
PRUNED_AUTH_DOC_CONTRIBS=$CONTRIB_PREFIX-pruned-auth-doc-contribs.mm
PRUNED_CONTRIBS=$CONTRIB_PREFIX-pruned-contribs.mm

LOG_CONTRIBS=$LOG_PREFIX-contribs.log

#echo "extracting likely namespaces from XML dump"
#NS_MIN_OCCURENCES=1
#( time ./bash/get_likely_namespaces.sh $HISTORY.bz2 $NS_MIN_OCCURENCES | tee $NAMESPACE_PREFIXES )|& tee $LOG_PREFIX-namespaces.log

echo "computing author contributions"
MIN_AUTH_DOCS=1
MIN_DOC_AUTHS=1
( time python scripts/history_to_contribs.py --history-dump=$HISTORY.bz2 --id2author=$ID2AUTHOR.bz2 --contribs=$RAW_CONTRIBS --contribution-value=$CONTRIBUTION_VALUE --min-auth-docs=$MIN_AUTH_DOCS --min-doc-auths=$MIN_DOC_AUTHS --namespace-prefixes=$NAMESPACE_PREFIXES ) |& tee $LOG_CONTRIBS
mv $RAW_CONTRIBS.metadata.cpickle $TITLES # Artikeltitel-Datei umbennen
bzip2 -zf $RAW_CONTRIBS $TITLES # komprimiere Beiträge, Artikeltitel

echo "accmulating contributions"
( time python scripts/accumulate_contribs.py --raw-contribs=$RAW_CONTRIBS.bz2 --acc-contribs=$ACC_CONTRIBS ) |& tee -a $LOG_CONTRIBS

echo "pruning top-N author contributions"
./bash/swap_doc_auth_columns.sh $ACC_CONTRIBS > $ACC_AUTH_DOC_CONTRIBS
TOP_N_CONTRIBS=100
python scripts/prune_author_contribs.py --author-doc-contribs=$ACC_AUTH_DOC_CONTRIBS --pruned-contribs=$PRUNED_AUTH_DOC_CONTRIBS --top-n-contribs=$TOP_N_CONTRIBS |& tee -a $LOG_CONTRIBS
./bash/swap_doc_auth_columns.sh $PRUNED_AUTH_DOC_CONTRIBS > $PRUNED_CONTRIBS

rm -f $ACC_AUTH_DOC_CONTRIBS $PRUNED_AUTH_DOC_CONTRIBS # entferne temporäre Dateien mit getauschten Spalten
bzip2 -zf $ACC_CONTRIBS $PRUNED_CONTRIBS # komprimiere alle angelegten Dateen
















#echo "pruning top-N contributions"
#TOP_N_CONTRIBS=50000
#./bash/get_top_n_contribs.sh $ACC_CONTRIBS $TOP_N_CONTRIBS > $DOC_AUTH_CONTRIBS
#NUM_CONTRIBS_BEFORE=$(cat $ACC_CONTRIBS | awk 'END {print NR-2}')
#NUM_CONTRIBS_AFTER=$(cat $DOC_AUTH_CONTRIBS | awk 'END {print NR-2}')
#echo "extracted $TOP_N_CONTRIBS contribs of max. value: from $NUM_CONTRIBS_BEFORE to $NUM_CONTRIBS_AFTER lines" | tee -a $LOG_CONTRIBS
#bzip2 -zf $ACC_CONTRIBS $DOC_AUTH_CONTRIBS # komprimiere kumulierte Beiträge, Top-N-Beiträge









