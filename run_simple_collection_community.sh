#!/bin/bash

# TODO rausfiltern von dokumenten, an denen nur einer gearbeitet hat -> bringe beide dokumentsätze "in einklang"?
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

# TODO stabil nötigt?
echo "sorting contributions by author"
# ignoriere die ersten beiden Zeilen beim Sortieren
( time ( head -n 2 $CONTRIB_PREFIX-acc-contributions.mm && tail -n +3 $CONTRIB_PREFIX-acc-contributions.mm | sort -k 2 -ns  ) > $CONTRIB_PREFIX-sorted-acc-contribs.mm ) |& tee $LOG_PREFIX-sorted-acc-contribs.log
bzip2 -zf $CONTRIB_PREFIX-acc-contributions.mm $CONTRIB_PREFIX-sorted-acc-contribs.mm # wird unkomprimiert benötigt
bzip2 -dkf $CONTRIB_PREFIX-acc-contributions.mm.bz2 $CONTRIB_PREFIX-sorted-acc-contribs.mm.bz2 # TODO produktiv raus



















