
Installation
------------
- erfordert python3
- Installation benötigter Module:
```
pip3 install xmltodict scipy mediawiki_utilities numpy matplotlib networkx gensim python_igraph scripts scikit_learn
```
- genauere Angabe der benötigten Module in `requirements.txt`
- erfordert außerdem die Installation von MALLET 
  - Download: siehe http://mallet.cs.umass.edu/download.php
  - in der verwendeten Konfigurationsdatei muss die Variable MALLET_HOME auf das entpackte Verzeichnis gesetzt werden, beispielsweise:
    `MALLET_HOME=~/Projekte/Wikipedia-Cluster-Analysis/bin/mallet-2.0.8`
  - die im Speichermedium enthaltene Version von "Wikipedia-Cluster-Analysis" enthält eine MALLET-Installation im Verzeichnis `bin`
  
  
Dumps
-----
- Artikeldump der Form `collections/<PREFIX>-pages-articles.xml.bz2`
- Historiendump der Form `collections/<PREFIX>-pages-articles.xml.bz2`
- hier enthalten:
  - Präfix `af07`: entspricht `afwiki-20070124`
    - Name des Artikeldumps: `afwiki-20070124-pages-articles.xml.bz2`
    - Name des Historiendumps: `afwiki-20070124-pages-meta-history.xml.bz2`
    - älterer Dump in "afrikaans" -> Dumps sind "richtige" Wikipediadumps, die aber klein und damit handlicher zur Untersuchung sind
  - Präfix `sw11`: entspricht `simplewiki-20111012`
    - Name des Artikeldumps: `simplewiki-20111012-pages-articles.xml.bz2`
    - Name des Historiendumps: `simplewiki-20111012-pages-meta-history.xml.bz2`
    -> älterer Dump in einfachem Englisch -> der in der Arbeit untersuchte Dump
  - Präfix `simple-collection`
    - Name des Artikeldumps: `simple-collection-pages-articles.xml.bz2`
    - Name des Historiendumps: `simple-collection-pages-meta-history.xml.bz2`
    -> sehr kleiner, künstlich erzeugter Dump zum Testen auf Funktionalität
      - erzeugt aus der Datei `simple-collection.json`
      - wird erneut erzeugt durch:
```
python3 -m scripts.utils.generate_xml_from_simple_json_collection simple-collection.json collections/simple-collection-pages-articles.xml collections/simple-collection-pages-meta-history.xml
bzip2 -zkf collections/simple-collection-pages-articles.xml collections/simple-collection-pages-meta-history.xml
```
         
Aufruf
------
- 8 zentrale Shellskripte, die aufgerufen werden
- Angabe von Parametern in Konfigurationsdateien in `config`-Verzeichnis
  - Beschreibung der Parameter ist in `config/simple-collection.config` enthalten
  - Konfigurationsdateien steuern z.B. zu untersuchende Clusteringrößen, Präfix der zu untersuchenden Dumps, ...

- Bestimmung Namespaces -> erforderlich für themenbasierte Clusteranalyse und autorenbasierte Community Detection:
```
./run_namespaces.sh config/<PREFIX>.config
```
  
- themenbasierte Clusteranalyse: Erzeugung Bag-of-Words-Modell, Erzeugung Latent Dirichlet Allocation-Topicmodell, Bestimmung Cluster -> erforderlich für Berechnung Statistiken und Centrality der themenbasierten Clusteranalyse:
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
   
   
           
           
           
           