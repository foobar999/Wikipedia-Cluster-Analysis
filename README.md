Wikipedia-Cluster-Analysis
==========================
Das Projekt "Wikipedia-Cluster-Analysis" ermöglicht die Erzeugung, den Vergleich und die Analyse von themenbasierten Clusterings und autorenbasierten Communitystrukturen aus XML-Dumps von Wikipedia. 

Installation
------------
Wikipedia-Cluster-Analysis erfordert grundsätzlich `python3`. Außerdem benötigt Wikipedia-Cluster-Analysis Pythonmodule, die folgendermaßen installiert werden können:
```
pip3 install xmltodict scipy mediawiki_utilities numpy matplotlib networkx gensim python_igraph scripts scikit_learn
```
Eine genauere Angabe der verwendeten Module befindet sich in `requirements.txt`. Wikipedia-Cluster-Analysis benötigt außerdem eine heruntergeladene Version von 
"MALLET", zum Download siehe http://mallet.cs.umass.edu/download.php . Der Aufruf des Skripts zur themenbasiertern Clusteranalyse sowie des zugehörigen Statistikskripts erfordert, dass in der verwendeten Knofigurationsdatei die Variable MALLET_HOME auf das entpackte Verzeichnis gesetzt wird, z.B. `MALLET_HOME=~/Projekte/Wikipedia-Cluster-Analysis/bin/mallet-2.0.8`. Die im Speichermedium enthaltene Version von Wikipedia-Cluster-Analysis enthält eine MALLET-Installation im Verzeichnis `bin`.
  
Dumps
-----
Wikipedia-Cluster-Analysis geht von zwei Arten von Wikipediadumps aus, die sich im Verzeichnis `collections` befinden müssen: Einem Artikeldump der Form `collections/<PREFIX>-pages-articles.xml.bz2` und einem Historiendump der Form `collections/<PREFIX>-pages-articles.xml.bz2`. Zwei zusammengehörende Dumps bilden ein Paar mit demselben Präfix `<PREFIX>`. Die im Speichermedium enthaltene Version von Wikipedia-Cluster-Analysis enthält drei Paare von Dumps:
- Präfix `af07`: 
  - originales Präfix dieses Dumps: `afwiki-20070124` => wurde hier zur Vermeidung langer Dateinamen umbenannt
  - Name des Artikeldumps: `af07-pages-articles.xml.bz2`
  - Name des Historiendumps: `af07-pages-meta-history.xml.bz2`
  - älterer Dump in "afrikaans" => Dumps sind "richtige" Wikipediadumps, die aber klein und damit handlicher zur Untersuchung sind
- Präfix `sw11`:
  - originales Präfix dieses Dumps: `simplewiki-20111012` => wurde hier zur Vermeidung langer Dateinamen umbenannt
  - Name des Artikeldumps: `sw11-pages-articles.xml.bz2`
  - Name des Historiendumps: `sw11-pages-meta-history.xml.bz2`
  - älterer Dump in einfachem Englisch => der in der Arbeit untersuchte Dump
- Präfix `simple-collection`:
  - Name des Artikeldumps: `simple-collection-pages-articles.xml.bz2`
  - Name des Historiendumps: `simple-collection-pages-meta-history.xml.bz2`
  - sehr kleiner, künstlich erzeugter Dump zum Testen auf Funktionalität
  - erzeugt aus der Datei `simple-collection.json`

Die Online-Version von Wikipedia-Cluster-Analysis enthält nur die beiden `simple-collection`-Dumps. Die beiden `simple-collection`-Dumps können folgendermaßen erzeugt werden:
```
python3 -m scripts.utils.generate_xml_from_simple_json_collection simple-collection.json collections/simple-collection-pages-articles.xml collections/simple-collection-pages-meta-history.xml
bzip2 -zkf collections/simple-collection-pages-articles.xml collections/simple-collection-pages-meta-history.xml
```
         
Verzeichnisse
-------------
- `bash`: Bash-Shellskripte
  - werden von den zentralen Shellskripten im Wurzelverzeichnis aufgerufen
  - rufen selbst wiederum die Pythonskripte in `scripts` auf
- `bin`: enthält die MALLET-Installation
- `collections`: Artikel- und Historiendumps der verschiedenen Wikipedia-Kollektionen
- `config`: Konfigurationsdateien der verschiedenen Wikipedia-Kollektionen
- `old`: einige alte, ggf. nützliche Skripte
- `output`: die von "Wikipedia-Cluster-Analysis" erzeugten Dateien
- `scripts`: die Pythonskripte
         
Aufruf
------
Wikipedia-Cluster-Analysis besitzt acht zentrale Shellskripte im Wurzelverzeichnis des Projektes zur Erzeugung, Vergleich und Analyse von themenbasierten Clustern und autorenbasierten Communities. Alle zentralen Skripte werden durch die Parameter einer Konfigurationsdatei im `config`-Verzeichnis gesteuert. Das Format und die Beschreibung der Parameter ist in `config/simple-collection.config` enthalten. Eine Konfigurationsdatei legt z.B. die zu untersuchenden Clusteringrößen oder das Präfix der zu untersuchenden Dumps fest. 

