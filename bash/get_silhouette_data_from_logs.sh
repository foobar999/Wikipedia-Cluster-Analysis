#!/bin/bash -e

if (( $# != 1 )); then
    echo "Usage: $0 LOG_FILES_PREFIX "
    exit 1
fi

LOG_FILES_PREFIX=$1
egrep -ir "silhouette" $LOG_FILES_PREFIX*.log | sed "s:${LOG_FILES_PREFIX}::" | sort -n | sed -E 's/\.log.*coefficient\://'