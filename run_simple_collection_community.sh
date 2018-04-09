#!/bin/bash

# TODO akkumulieren

set -e  # Abbruch bei Fehler
export DEBUG="DEBUG" # TODO produktiv raus
PREFIX="simple-collection"
COLL_PREFIX="collections/$PREFIX"
mkdir -p "output/contribs"
CONTRIB_PREFIX="output/contribs/$PREFIX"
mkdir -p "output/logs"
LOG_PREFIX="output/logs/$PREFIX"

echo "generating XML dumps from JSON description"
time python scripts/utils/generate_xml_from_simple_json_collection.py $PREFIX.json $COLL_PREFIX-articles.xml $COLL_PREFIX-pages-meta-history.xml
bzip2 -zkf $COLL_PREFIX-articles.xml $COLL_PREFIX-pages-meta-history.xml 

echo "computing id2author dictionary"
( time python scripts/history_to_id2author.py --history-dump=$COLL_PREFIX-pages-meta-history.xml.bz2 --id2author=$CONTRIB_PREFIX-id2author.cpickle.bz2 ) |& tee $LOG_PREFIX-id2author.log
python scripts/utils/binary_to_text.py gensim $CONTRIB_PREFIX-id2author.cpickle.bz2 $CONTRIB_PREFIX-id2author.txt # TODO produktiv raus

echo "computing author contributions"
CONTRIBUTION_VALUE=diff_numterms
( time python scripts/history_to_contribs.py --history-dump=$COLL_PREFIX-pages-meta-history.xml.bz2 --id2author=$CONTRIB_PREFIX-id2author.cpickle.bz2 --contribs=$CONTRIB_PREFIX-raw-contributions.mm --contribution-value=$CONTRIBUTION_VALUE ) |& tee $LOG_PREFIX-raw-contribs.log
bzip2 -zf $CONTRIB_PREFIX-raw-contributions.mm
bzip2 -dkf $CONTRIB_PREFIX-raw-contributions.mm.bz2  # TODO produktiv raus


echo "accmulating contributions"
( time python scripts/accumulate_contribs.py --raw-contribs=$CONTRIB_PREFIX-raw-contributions.mm.bz2 --acc-contribs=$CONTRIB_PREFIX-acc-contributions.mm ) |& tee $LOG_PREFIX-acc-contribs.log
bzip2 -zf $CONTRIB_PREFIX-acc-contributions.mm
bzip2 -dkf $CONTRIB_PREFIX-acc-contributions.mm.bz2  # TODO produktiv raus



