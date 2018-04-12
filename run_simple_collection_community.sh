#!/bin/bash

# TODO numterms raus, da nicht intuitiv!s
# TODO statistik skript -> iteriere mit counter über corpus (eigenes skript, da ungefiltert): #doks,#autoren,#beiträge
# TODO rausfiltern von dokumenten, an denen nur einer gearbeitet hat -> bringe beide dokumentsätze "in einklang"?
#   TODO filtere author2id dict mit gensim methoden
#   muss ich wirklich dokumente rausschmeißen, die nix zum topicmodel beitragen? 
#     naja: je früher raus, desto besser
#   eher filterung: entferne dokumente mit weniger als k verschiedenen autoren?
#     auf jeden fall doks filtern, die genau 1 contributor haben
#   alternativ: nimm einfach größte zusammenhangskomponente?
# TODO das topicmodell kann ich mit allen (oder sehr vielen) doks trainieren, ohne was zu filtern
#   macht auch sinn: ein dokument kann zur themenbildung auch was beitragen, wenn wenige autoren dran arbeiteten
#   lediglich vor dem topicclustering muss ich die dokumente filtern
#   macht es sinn, dokumente zum clustering zu nehmen, die fürs topic model rausflogen?
# TODO pageid-basierte Filterung mit titel-basierter filterung vergleichen
# TODO per if-abfrage prüfen, ob pageid bereits vorhanden?
# ich machs so:
#   topicclus,commclus individuell, basierend auf eigenen filterungen
#   topicclus: filtere mittels whitelist bei clustering die entsprechenden docs
#   commclus: filtere mittels whitelist bei grapherzeugung?
#   ich sollte erst filtern, wenn kein mm-dateizugriff mehr nöigt
# TODO tausche bei mm spalten, da sonst gensim zicken macht?

set -e  # Abbruch bei Fehler
export DEBUG="DEBUG" # TODO produktiv raus
PREFIX="simple-collection"
COLL_PREFIX="collections/$PREFIX"
mkdir -p "output/contribs"
CONTRIB_PREFIX="output/contribs/$PREFIX"
mkdir -p "output/graph"
GRAPH_PREFIX="output/graph/$PREFIX"
mkdir -p "output/logs"
LOG_PREFIX="output/logs/$PREFIX"

echo "generating XML dumps from JSON description"
time python scripts/utils/generate_xml_from_simple_json_collection.py $PREFIX.json $COLL_PREFIX-articles.xml $COLL_PREFIX-pages-meta-history.xml
bzip2 -zkf $COLL_PREFIX-articles.xml $COLL_PREFIX-pages-meta-history.xml 

echo "computing author contributions"
CONTRIBUTION_VALUE=diff_numterms
( time python scripts/history_to_contribs.py --history-dump=$COLL_PREFIX-pages-meta-history.xml.bz2 --id2author=$CONTRIB_PREFIX-id2author.cpickle.bz2 --contribs=$CONTRIB_PREFIX-raw-contributions.mm --contribution-value=$CONTRIBUTION_VALUE ) |& tee $LOG_PREFIX-raw-contribs.log
python scripts/utils/binary_to_text.py gensim $CONTRIB_PREFIX-id2author.cpickle.bz2 $CONTRIB_PREFIX-id2author.txt # TODO produktiv raus
bzip2 -zf $CONTRIB_PREFIX-raw-contributions.mm
bzip2 -dkf $CONTRIB_PREFIX-raw-contributions.mm.bz2  # TODO produktiv raus

echo "accmulating contributions"
( time python scripts/accumulate_contribs.py --raw-contribs=$CONTRIB_PREFIX-raw-contributions.mm.bz2 --acc-contribs=$CONTRIB_PREFIX-acc-contributions.mm ) |& tee $LOG_PREFIX-acc-contribs.log

function swap_columns_and_sort {
    ACC_FILE=$CONTRIB_PREFIX-acc-contributions.mm
    ( head -n 1 $ACC_FILE && # übernehme erste Zeile
      head -n 2 $ACC_FILE | tail -n 1 | awk '{ print $2 " " $1 " " $3}' && # tausche #dokumente,#autoren in zweiter zeile
      tail -n +3 $ACC_FILE | sort -k 2 -ns | awk '{ print $2 " " $1 " " $3}'  ) > $CONTRIB_PREFIX-auth-doc-contribs.mm # sortiere nach autoren und tausche docid,autorid
}
echo "transforming (docid,authorid,contribvalue) file to (authorid,docid,contribvalue) file"
( time swap_columns_and_sort ) |& tee $LOG_PREFIX-sorted-acc-contribs.log
bzip2 -zf $CONTRIB_PREFIX-acc-contributions.mm $CONTRIB_PREFIX-auth-doc-contribs.mm
bzip2 -dkf $CONTRIB_PREFIX-acc-contributions.mm.bz2 $CONTRIB_PREFIX-auth-doc-contribs.mm.bz2 # TODO produktiv raus



















