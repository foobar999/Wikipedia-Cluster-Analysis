#!/bin/bash -e

if (( $# != 1 )); then
    echo "Usage: $0 CONTRIBS_FILE"
    exit 1
fi

CONTRIBS_FILE=$1
head -n 1 $CONTRIBS_FILE # übernehme erste Zeile
head -n 2 $CONTRIBS_FILE | tail -n 1 | awk '{ print $2 " " $1 " " $3}' # tausche #dokumente,#autoren in zweiter zeile
tail -n +3 $CONTRIBS_FILE | sort -k 2,2 -k 1,1 -ns | awk '{ print $2 " " $1 " " $3}' # sortiere nach autoren und tausche docid,autorid