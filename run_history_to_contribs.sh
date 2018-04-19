#!/bin/bash -e

unset DEBUG
PREFIX=simplewiki-20111012
COLL_PREFIX="collections/$PREFIX"
mkdir -p "output/contribs"
CONTRIB_PREFIX="output/contribs/$PREFIX"
mkdir -p "output/logs"
LOG_PREFIX="output/logs/$PREFIX"

echo "computing author contributions"
CONTRIBUTION_VALUE=one
MIN_AUTH_DOCS=2
( time python scripts/history_to_contribs.py --history-dump=$COLL_PREFIX-pages-meta-history.xml.bz2 --id2author=$CONTRIB_PREFIX-id2author.cpickle.bz2 --contribs=$CONTRIB_PREFIX-raw-contributions.mm --contribution-value=$CONTRIBUTION_VALUE --min-auth-docs=$MIN_AUTH_DOCS --namespace-prefixes=output/$PREFIX-namespaces.txt) |& tee $LOG_PREFIX-contribs.log
mv $CONTRIB_PREFIX-raw-contributions.mm.metadata.cpickle $CONTRIB_PREFIX.titles.cpickle # Artikeltitel-Datei umbennen
bzip2 -zf $CONTRIB_PREFIX-raw-contributions.mm $CONTRIB_PREFIX.titles.cpickle

echo "accmulating contributions"
( time python scripts/accumulate_contribs.py --raw-contribs=$CONTRIB_PREFIX-raw-contributions.mm.bz2 --acc-contribs=$CONTRIB_PREFIX-acc-contributions.mm ) |& tee -a $LOG_PREFIX-contribs.log
bzip2 -zf $CONTRIB_PREFIX-acc-contributions.mm

