#!/bin/bash -e

if (( $# != 4 )); then
    echo "Usage: $0 PREFIX NO_BELOW NO_ABOVE ARTICLE_MIN_TOKENS"
    exit 1
fi
PREFIX=$1
NO_BELOW=$2
NO_ABOVE=$3
ARTICLE_MIN_TOKENS=$4

COLL_PREFIX=collections/$PREFIX
BOW_PREFIX=output/bow/$PREFIX
LOG_PREFIX=output/logs/$PREFIX

NAMESPACE_PREFIXES=output/$PREFIX-namespaces.txt
ARTICLES_DUMP=$COLL_PREFIX-pages-articles.xml
BOW_CORPUS_PREFIX=$BOW_PREFIX-bow
BOW_MODEL=$BOW_CORPUS_PREFIX.mm
BOW_TITLES=$BOW_CORPUS_PREFIX-titles.json
BOW_ID2WORD=$BOW_CORPUS_PREFIX-id2word.txt

LOG_BOW=$LOG_PREFIX-articles-to-bow.log

VOCABULARY_SIZE=2000000
TOKEN_MIN_LEN=2
echo "generating bag-of-words corpus files"
( time python3 -m scripts.cluster.articles_to_bow --articles-dump=$ARTICLES_DUMP.bz2 --out-prefix=$BOW_CORPUS_PREFIX --keep-words=$VOCABULARY_SIZE --no-below=$NO_BELOW --no-above=$NO_ABOVE --article-min-tokens=$ARTICLE_MIN_TOKENS --token-min-len=$TOKEN_MIN_LEN --remove-stopwords --namespace-prefixes=$NAMESPACE_PREFIXES ) |& tee $LOG_BOW

echo "creating JSON docid->doctitle mapping file"
python3 -m scripts.utils.metadata_to_doc_id_titles --metadata=$BOW_CORPUS_PREFIX.mm.metadata.cpickle --titles=$BOW_TITLES 
rm -f $BOW_CORPUS_PREFIX.mm.metadata.cpickle # entferne binäre Metadatendatei
bzip2 -zf $BOW_MODEL $BOW_TITLES $BOW_ID2WORD # komprimiere Korpus, Dictionary, docID-Mapping