Das Skript `run_namespaces.sh` ermöglicht die Bestimmung der im Historiendump enthaltenen Namensräume:
```
./run_namespaces.sh config/<PREFIX>.config <MIN_OCCURENCES>
```
Danach ist eine manuelle Filterung der gefundenen Namensräume in der erzeugten Liste `output/<PREFIX>-namespaces.txt` von Namensraumpräfixen erforderlich (siehe Abschnitt "Bestimmung Namensräume" unten). Da die Liste von Namensraumpräfixen in der Online- und in der Speichermedium-Version von Wikipedia-Cluster-Analysis enthalten ist, kann auf den Aufruf von `run_namespaces.sh` verzichtet werden. Die Bestimmung der Namensräume ist für die themenbasierte Clusteranalyse und autorenbasierte Community Detection erforderlich.
  
Das Skript `run_topic_clustering.sh` führt die themenbasierte Clusteranalyse durch:
```
./run_topic_clustering.sh config/<PREFIX>.config
```
Dies beinhaltet die Erzeugung des Bag-of-Words-Modells (BOW), die Erzeugung des Latent Dirichlet Allocation-Topicmodells (LDA) und die Bestimmung der Cluster. Die themenbasierte Clusteranalyse ist erforderlich für die zugehörige Berechnung zentralster Dokumente und Statistiken.
  
Das Skript `run_community_detection.sh` führt die autorenbasierte Community Detection durch: 
```
./run_community_detection.sh config/<PREFIX>.config
```
Dies beinhaltet die Bestimmung der Beitragswerte, die Erzeugung des Affiliations- und Dokumentnetzwerkes und Bestimmung der Communities. Die autorenbasierte Community Detection ist erforderlich für die zugehörige Berechnung zentralster Dokumente und Statistiken.

Das Skript `run_centralities_topic.sh` berechnet die zentralsten Dokumente der themenbasierten Clusteranalyse:
```
./run_centralities_topic.sh config/<PREFIX>.config
```
Die Berechnung der zentralsten Dokumente der themenbasierten Clusteranalyse ist erforderlich für den Cluster-Community-Vergleich.
  
Das Skript `run_centralities_community.sh` berechnet die zentralsten Dokumente der autorenbasierten Community Detection:
```
./run_centralities_community.sh config/<PREFIX>.config  
```
Die Berechnung der zentralsten Dokumente der autorenbasierten Community Detection ist erforderlich für den Cluster-Community-Vergleich.
  
Das Skript `run_compare_clus_comm.sh` vergleicht berechnete Cluster und Communities:
```
./run_compare_clus_comm.sh config/<PREFIX>.config
```
Der Vergleich von Clusterings und Communitystrukturen erfolgt mit Normalized Mutual Information. Außerdem bestimmt das Skript Jaccard-ähnlichste Cluster-Community-Paare und repräsentiert Cluster und Communities mit den Titeln ihrer zentralsten Dokumente.

  
Das Skript `run_stats_topic.sh` berechnet verschiedene Statistiken (u.A. Plots) der themenbasierten Clusteranalyse:
```
./run_stats_topic.sh config/<PREFIX>.config
```

Das Skript `run_stats_community.sh` berechnet verschiedener Statistiken (u.A. Plots) der autorenbasierten Community Detection:    
```
./run_stats_community.sh config/<PREFIX>.config  
```

Test
----
Die Funktionalität von Wikipedia-Cluster-Analysis kann mithilfe der vorliegenden `simple-collection`-Dumps einfach getestet werden:
```
./run_namespaces.sh config/simple-collection.config 1
./run_topic_clustering.sh config/simple-collection.config
./run_community_detection.sh config/simple-collection.config
./run_centralities_topic.sh config/simple-collection.config
./run_centralities_community.sh config/simple-collection.config  
./run_compare_clus_comm.sh config/simple-collection.config
./run_stats_topic.sh config/simple-collection.config
./run_stats_community.sh config/simple-collection.config 
```

Ausgabe
-------
Die Ergebnisse der verschiedenen Skriptaufrufe befinden sich im Verzeichnis `output`. Dieses Verzeichnis enthält folgende Verzeichnisse und Dateien:
- `output/<PREFIX>-namespaces.txt`: Listen der Namensraumpräfixe 
- `output/bow`: Dateien des BOW-Modells: BOW-Matrix, Vokabular, Dokumenttitel
- `output/topic`: Dateien des LDA-Topicmodells: Modellinstanz-Dateien, Matrix der Dokument-Topic-Anteile
- `output/clusters`: Dateien der themenbasierten Clusterings: Dokument-Cluster-Label, Dokumenttitel-Cluster-Label
- `output/contribs`: Dateien der Beitragswerte: rohe/akkumulierte Beiträge, Autornamen, Dokumenttitel
- `output/graph`: Dateien der Graphen: Affiliationsnetzwerk, Co-Authorship-Dokumentnetzwerk
- `output/communities`: Dateien der autorenbasierten Communities: Dokument-Community-Label, Dokumenttitel-Community-Label
- `output/logs`: Logfiles der verschiedenen Schritte
- `output/stats`: Dateien von Statistiken und Cluster-Community-Vergleichen

