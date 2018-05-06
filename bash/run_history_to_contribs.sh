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
#mkdir -p output/stats
#STATS_PREFIX=output/stats/$PREFIX
mkdir -p output/logs
LOG_PREFIX=output/logs/$OPREFIX

NAMESPACE_PREFIXES=output/$IPREFIX-namespaces.txt
HISTORY=$COLL_PREFIX-pages-meta-history.xml
ID2AUTHOR=$CONTRIB_PREFIX-id2author.txt
RAW_CONTRIBS=$CONTRIB_PREFIX-raw-contribs.mm
TITLES=$CONTRIB_PREFIX-titles.json
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
#mv $RAW_CONTRIBS.metadata.cpickle $TITLES # Artikeltitel-Datei umbennen
python ./scripts/utils/binary_to_text.py pickle $RAW_CONTRIBS.metadata.cpickle $TITLES
rm -f $RAW_CONTRIBS.metadata.cpickle
bzip2 -zf $RAW_CONTRIBS $TITLES # komprimiere Beiträge, Artikeltitel

echo "accmulating contributions"
( time python scripts/accumulate_contribs.py --raw-contribs=$RAW_CONTRIBS.bz2 --acc-contribs=$ACC_CONTRIBS ) |& tee -a $LOG_CONTRIBS

echo "pruning top-$TOP_N_CONTRIBS author contributions"
./bash/swap_doc_auth_columns.sh $ACC_CONTRIBS > $ACC_AUTH_DOC_CONTRIBS
python scripts/prune_author_contribs.py --author-doc-contribs=$ACC_AUTH_DOC_CONTRIBS --pruned-contribs=$PRUNED_AUTH_DOC_CONTRIBS --top-n-contribs=$TOP_N_CONTRIBS |& tee -a $LOG_CONTRIBS
./bash/swap_doc_auth_columns.sh $PRUNED_AUTH_DOC_CONTRIBS > $PRUNED_CONTRIBS

rm -f $ACC_AUTH_DOC_CONTRIBS $PRUNED_AUTH_DOC_CONTRIBS # entferne temporäre Dateien mit getauschten Spalten
bzip2 -zf $ACC_CONTRIBS $PRUNED_CONTRIBS # komprimiere alle angelegten Dateen























