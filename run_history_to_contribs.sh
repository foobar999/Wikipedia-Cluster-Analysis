#!/bin/bash

set -e  # Abbruch bei Fehler
unset DEBUG
PREFIX="afwiki-20070124"
COLL_PREFIX="collections/$PREFIX"
mkdir -p "output/contribs"
CONTRIB_PREFIX="output/contribs/$PREFIX"
mkdir -p "output/logs"
LOG_PREFIX="output/logs/$PREFIX"

echo "computing author contributions"
CONTRIBUTION_VALUE=one
MIN_AUTH_DOCS=2
NAMESPACE_PREFIXES=$(cat output/$PREFIX-namespaces.txt | tr '[:space:]' ' ')
( time python scripts/history_to_contribs.py --history-dump=$COLL_PREFIX-pages-meta-history.xml.bz2 --id2author=$CONTRIB_PREFIX-id2author.cpickle.bz2 --contribs=$CONTRIB_PREFIX-raw-contributions.mm --contribution-value=$CONTRIBUTION_VALUE --min-auth-docs=$MIN_AUTH_DOCS --namespace-prefixes $NAMESPACE_PREFIXES) |& tee $LOG_PREFIX-raw-contribs.log
bzip2 -zf $CONTRIB_PREFIX-raw-contributions.mm

echo "accmulating contributions"
( time python scripts/accumulate_contribs.py --raw-contribs=$CONTRIB_PREFIX-raw-contributions.mm.bz2 --acc-contribs=$CONTRIB_PREFIX-acc-contributions.mm ) |& tee $LOG_PREFIX-acc-contribs.log
bzip2 -zf $CONTRIB_PREFIX-acc-contributions.mm


