#!/bin/bash

set -e  # Abbruch bei Fehler
if (( $# != 1 )); then
    echo "Usage: $0 PREFIX"
    exit 1
fi
unset DEBUG
PREFIX=$1

COLL_PREFIX="collections/$PREFIX"
BOW_PREFIX="output/bow/$PREFIX"
LOG_PREFIX="output/logs/$PREFIX"

VOCABULARY_SIZE=1000000
#NO_BELOW=5  # TODO höher bei großem korpus
#NO_ABOVE=0.1
#ARTICLE_MIN_TOKENS=50
#TOKEN_MIN_LEN=1
#TOKEN_MAX_LEN=100
NO_BELOW=1  # TODO höher bei großem korpus
NO_ABOVE=0.25
ARTICLE_MIN_TOKENS=1
TOKEN_MIN_LEN=1
TOKEN_MAX_LEN=100
echo "generating bag-of-words corpus files"
( time python scripts/articles_to_bow.py --articles-dump=$COLL_PREFIX-pages-articles.xml.bz2 --out-prefix=$BOW_PREFIX-corpus --keep-words=$VOCABULARY_SIZE --no-below=$NO_BELOW --no-above=$NO_ABOVE --article-min-tokens=$ARTICLE_MIN_TOKENS --token-len-range $TOKEN_MIN_LEN $TOKEN_MAX_LEN --namespace-prefixes=output/$PREFIX-namespaces.txt ) |& tee $LOG_PREFIX-wiki-to-bow.log
mv $BOW_PREFIX-corpus.mm.metadata.cpickle $BOW_PREFIX-corpus.metadata.cpickle # gib docID-Mapping intuitiveren Namen
#python scripts/utils/binary_to_text.py pickle $BOW_PREFIX-corpus.metadata.cpickle $BOW_PREFIX-corpus.metadata.json # TODO produktiv raus
#python scripts/utils/binary_to_text.py gensim $BOW_PREFIX-corpus.id2word.cpickle $BOW_PREFIX-corpus.id2word.txt # TODO produktiv raus
bzip2 -zf $BOW_PREFIX-corpus.mm $BOW_PREFIX-corpus.id2word.cpickle $BOW_PREFIX-corpus.metadata.cpickle # komprimiere Korpus, Dictionary, docID-Mapping
