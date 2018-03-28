#!/bin/bash
set -e  # Abbruch bei Fehler
PREFIX="simple-collection"
COLL_PREFIX="collections/$PREFIX"
OUT_PREFIX="output/$PREFIX"
TM_DIR="output/topic"

echo "generating XML dumps from JSON description"
time python generate_xml_from_simple_json_collection.py "$PREFIX.json" "$COLL_PREFIX-articles.xml" "$COLL_PREFIX-pages-meta-history.xml"

# TODO preprocessing (stopwords,...)

# erfordert grundsätzlich bz2
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
#python -m gensim.scripts.make_wiki "$COLL_PREFIX-articles.xml.bz2" "$TM_DIR/$PREFIX" $VOCABULARY_SIZE online
echo "generating gensim model data"
python simple_make_wiki.py "$COLL_PREFIX-articles.xml.bz2" "$TM_DIR/$PREFIX" --keep-words $VOCABULARY_SIZE --no-below=$NO_BELOW --no-above=$NO_ABOVE --article-min-tokens $ARTICLE_MIN_TOKENS --token-min-len $TOKEN_MIN_LEN --token-max-len $TOKEN_MAX_LEN --namespaces $NAMESPACES


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


