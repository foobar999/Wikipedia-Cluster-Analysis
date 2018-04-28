#!/bin/bash -e

if (( $# != 2 )); then
    echo "Usage: $0 DOC_AUTH_FILE TOP_N"
    exit 1
fi
DOC_AUTH_FILE=$1
TOP_N=$2

# �bernehme erste Zeile
head -n 1 $DOC_AUTH_FILE 

# hole Daten ohne Header
# sortiere absteigend nach Beitragswerten
# hole Eintr�ge mit Top-N-Beitr�gen
# erzeuge wieder Sortierung nach DocIDs, AuthorIDs
CONTRIBS=$(tail -n +3 $DOC_AUTH_FILE | sort -k 3 -rns | head -n $TOP_N | sort -k1,1 -k2,2 -ns)

# z�hle neue Anzahl Beitr�ge
NUM_LINES=$(echo "$CONTRIBS" | wc -l)

# neuer Header mit neuer Anzahl Beitr�ge
head -n 2 $DOC_AUTH_FILE | tail -n 1 | awk -v NUM_CONTRIBS="$NUM_LINES" '{ print $1 " " $2 " " NUM_CONTRIBS }'

# gib Top-N-Beitr�ge aus
echo "$CONTRIBS"

#CONTRIBS_OUTPUT=$(tail -n +3 $DOC_AUTH_FILE | awk -v limit=$THRESHOLD '$3 >= limit{print $1 " " $2 " " $3}')
#NUM_LINES=$(echo "$CONTRIBS_OUTPUT" | wc -l)
#head -n 2 $DOC_AUTH_FILE | tail -n 1 | awk -v NUM_CONTRIBS="$NUM_LINES" '{ print $1 " " $2 " " NUM_CONTRIBS }'
#echo "$CONTRIBS_OUTPUT"