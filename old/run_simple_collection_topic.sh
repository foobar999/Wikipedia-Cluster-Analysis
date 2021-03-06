#!/bin/bash -e

# TODO mal verschiendene maße (insb jsd) ausprobieren, dafür scipy clustering nehmen
# TODO soll ich echte minibatch kmeans nehmen? is mehr zu erklären
# TODO verschiedene clusteringverfahren: trivial, k-means, hierarchisch
# TODO index wird bisher nichtgelesen, da datei mit .bz2 umbenannt -> später Performanceverlust deshalb? -> mit und ohne kompression testen
# TODO time auf stunden umrechnen / besseres zeitmesskommando finden
# TODO "required" bei argparse einbauen
# TODO epilogs

export DEBUG="DEBUG" # TODO produktiv raus
PREFIX=simple-collection
COLL_PREFIX=collections/$PREFIX
mkdir -p output/bow
BOW_PREFIX=output/bow/$PREFIX
mkdir -p output/topic
TM_PREFIX=output/topic/$PREFIX
mkdir -p output/clusters
CLUS_PREFIX=output/clusters/$PREFIX
mkdir -p output/logs
LOG_PREFIX=output/logs/$PREFIX
NAMESPACE_PREFIXES_FILE=output/$PREFIX-namespaces.txt

echo "generating XML dumps from JSON description"
time python scripts/utils/generate_xml_from_simple_json_collection.py $PREFIX.json $COLL_PREFIX-pages-articles.xml $COLL_PREFIX-pages-meta-history.xml
bzip2 -zkf $COLL_PREFIX-pages-articles.xml $COLL_PREFIX-pages-meta-history.xml # gensim erfordert grundsätzlich .xml.bz2-Dateien

echo "extracting likely namespaces from XML dump"
#NS_MIN_OCCURENCES=1
#( time ./bash/get_likely_namespaces.sh $COLL_PREFIX-pages-articles.xml.bz2 $NS_MIN_OCCURENCES | tee $NAMESPACE_PREFIXES_FILE )|& tee $LOG_PREFIX-namespaces.log


VOCABULARY_SIZE=100
NO_BELOW=0
NO_ABOVE=1.0
ARTICLE_MIN_TOKENS=1
TOKEN_MIN_LEN=2
TOKEN_MAX_LEN=20
echo "generating bag-of-words corpus files"
( time python scripts/articles_to_bow.py --articles-dump=$COLL_PREFIX-pages-articles.xml.bz2 --out-prefix=$BOW_PREFIX-corpus --keep-words=$VOCABULARY_SIZE --no-below=$NO_BELOW --no-above=$NO_ABOVE --article-min-tokens=$ARTICLE_MIN_TOKENS --token-len-range $TOKEN_MIN_LEN $TOKEN_MAX_LEN --remove-stopwords --namespace-prefixes $NAMESPACE_PREFIXES_FILE ) |& tee $LOG_PREFIX-wiki-to-bow.log

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


