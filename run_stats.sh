#!/bin/bash

set -e  # Abbruch bei Fehler
if (( $# != 1 )); then
    echo "Usage: $0 PREFIX"
    exit 1
fi
unset DEBUG
PREFIX=$1

COLL_PREFIX="collections/$PREFIX"
STATS_PREFIX="output/stats/$PREFIX"
LOG_PREFIX="output/logs/$PREFIX"

echo "calculating stats from history dump"
( time python scripts/get_history_stats.py --history-dump=$COLL_PREFIX-pages-meta-history.xml.bz2 --stat-files-prefix=$STATS_PREFIX --namespace-prefixes=output/$PREFIX-namespaces.txt ) |& tee $LOG_PREFIX-stats.log
QUANTILE=0.95
for STAT_FILE in $STATS_PREFIX*.csv; do
    [ -f "$STAT_FILE" ] || break
    IMAGE_FILE="${STAT_FILE%%.*}.pdf"
    LOG_FILE="$(basename ${STAT_FILE%%.*})"
    ( python scripts/visualize_stats.py --stats=$STAT_FILE --viz=$IMAGE_FILE --quantile=$QUANTILE ) |& tee output/logs/$LOG_FILE.log
done