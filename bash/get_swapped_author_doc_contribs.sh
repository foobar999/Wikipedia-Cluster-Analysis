#!/bin/bash -e

if (( $# != 1 )); then
    echo "Usage: $0 DOC_AUTH_FILE"
    exit 1
fi

DOC_AUTH_FILE=$1
head -n 1 $DOC_AUTH_FILE # übernehme erste Zeile
head -n 2 $DOC_AUTH_FILE | tail -n 1 | awk '{ print $2 " " $1 " " $3}' # tausche #dokumente,#autoren in zweiter zeile
tail -n +3 $DOC_AUTH_FILE | sort -k 2 -ns | awk '{ print $2 " " $1 " " $3}' # sortiere nach autoren und tausche docid,autorid