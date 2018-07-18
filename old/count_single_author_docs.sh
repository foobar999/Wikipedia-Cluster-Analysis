#!/bin/bash

# entferne 2-zeilen-header
# lade 1. spalte (dokumente)
# zähle acc contribs je dokument
# repariere kaputte uniq-ausgabe
# lade 2. spalte (eigentlich 1. spalte: anzahl contribs je dokument)
# zähle alle dokumente, die genau 1 contributor haben -> fallen weg beim co-authorship
#file=output/contribs/simple-collection-acc-contributions.mm.bz2
file=output/contribs/afwiki-20070124-acc-contributions.mm.bz2
num_single_author_docs=$(bzcat $file | tail -n +3 | cut -f 1 -d' ' | uniq -c  | tr -s ' ' | cut -f 2 -d' ' | grep -c '^1$')
echo "$num_single_author_docs documents having only 1 contributor"
#bzcat $file | tail -n +3 | cut -f 1 -d' ' | uniq -c  | tr -s ' '