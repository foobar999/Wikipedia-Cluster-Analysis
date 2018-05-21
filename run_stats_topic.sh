#!/bin/bash -e

if (( $# != 1 )); then
    echo "Usage: $0 CONFIG"
    exit 1
fi
unset DEBUG
CONFIG=$1
source $CONFIG

COLL_PREFIX=collections/$PREFIX
STATS_PREFIX=output/stats/$PREFIX

echo "PREFIX $PREFIX"
echo "DEBUG $DEBUG"
if [ ! -z ${DEBUG+x} ]; then # variable gesetzt?
    export DEBUG=$DEBUG
fi
echo "NO_BELOW $NO_BELOW"
echo "NO_ABOVE $NO_ABOVE"
echo "ARTICLE_MIN_TOKENS $ARTICLE_MIN_TOKENS"

ARTICLES_DUMP=$COLL_PREFIX-pages-articles.xml.bz2
LOG_ART_STATS=$STATS_PREFIX-articles-stats.log
NAMESPACE_PREFIXES=output/$PREFIX-namespaces.txt
TOKEN_MIN_LEN=2
python3 scripts/get_articles_stats.py --articles-dump=$ARTICLES_DUMP --no-below=$NO_BELOW --no-above=$NO_ABOVE --token-min-len=$TOKEN_MIN_LEN --article-min-tokens=$ARTICLE_MIN_TOKENS --namespace-prefixes=$NAMESPACE_PREFIXES |& tee  $LOG_ART_STATS
