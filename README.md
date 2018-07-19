
Installation
------------
Das Projekt "Wikipedia-Cluster-Analysis" ermöglicht Erzeugung, Vergleich und Analyse von themenbasierten Clustern und autorenbasierten Communities aus einem Artikeldump und einem Historiendump von Wikipedia. Wikipedia-Cluster-Analysis erfordert grundsätzlich `python3`. Außerdem benötigt Wikipedia-Cluster-Analysis Pythonmodule, die folgendermaßen installiert werden können:
```
pip3 install xmltodict scipy mediawiki_utilities numpy matplotlib networkx gensim python_igraph scripts scikit_learn
```
Eine genauere Angabe der verwendeten Module befindet sich in `requirements.txt`. Wikipedia-Cluster-Analysis benötigt außerdem eine heruntergeladene Version von 
"MALLET", zum Download siehe http://mallet.cs.umass.edu/download.php . Der Aufruf des Skripts zur themenbasiertern Clusteranalyse sowie des zugehörigen Statistikskripts erfordert, dass in der verwendeten Knofigurationsdatei die Variable MALLET_HOME auf das entpackte Verzeichnis gesetzt wird, z.B. `MALLET_HOME=~/Projekte/Wikipedia-Cluster-Analysis/bin/mallet-2.0.8`. Die im Speichermedium enthaltene Version von Wikipedia-Cluster-Analysis enthält eine MALLET-Installation im Verzeichnis `bin`.
  
  
Dumps
-----
Wikipedia-Cluster-Analysis geht von zwei Arten von Wikipediadumps aus, die sich im Verzeichnis `collections` befinden müssen: Einem Artikeldump der Form `collections/<PREFIX>-pages-articles.xml.bz2` und einem Historiendump der Form `collections/<PREFIX>-pages-articles.xml.bz2`. Zwei zusammengehörende Dumps bilden ein Paar mit demselben Präfix `<PREFIX>`. Die im Speichermedium enthaltene Version von Wikipedia-Cluster-Analysis enthält drei Dump-Paar:
- Präfix `af07`: 
  - originales Präfix dieses Dumps: `afwiki-20070124` -> wurde hier zur Vermeidung langer Dateinamen umbenannt
  - Name des Artikeldumps: `af07-pages-articles.xml.bz2`
  - Name des Historiendumps: `af07-pages-meta-history.xml.bz2`
  - älterer Dump in "afrikaans" -> Dumps sind "richtige" Wikipediadumps, die aber klein und damit handlicher zur Untersuchung sind
- Präfix `sw11`:
  - originales Präfix dieses Dumps: `simplewiki-20111012` -> wurde hier zur Vermeidung langer Dateinamen umbenannt
  - Name des Artikeldumps: `sw11-pages-articles.xml.bz2`
  - Name des Historiendumps: `sw11-pages-meta-history.xml.bz2`
  - älterer Dump in einfachem Englisch -> der in der Arbeit untersuchte Dump
- Präfix `simple-collection`
  - Name des Artikeldumps: `simple-collection-pages-articles.xml.bz2`
  - Name des Historiendumps: `simple-collection-pages-meta-history.xml.bz2`
  - sehr kleiner, künstlich erzeugter Dump zum Testen auf Funktionalität
  - erzeugt aus der Datei `simple-collection.json`

Die beiden künstlichen `simple-collection`-Dumps können folgendermaßen erzeugt werden:
```
python3 -m scripts.utils.generate_xml_from_simple_json_collection simple-collection.json collections/simple-collection-pages-articles.xml collections/simple-collection-pages-meta-history.xml
bzip2 -zkf collections/simple-collection-pages-articles.xml collections/simple-collection-pages-meta-history.xml
```
         
Aufruf
------
Wikipedia-Cluster-Analysis besitzt acht zentrale Shellskripte im Wurzelverzeichnis des Projektes zur Erzeugung, Vergleich und Analyse von themenbasierten Clustern und autorenbasierten Communities. Alle zentralen Skripte werden durch die Parameter einer Konfigurationsdatei im `config`-Verzeichnis gesteuert. Das Format und die Beschreibung der Parameter ist in `config/simple-collection.config` enthalten. Eine Konfigurationsdatei legt z.B. die zu untersuchenden Clusteringrößen oder das Präfix der zu untersuchenden Dumps fest. 

Wikipedia-Cluster-Analysis enthält folgende zentrale Shellskripte:
- Bestimmung Namespaces -> erforderlich für themenbasierte Clusteranalyse und autorenbasierte Community Detection:
```
./run_namespaces.sh config/<PREFIX>.config
```
  
- themenbasierte Clusteranalyse: Erzeugung Bag-of-Words-Modell, Erzeugung Latent Dirichlet Allocation-Topicmodell, Bestimmung Cluster -> erforderlich für Berechnung zentralster Dokumente und Statistiken der themenbasierten Clusteranalyse:
```
./run_topic_clustering.sh config/<PREFIX>.config
```
  
- autorenbasierte Community Detection: Bestimmung Beitragswerte aus Historiendump, Erzeugung Affiliations- und Dokumentnetzwerk, Bestimmung Communities -> erforderlich für Berechnung zentralster Dokumente und Statistiken der autorenbasierten Community Detection:
```
./run_community_detection.sh config/<PREFIX>.config
```

- Berechnung der zentralsten Dokumente der themenbasierten Clusteranalyse -> erforderlich für Cluster-Community-Vergleich:
```
./run_centralities_topic.sh config/<PREFIX>.config
```
  
- Berechnung der zentralsten Dokumente der autorenbasierten Community Detection -> erforderlich für Cluster-Community-Vergleich:    
```
./run_centralities_community.sh config/<PREFIX>.config  
```
  
- Vergleich von Clustern und Communities (Normalized Mutual Information, Jaccard-Vergleich mit Titeln zentralster Dokumente):
```
./run_compare_clus_comm.sh config/<PREFIX>.config
```
  
- Berechnung verschiedener Statistiken (u.A. Plots) der themenbasierten Clusteranalyse:
```
./run_stats_topic.sh config/<PREFIX>.config
```

- Berechnung verschiedener Statistiken (u.A. Plots) der autorenbasierten Community Detection:    
```
./run_stats_community.sh config/<PREFIX>.config  
```

Verzeichnisse
-------------
- `bash`: Bash-Shellskripte
  - werden von den 6 wichtigen Shellskripten aufgerufen
  - rufen selbst wiederum die Pythonskripte in `scripts` auf
- `bin`: enthält die MALLET-Installation
- `collections`: Artikel- und Historiendumps der verschiedenen Wikipedia-Kollektionen
- `config`: Konfigurationsdateien der verschiedenen Wikipedia-Kollektionen
- `old`: einige alte, ggf. nützliche Skripte
- `output`: die von "Wikipedia-Cluster-Analysis" erzeugten Dateien
- `scripts`: die Pythonskripte
   
   
           
           
           
           