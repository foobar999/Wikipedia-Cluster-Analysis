import math
from io import StringIO
import numpy as np
from scripts.utils.utils import init_logger

logger = init_logger()

             
# erzeugt aus einem Mapping Objekt->Clusterlabel eine Liste von Mengen, die den Clustern entsprechen
def clustering_labels_to_sets(title_clustering):
    num_clusters = len(set(title_clustering.values()))
    clusters = [set() for _ in range(num_clusters)]
    for element,label in title_clustering.items():
        clusters[label].add(element)
    return clusters

    
# liefert K äquidistante Indizes von N Elementen 
def get_equidistant_indices(N, K):     
    logger.info('calculating K={} equidistant sample partition indices of N={} partitions'.format(N, K))
    if K > N:
        logger.warning('K is higher than N: setting K to N')
        K = N
    return [math.floor(k*(N-1)/(K-1)) for k in range(0,K)]
    

# liefert die größte Anzahl an zentralsten Dokumenttiteln, die ein Cluster in centrality_data_values besitzt
def get_max_num_titles_in_centrality_data(centrality_data_values):
    max_part_titles = max(len(clus['titles']) for clus in centrality_data_values)
    logger.info('at most {} central titles in given partitions'.format(max_part_titles))
    return max_part_titles
    

# erzeugt eine Matrix: jede Spalte entspricht einem Sample-Cluster, die 1. Zeile enthält dessen Größe, der Rest der Spalte enthält die zentralsten Dokumente
# die Höhe der Matrix ergibt sich aus der maximalen Anzahl zentralster Dokumente samples_centrality_data_values
def get_partitions_titles_matrix(samples_centrality_data_values):
    max_num_titles = get_max_num_titles_in_centrality_data(samples_centrality_data_values)
    titles_matrix = np.empty(shape=(max_num_titles+1, len(samples_centrality_data_values)), dtype=object)
    for i, part_centrality_data in enumerate(samples_centrality_data_values):
        titles_matrix[0,i] = '$n={}$'.format(part_centrality_data['size'])
        part_central_titles = part_centrality_data['titles']
        part_central_titles_padded = part_central_titles + [''] * (max_num_titles - len(part_central_titles))
        titles_matrix[1:,i] = part_central_titles_padded
    return titles_matrix
    
    
# loggt eine Matrix in CSV-Darstellung
def display_matrix_as_csv(titles_matrix):
    strf = StringIO()
    np.savetxt(strf, titles_matrix, delimiter=";", fmt="%s")
    logger.info('CSV sample partition titles \n{}'.format(strf.getvalue()))
    
    
    