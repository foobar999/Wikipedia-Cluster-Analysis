#!/bin/bash
#python.exe ~/Python-Miniconda3/Lib/site-packages/mwpersistence/mwpersistence.py dump2diffs afwiki-20070124-pages-meta-history.xml.bz2
PREFIX="afwiki-20070124"
# TODO split einbauen für revdocs
echo "generating JSON revdocs from XML dumps"
time ~/Python-Miniconda3/Scripts/mwxml.exe dump2revdocs "$PREFIX-pages-meta-history.xml.bz2" --output="$PREFIX-revdocs" --verbose
echo "generating JSON revdocs with SHA1 hashes from revision texts"
time python ~/Eclipse-Projekte/Wikipedia-Cluster-Analysis/add_sha1_to_revdocs.py "$PREFIX-revdocs/$PREFIX-pages-meta-history.xml.bz2" "$PREFIX-revdocs-sha1"
echo "generating diffs from revdocs"
time ~/Python-Miniconda3/Scripts/mwdiffs.exe revdocs2diffs "$PREFIX-revdocs-sha1/$PREFIX-pages-meta-history.xml.bz2" --config="diffengine_config.yaml" --output="$PREFIX-diffs" --verbose
echo "calculating persistence data from diffs"
time ~/Python-Miniconda3/Scripts/mwpersistence.exe diffs2persistence "$PREFIX-diffs/$PREFIX-pages-meta-history.xml.bz2" --output="$PREFIX-persistence" --sunset="<now>" --verbose 
echo "calculating stats from persistence"
time ~/Python-Miniconda3/Scripts/mwpersistence.exe persistence2stats "$PREFIX-persistence/$PREFIX-pages-meta-history.xml.bz2" --output="$PREFIX-stats" --verbose

#time ~/Python-Miniconda3/Scripts/mwpersistence.exe dump2stats "$PREFIX-pages-meta-history.xml.bz2" --config="diffengine_config.yaml" --sunset="<now>" --output="$PREFIX-stats" --verbose


