#!/bin/bash

if (( $# != 2 )); then
    echo "Usage: $0 DOC_AUTH_FILE THRESHOLD"
    exit 1
fi
DOC_AUTH_FILE=$1
THRESHOLD=$2

head -n 1 $DOC_AUTH_FILE # übernehme erste Zeile
CONTRIBS_OUTPUT=$(tail -n +3 $DOC_AUTH_FILE | awk -v limit=$THRESHOLD '$3 >= limit{print $1 " " $2 " " $3}')
NUM_LINES=$(echo "$CONTRIBS_OUTPUT" | wc -l)
head -n 2 $DOC_AUTH_FILE | tail -n 1 | awk -v NUM_CONTRIBS="$NUM_LINES" '{ print $1 " " $2 " " NUM_CONTRIBS }'
echo "$CONTRIBS_OUTPUT"