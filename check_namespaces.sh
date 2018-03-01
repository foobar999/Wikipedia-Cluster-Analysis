#!/bin/bash
# https://de.wikipedia.org/wiki/Hilfe:Namensr%C3%A4ume
namespace_ids=( 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 100 101 )
namespace_names=( "<keiner (:)>" "Diskussion" "Benutzer" "Benutzer-Diskussion" "Meta-Wikipedia" "Meta-Wikipedia-Diskussion" "Datei" "Datei-Diskussion" "MediaWiki" "MediaWiki-Diskussion" "Vorlage" "Vorlage-Diskussion" "Hilfe" "Hilfe-Diskussion" "Kategorie" "Kategorie-Diskussion" "Portal" "Portal-Diskussion" )
egrep -o '"namespace": -?[0-9]+' afwiki-20070124-revdocs/afwiki-20070124-pages-meta-history.xml | sort -V | uniq -c | awk '{print "namespace "$3":",$1}'