Bestimmung Namensräume
---------------------
Die Bestimmung der Namensräume ist für themenbasierte Clusteranalyse und autorenbasierte Community Detection notwendig, da beide Prozesse auf den Artikeln der Wikipediadumps beruhen. Artikeldumps und Historiendumps enthalten Seiten eines Standes von Wikipedia, die Artikel sind die Seiten im Namensraum 0 ("Mainspace"). Beide Arten von Dumps speichern Angaben zu den enhaltenen Seiten als große XML-Datenstruktur, jede Seite liegt in der Form `<page>...</page>` vor. In modernen XML-Wikipediadumps ist je Seite durch das XML-Tag `<ns>...</ns>` explizit angegeben, zu welchem Namensraum diese Seite gehört (ein Beispiel befindet sich in https://en.wikipedia.org/wiki/Help:Export#Example). Diese Angabe ermöglicht eine einfache Bestimmung des Namensraumes einer Seite, fehlt aber in den hier verwendeten, älteren Dumps. Wikipedia-Cluster-Analysis verwendet daher zur Überprüfung, ob eine Seite im Mainspace liegt oder nicht, den Titel der Seite. Der Titel einer Seite, die nicht im Mainspace liegt, besitzt das Präfix `<NAMESPACE>:`. Dies ist z.B. am Titel der Seite https://en.wikipedia.org/wiki/Help:Export, die im Namensraum `Help` liegt, und am Titel der Seite https://en.wikipedia.org/wiki/Template:Article_creation, die im Namensraum `Template` liegt, erkennbar. Um zu bestimmen, ob eine Seite im Mainspace liegt, ist eine einfache Überprüfung, ob der Seitentitel mit einem String gefolgt von `:` beginnt, allerdings nicht sinnvoll: Es ist auch möglich, dass Seiten im Mainspace ein Präfix `<STRING>:` besitzen, ohne dass dieses Präfix einem Namensraum entspricht (wie z.B. in https://de.wikipedia.org/wiki/CSI:_Vegas). Daher prüft Wikipedia-Cluster-Analysis, ob eine Seite im Mainspace liegt, folgendermaßen:

1. Falls die Seite im Dump eine explizite Namensraumangabe der Form `<ns>...</ns>` besitzt: Die Seite gehört zum Mainspace, falls die Angabe `<ns>0</ns>` ist, ansonsten gehört sie nicht zum Mainspace.
2. Falls die Seite im Dump keine explizite Namensraumangabe besitzt: Die Seite gehört nicht zum Mainspace, falls der Titel mit einem Präfix `<NAMESPACE>:` beginnt, das in einer vordefinierten Liste von Namensräumen enthalten ist. Ansonsten gehört die Seite zum Mainspace.

Die Erstellung der dafür benötigten Liste von Namensräumen ist anhand der online angegebenen Namensräume https://en.wikipedia.org/wiki/Wikipedia:Namespace möglich. Diese Methode zur Erstellung der Liste besitzt den Nachteil, dass die online angegebenen Namensräume von den in den Dumps verwendeten Namensräumen abweichen können. Erschwerend kommt hinzu, dass Namensräume durch "Aliasse" abgekürzt werden können https://en.wikipedia.org/wiki/Wikipedia:Namespace#Aliases_and_pseudo-namespaces_2. Daher bestimmt Wikipedia-Cluster-Analysis die Liste der Namensräume aus allen Titelpräfixen `<STRING>:`, die im Historiendump vorliegen (die Seiten des Historiendump bilden eine Obermenge der Seiten des Artikeldumps). Der Aufruf `./run_namespaces.sh config/<PREFIX>.config <MIN_OCCURENCES>` liefert alle Titelpräfixe, die im konfigurierten Historiendump mindestens `<MIN_OCCURENCES>`-mal enthalten sind, als Datei `output/<PREFIX>-namespaces.txt`. Danach ist eine manuelle Entfernung aller Titelpräfixe, die keinen Namensräumen entsprechen, in dieser Datei erforderlich. Titelpräfixe, die einem Namensraum entsprechen, enthalten typischerweise mehr zugehörige Seiten als Titelpräfixe, die keinem Namensraum entsprechen. Je kleiner der Wert für `<MIN_OCCURENCES>`, desto mehr Titelpräfixe müssen entfernt werden, die keinem Namensraum entsprechen. Ein zu hoher Wert für `<MIN_OCCURENCES>` ignoriert möglicherweise Namensräume, in denen wenige Seiten enthalten sind. 




 












           
           
           
           