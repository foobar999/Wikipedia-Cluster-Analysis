#!/bin/bash -e

if (( $# != 2 )); then
    echo "Usage: $0 DUMP NS_MIN_OCCURENCES"
    exit 1
fi
DUMP=$1
NS_MIN_OCCURENCES=$2

# suche alle <title>...</title> Elemente mit ':'
# extrahiere Substring bis zum ':' -> Präfix
# sortiere
# zähle Vorkommen der Präfixe
# repariere uniq-ausgabe
# filtere Präfixe: entferne mit #Vorkommen < NS_MIN_OCCURENCES
# entferne counter
# hänge überall wieder ':' an
bzgrep -o "<title>.*\:.*</title>" $DUMP | awk -F: '{print substr($1,8)}' | sort | uniq -c | sed 's/^\s*//' | awk -v limit=$NS_MIN_OCCURENCES '$1 >= limit{print $0}' | cut -d' ' -f2- | sed 's/$/:/g'
