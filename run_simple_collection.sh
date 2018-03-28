#!/bin/bash
set -e  # Abbruch bei Fehler
PREFIX="simple-collection"
COLL_PREFIX="collections/$PREFIX"
OUT_PREFIX="output/$PREFIX"
TM_DIR="output/topic"
TM_PREFIX="output/topic/$PREFIX"

echo "generating XML dumps from JSON description"
time python generate_xml_from_simple_json_collection.py "$PREFIX.json" "$COLL_PREFIX-articles.xml" "$COLL_PREFIX-pages-meta-history.xml"

# TODO performanceüberlegungen:
# - sollte ich lieber binäre formate mit .save()/.save_corpus() statt .save_as_text() nehmen (wie etwa tfidf.save(output_files_prefix + '.tfidf_model')?)
# - .mm models durch .mm.bz2 ersetzen
# TODO preprocessing (stopwords,...)

# erfordert grundsätzlich .xml.bz2-Dateien
bzip2 -zkf "$COLL_PREFIX-articles.xml"
bzip2 -zkf "$COLL_PREFIX-pages-meta-history.xml"
mkdir -p $TM_DIR
VOCABULARY_SIZE=100
NO_BELOW=0
NO_ABOVE=1.0
ARTICLE_MIN_TOKENS=1
TOKEN_MIN_LEN=2
TOKEN_MAX_LEN=20
NAMESPACES="0"
echo "generating bag-of-words model"
time python src/wiki_to_bow.py $COLL_PREFIX-articles.xml.bz2 $TM_PREFIX-bow.pkl.bz2 --keep-words $VOCABULARY_SIZE --no-below=$NO_BELOW --no-above=$NO_ABOVE --article-min-tokens $ARTICLE_MIN_TOKENS --token-min-len $TOKEN_MIN_LEN --token-max-len $TOKEN_MAX_LEN --namespaces $NAMESPACES
time python src/utils/serialize_pkl_to_mm.py $TM_PREFIX-bow.pkl.bz2 $TM_PREFIX-bow.mm # TODO produktiv raus
time python src/utils/serialize_pkl_to_dict.py $TM_PREFIX-bow.pkl.bz2 $TM_PREFIX-dict.txt # TODO productiv raus

SMART_TFIDF="ltn"
echo "generating tf-idf model"
time python src/bow_to_tfidf.py $TM_PREFIX-bow.pkl.bz2 $TM_PREFIX-tfidf.pkl.bz2 --smart=$SMART_TFIDF
time python src/utils/serialize_pkl_to_mm.py $TM_PREFIX-tfidf.pkl.bz2 $TM_PREFIX-tfidf.mm # TODO prouktive raus


# echo "generating JSON revdocs from XML dumps"
# time ~/Python-Miniconda3/Scripts/mwxml.exe dump2revdocs "$COLL_PREFIX-pages-meta-history.xml" --output="$OUT_PREFIX-revdocs" --compress="json" --verbose
# echo "generating JSON revdocs with SHA1 hashes from revision texts"
# time python ~/Eclipse-Projekte/Wikipedia-Cluster-Analysis/add_sha1_to_revdocs.py "$OUT_PREFIX-revdocs/$PREFIX-pages-meta-history.json" --compress="json" "$OUT_PREFIX-revdocs-sha1"  
# echo "generating diffs from revdocs"
# #TODO hier namespaces filetern? oder in Zwischenschritt ganz kicken?
# time ~/Python-Miniconda3/Scripts/mwdiffs.exe revdocs2diffs "$OUT_PREFIX-revdocs-sha1/$PREFIX-pages-meta-history.json" --config="simple_collection_diffengine_config.yaml" --output="$OUT_PREFIX-diffs" --compress="json" --verbose
# echo "calculating persistence data from diffs"
# time ~/Python-Miniconda3/Scripts/mwpersistence.exe diffs2persistence "$OUT_PREFIX-diffs/$PREFIX-pages-meta-history.json" --output="$OUT_PREFIX-persistence" --sunset="<now>" --compres="json" --verbose 
# echo "calculating stats from persistence"
# time ~/Python-Miniconda3/Scripts/mwpersistence.exe persistence2stats "$OUT_PREFIX-persistence/$PREFIX-pages-meta-history.json" --output="$OUT_PREFIX-stats" --compress="json" --min-visible=0 --verbose
# python display_stats.py "$OUT_PREFIX-stats/$PREFIX-pages-meta-history.json" 


