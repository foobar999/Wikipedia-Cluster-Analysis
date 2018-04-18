#!/bin/bash -e 

if (( $# != 1 )); then
    echo "Usage: $0 NS_FILE"
    exit 1
fi
NS_FILE=$1


# gibt Datei aus
# füge je Zeile vorne und hinten " ein
# ersetze Zeilenumbrüche durch Leerzeichen
cat $NS_FILE |  awk '{print "\""$0"\""}' | tr '[:space:]' ' '
