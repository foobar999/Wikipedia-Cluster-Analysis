#!/bin/bash

# TODO preprocessing (stopwords,...) https://radimrehurek.com/gensim/corpora/dictionary.html https://radimrehurek.com/gensim/corpora/textcorpus.html
# - beachte: deutsch braucht andere stopwords! https://github.com/stopwords-iso
# - am besten mit filter_tokens() vom Dictionary!
# - stemming? -> könnte ich ja mal untersuchen 
#   - scheinen eher zu stören https://mimno.infosci.cornell.edu/papers/schofield_tacl_2016.pdf
# - lemmatisierung? -> könnte ich ja mal versuchen https://radimrehurek.com/gensim/utils.html#gensim.utils.lemmatize braucht nur lemmatize=True und package
#   - package aus rep braucht python 2, für python 3: https://github.com/clips/pattern https://stackoverflow.com/questions/44234796/pattern-package-for-python-3-6-anaconda
#   - scheint positiven Einfluss zu haben (da gensim das benutzen will, https://arxiv.org/pdf/1608.03995.pdf)
# - beachte sprachen bei stopwords, stemming, lemmatisierung!
# - nummern filtern?
# TODO index wird bisher nichtgelesen, da datei mit .bz2 umbenannt -> später Performanceverlust deshalb? -> mit und ohne kompression testen
# TODO debug-schalter mit mehr logging,...
# TODO logging auf dateien ändern?
# TODO logge: 
# - #dokumente vor preprocessing (geht das? ansonsten über bash-script)
# - nach preprocessing: #dokumente, größe dictionay, größe bow (d.h. summe aller einträge)
# TODO hashing dict -> dann auch in realisierung?

set -e  # Abbruch bei Fehler
export DEBUG="DEBUG" # TODO produktiv raus
PREFIX="simple-collection"
COLL_PREFIX="collections/$PREFIX"
OUT_PREFIX="output/$PREFIX"
BOW_DIR="output/bow"
BOW_PREFIX="output/bow/$PREFIX"
TM_DIR="output/topic"
TM_PREFIX="output/topic/$PREFIX"
LOG_PREFIX="logs/$PREFIX"

echo "generating XML dumps from JSON description"
time python scripts/utils/generate_xml_from_simple_json_collection.py $PREFIX.json $COLL_PREFIX-articles.xml $COLL_PREFIX-pages-meta-history.xml
bzip2 -zkf $COLL_PREFIX-articles.xml $COLL_PREFIX-pages-meta-history.xml # gensim erfordert grundsätzlich .xml.bz2-Dateien

mkdir -p $BOW_DIR
VOCABULARY_SIZE=100
NO_BELOW=0
NO_ABOVE=1.0
ARTICLE_MIN_TOKENS=1
TOKEN_MIN_LEN=2
TOKEN_MAX_LEN=20
NAMESPACES="0"
echo "generating bag-of-words corpus files"
time python scripts/wiki_to_bow.py $COLL_PREFIX-articles.xml.bz2 $BOW_PREFIX-corpus --keep-words $VOCABULARY_SIZE --no-below=$NO_BELOW --no-above=$NO_ABOVE --article-min-tokens $ARTICLE_MIN_TOKENS --token-len-range $TOKEN_MIN_LEN $TOKEN_MAX_LEN --namespaces $NAMESPACES 2>&1 | tee $LOG_PREFIX-wiki-to-bow.log
mv $BOW_PREFIX-corpus.mm.metadata.cpickle $BOW_PREFIX-corpus.metadata.cpickle # gib docID-Mapping intuitiveren Namen
python scripts/utils/dict_cpickle_to_text.py $BOW_PREFIX-corpus.metadata.cpickle $BOW_PREFIX-corpus.metadata.json # TODO produktiv raus
python scripts/utils/dictionary_cpickle_to_text.py $BOW_PREFIX-corpus.id2word.cpickle $BOW_PREFIX-corpus.id2word.txt # TODO produktiv raus
bzip2 -zf $BOW_PREFIX-corpus.mm $BOW_PREFIX-corpus.id2word.cpickle $BOW_PREFIX-corpus.metadata.cpickle # komprimiere Korpus, Dictionary, docID-Mapping

mkdir -p $TM_DIR
NUMTOPICS=3
PASSES=10
ITERATIONS=100
echo "generating lda model"
time python scripts/run_lda.py $BOW_PREFIX-corpus.mm.bz2 $BOW_PREFIX-corpus.id2word.cpickle.bz2 $TM_PREFIX-lda-model $NUMTOPICS --passes=$PASSES --iterations=$ITERATIONS 2>&1 | tee $LOG_PREFIX-lda.log
python scripts/utils/apply_lda_model_to_corpus.py $BOW_PREFIX-corpus.mm.bz2 $TM_PREFIX-lda-model $TM_PREFIX-corpus-topics.txt # TODO produktiv raus



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


