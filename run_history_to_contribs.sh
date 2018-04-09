#!/bin/bash

# TODO akkumulieren

set -e  # Abbruch bei Fehler
unset DEBUG
PREFIX="afwiki-20070124"
COLL_PREFIX="collections/$PREFIX"
mkdir -p "output/contribs"
CONTRIB_PREFIX="output/contribs/$PREFIX"
mkdir -p "output/logs"
LOG_PREFIX="output/logs/$PREFIX"

echo "computing id2author dictionary"
( time python scripts/history_to_id2author.py --history-dump=$COLL_PREFIX-pages-meta-history.xml.bz2 --id2author=$CONTRIB_PREFIX-id2author.cpickle.bz2 ) |& tee $LOG_PREFIX-id2author.log

echo "computing author contributions"
CONTRIBUTION_VALUE=one
( time python scripts/history_to_contribs.py --history-dump=$COLL_PREFIX-pages-meta-history.xml.bz2 --id2author=$CONTRIB_PREFIX-id2author.cpickle.bz2 --contribs=$CONTRIB_PREFIX-contributions.mm --contribution-value=$CONTRIBUTION_VALUE ) |& tee $LOG_PREFIX-id2author.log