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
# TODO logge: 
# - #dokumente vor preprocessing (geht das? ansonsten über bash-script)
# - nach preprocessing: #dokumente, größe dictionay, größe bow (d.h. summe aller einträge)
# TODO debug: normales dicr, release hashing dict -> sinnvoll, da terme später ziemlich sicher nötig?
# TODO time auf stunden umrechnen / besseres zeitmesskommando finden
# TODO "required" bei argparse einbauen
# TODO wiki_to_bow -> articles_to_bow
# TODO in allen description enwiki reinschreiben

set -e  # Abbruch bei Fehler
export DEBUG="DEBUG" # TODO produktiv raus
PREFIX="simple-collection"
COLL_PREFIX="collections/$PREFIX"
mkdir -p "output/bow"
BOW_PREFIX="output/bow/$PREFIX"
mkdir -p "output/topic"
TM_PREFIX="output/topic/$PREFIX"
mkdir -p "output/clusters"
CLUS_PREFIX="output/clusters/$PREFIX"
mkdir -p "output/logs"
LOG_PREFIX="output/logs/$PREFIX"

echo "generating XML dumps from JSON description"
time python scripts/utils/generate_xml_from_simple_json_collection.py $PREFIX.json $COLL_PREFIX-articles.xml $COLL_PREFIX-pages-meta-history.xml
bzip2 -zkf $COLL_PREFIX-articles.xml $COLL_PREFIX-pages-meta-history.xml # gensim erfordert grundsätzlich .xml.bz2-Dateien

echo "extracting likely namespaces from XML dump"
NS_MIN_OCCURENCES=1
( time bzgrep -o "<title>.*\:.*</title>" $COLL_PREFIX-articles.xml.bz2 | awk -F: '{print substr($1,8)}' | sort | uniq -c | awk -v limit=$NS_MIN_OCCURENCES '$1 >= limit{print $2}' | tee output/$PREFIX-namespaces.txt )|& tee $LOG_PREFIX-namespaces.log


VOCABULARY_SIZE=100
NO_BELOW=0
NO_ABOVE=1.0
ARTICLE_MIN_TOKENS=1
TOKEN_MIN_LEN=2
TOKEN_MAX_LEN=20
NAMESPACE_PREFIXES=$(cat output/$PREFIX-namespaces.txt | tr '[:space:]' ' ')
echo "generating bag-of-words corpus files"
#( time python scripts/wiki_to_bow.py $COLL_PREFIX-articles.xml.bz2 $BOW_PREFIX-corpus --keep-words $VOCABULARY_SIZE --no-below=$NO_BELOW --no-above=$NO_ABOVE --article-min-tokens $ARTICLE_MIN_TOKENS --token-len-range $TOKEN_MIN_LEN $TOKEN_MAX_LEN --namespaces $NAMESPACES ) |& tee $LOG_PREFIX-wiki-to-bow.log
( time python scripts/articles_to_bow.py --articles-dump=$COLL_PREFIX-articles.xml.bz2 --out-prefix=$BOW_PREFIX-corpus --keep-words=$VOCABULARY_SIZE --no-below=$NO_BELOW --no-above=$NO_ABOVE --article-min-tokens=$ARTICLE_MIN_TOKENS --token-len-range $TOKEN_MIN_LEN $TOKEN_MAX_LEN --namespace-prefixes $NAMESPACE_PREFIXES ) |& tee $LOG_PREFIX-wiki-to-bow.log

mv $BOW_PREFIX-corpus.mm.metadata.cpickle $BOW_PREFIX-corpus.metadata.cpickle # gib docID-Mapping intuitiveren Namen
python scripts/utils/binary_to_text.py pickle $BOW_PREFIX-corpus.metadata.cpickle $BOW_PREFIX-corpus.metadata.json # TODO produktiv raus
python scripts/utils/binary_to_text.py gensim $BOW_PREFIX-corpus.id2word.cpickle $BOW_PREFIX-corpus.id2word.txt # TODO produktiv raus
bzip2 -zf $BOW_PREFIX-corpus.mm $BOW_PREFIX-corpus.id2word.cpickle $BOW_PREFIX-corpus.metadata.cpickle # komprimiere Korpus, Dictionary, docID-Mapping

echo "extracting pageids from metadata"
( time python scripts/metadata_to_pageids.py --metadata=$BOW_PREFIX-corpus.metadata.cpickle.bz2 --pageids=$BOW_PREFIX-corpus.pageids.cpickle.bz2 ) |& tee $LOG_PREFIX-pageids.log

NUMTOPICS=3
PASSES=10
ITERATIONS=100
ALPHA=symmetric
BETA=symmetric
echo "generating lda model"
( time python scripts/bow_to_topic.py $BOW_PREFIX-corpus.mm.bz2 $BOW_PREFIX-corpus.id2word.cpickle.bz2 $TM_PREFIX-lda-model $NUMTOPICS --passes=$PASSES --iterations=$ITERATIONS --alpha=$ALPHA --beta=$BETA ) |& tee $LOG_PREFIX-lda.log
python scripts/utils/apply_lda_model_to_corpus.py $BOW_PREFIX-corpus.mm.bz2 $TM_PREFIX-lda-model $TM_PREFIX-corpus-topics.txt # TODO produktiv raus

NUMCLUSTERS=$NUMTOPICS
BATCHSIZE=1000
echo "computing kmeans clusters"
( time python scripts/topic_to_cluster.py $BOW_PREFIX-corpus.mm.bz2 $TM_PREFIX-lda-model $CLUS_PREFIX-kmeans-labels.cpickle.bz2 $NUMCLUSTERS --batch-size=$BATCHSIZE ) |& tee $LOG_PREFIX-kmeans.log
python scripts/utils/binary_to_text.py numpy $CLUS_PREFIX-kmeans-labels.cpickle.bz2 $CLUS_PREFIX-kmeans-labels.txt # TODO produktiv raus

echo "calculating silhouette score"
( time python scripts/evaluate_dense.py $BOW_PREFIX-corpus.mm.bz2 $TM_PREFIX-lda-model $CLUS_PREFIX-kmeans-labels.cpickle.bz2 ) |& tee $LOG_PREFIX-silhouette.log

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


