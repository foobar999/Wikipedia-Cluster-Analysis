import math
from scripts.utils.utils import init_logger

logger = init_logger()

             
# erzeugt aus einem Mapping Objekt->Clusterlabel eine Liste von Mengen, die den Clustern entsprechen
def clustering_labels_to_sets(title_clustering):
    num_clusters = len(set(title_clustering.values()))
    clusters = [set() for _ in range(num_clusters)]
    for element,label in title_clustering.items():
        clusters[label].add(element)
    return clusters

    
# liefert die Indizies von K äquidistanten Elementen elements
def get_equidistant_indices(elements, K):     
    N = len(elements)
    logger.info('calculating K={} equidistant sample partition indices of N={} partitions'.format(N, K))
    if K > N:
        logger.warning('K is higher than N: setting K to N')
        K = N
    return [math.floor(k*(N-1)/(K-1)) for k in range(0,K)]
    

# liefert die größte Anzahl an zentralsten Dokumenttiteln, die ein Cluster in centrality_data besitzt
def get_max_num_titles_in_centrality_data(centrality_data):
    max_part_titles = max(len(clus['titles']) for clus in centrality_data.values())
    logger.info('at most {} central titles in given partitions'.format(max_part_titles))
    return max_part_titles