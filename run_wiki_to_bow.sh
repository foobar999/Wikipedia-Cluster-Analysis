
set -e  # Abbruch bei Fehler
if (( $# != 1 )); then
    echo "Usage: $0 PREFIX"
    exit 1
fi

unset DEBUG
PREFIX=$1
COLL_PREFIX="collections/$PREFIX"
BOW_PREFIX="output/bow/$PREFIX"
LOG_PREFIX="logs/$PREFIX"

VOCABULARY_SIZE=100000
NO_BELOW=5  # TODO höher bei großem korpus
NO_ABOVE=0.1
ARTICLE_MIN_TOKENS=50
TOKEN_MIN_LEN=2
TOKEN_MAX_LEN=20
NAMESPACES="0"
echo "generating bag-of-words corpus files"
time python scripts/wiki_to_bow.py $COLL_PREFIX-articles.xml.bz2 $BOW_PREFIX-corpus --keep-words $VOCABULARY_SIZE --no-below=$NO_BELOW --no-above=$NO_ABOVE --article-min-tokens $ARTICLE_MIN_TOKENS --token-len-range $TOKEN_MIN_LEN $TOKEN_MAX_LEN --namespaces $NAMESPACES 2>&1 | tee $LOG_PREFIX-wiki-to-bow.log
mv $BOW_PREFIX-corpus.mm.metadata.cpickle $BOW_PREFIX-corpus.metadata.cpickle # gib docID-Mapping intuitiveren Namen
bzip2 -zf $BOW_PREFIX-corpus.mm $BOW_PREFIX-corpus.id2word.cpickle $BOW_PREFIX-corpus.metadata.cpickle # komprimiere Korpus, Dictionary, docID-Mapping