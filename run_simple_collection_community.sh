#!/bin/bash -e

# graph aufbau optimieren -> cocitation/bib coupling con igraph? https://gist.github.com/tts/4737987 http://igraph.org/python/doc/igraph.Graph-class.html#Incidence http://www.shizukalab.com/toolkits/sna/bipartite https://lists.nongnu.org/archive/html/igraph-help/2013-07/msg00014.html https://github.com/igraph/python-igraph/issues/168
# TODO ip-adressen ignorieren
# http://www.shizukalab.com/toolkits/sna/bipartite
# TODO .index-Dateien kicken
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

export DEBUG="DEBUG" # TODO produktiv raus
PREFIX=simple-collection
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

echo "generating XML dumps from JSON description"
time python scripts/utils/generate_xml_from_simple_json_collection.py $PREFIX.json $COLL_PREFIX-pages-articles.xml $HISTORY
bzip2 -zkf $COLL_PREFIX-pages-articles.xml $HISTORY 

echo "extracting likely namespaces from XML dump"
NS_MIN_OCCURENCES=1
( time ./bash/get_likely_namespaces.sh $HISTORY.bz2 $NS_MIN_OCCURENCES | tee $NAMESPACE_PREFIXES )|& tee $LOG_PREFIX-namespaces.log

echo "computing author contributions"
CONTRIBUTION_VALUE=diff_numterms
MIN_AUTH_DOCS=1
MIN_DOC_AUTHS=1
( time python scripts/history_to_contribs.py --history-dump=$HISTORY.bz2 --id2author=$ID2AUTHOR.bz2 --contribs=$RAW_CONTRIBS --contribution-value=$CONTRIBUTION_VALUE --min-auth-docs=$MIN_AUTH_DOCS --min-doc-auths=$MIN_DOC_AUTHS --namespace-prefixes=$NAMESPACE_PREFIXES ) |& tee $LOG_CONTRIBS
python scripts/utils/binary_to_text.py gensim $ID2AUTHOR.bz2 $CONTRIB_PREFIX-id2author.txt # TODO produktiv raus
mv $RAW_CONTRIBS.metadata.cpickle $TITLES # Artikeltitel-Datei umbennen
bzip2 -zf $RAW_CONTRIBS $TITLES # komprimiere Beiträge, Artikeltitel
bzip2 -dkf $RAW_CONTRIBS.bz2  # TODO produktiv raus
python scripts/utils/binary_to_text.py pickle $TITLES.bz2 $CONTRIB_PREFIX.titles.json # TODO produktiv raus

echo "accmulating contributions"
( time python scripts/accumulate_contribs.py --raw-contribs=$RAW_CONTRIBS.bz2 --acc-contribs=$ACC_CONTRIBS ) |& tee -a $LOG_CONTRIBS

echo "thresholding contributions"
MIN_CONTRIB_VALUE=1
./bash/threshold_contribs.sh $ACC_CONTRIBS $MIN_CONTRIB_VALUE > $DOC_AUTH_CONTRIBS
NUM_CONTRIBS_BEFORE=$(cat $ACC_CONTRIBS | awk 'END {print NR-2}')
NUM_CONTRIBS_AFTER=$(cat $DOC_AUTH_CONTRIBS | awk 'END {print NR-2}')
echo "thresholded number of contribs from $NUM_CONTRIBS_BEFORE to $NUM_CONTRIBS_AFTER" | tee -a $LOG_CONTRIBS

echo "creating bipartite graph from contributions"
WEIGHTED=y
( time python scripts/contribs_to_bipart_graph.py --contribs=$DOC_AUTH_CONTRIBS.bz2 --bipart-graph=$GRAPH_PREFIX-doc-auth-bipartite.graph.gz --weighted=$WEIGHTED) |& tee $LOG_PREFIX-graph.log


haschegif

echo "calculating graph stats"
( time python scripts/get_graph_stats.py --graph=$GRAPH_PREFIX-co-authorship.cpickle.gz ) |& tee -a $LOG_PREFIX-graph.log

echo "calculating stats from history dump"
( time python scripts/get_history_stats.py --history-dump=$HISTORY.bz2 --stat-files-prefix=$STATS_PREFIX --namespace-prefixes=$NAMESPACE_PREFIXES ) |& tee $LOG_PREFIX-stats.log
QUANTILE=1
for STAT_FILE in $STATS_PREFIX*.csv; do
    [ -f "$STAT_FILE" ] || break
    IMAGE_FILE="${STAT_FILE%%.*}.pdf"
    LOG_FILE="$(basename ${STAT_FILE%%.*})"
    ( python scripts/visualize_stats.py --stats=$STAT_FILE --viz=$IMAGE_FILE --quantile=$QUANTILE ) |& tee output/logs/$LOG_FILE.log
done







#echo "transforming (docid,authorid,contribvalue) file to (authorid,docid,contribvalue) file"
#./bash/get_swapped_author_doc_contribs.sh $DOC_AUTH_CONTRIBS > $AUTH_DOC_CONTRIBS
#bzip2 -zf $ACC_CONTRIBS $DOC_AUTH_CONTRIBS $AUTH_DOC_CONTRIBS
#bzip2 -dkf $ACC_CONTRIBS.bz2 $DOC_AUTH_CONTRIBS.bz2 $AUTH_DOC_CONTRIBS.bz2 # TODO produktiv raus





