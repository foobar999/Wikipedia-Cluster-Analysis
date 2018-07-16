import argparse
from pprint import pformat
import numpy as np
from sklearn.cluster import KMeans, AgglomerativeClustering
from scripts.utils.utils import init_logger, load_npz, save_data_to_json
 
logger = init_logger()
 
 
# liefert zum Clusterverfahren cluster_method das passende sklearn-Cluster-Modell, das num_clusters Clusters erzeugt
# cluster_method == 'kmeans' -> liefert sklearn-K-Means
# cluster_method == aggl-avg[-cos] -> liefert sklearn-AgglomerativeClustering mit euklidischer Distanz [mit Kosinusunähnlichkeit]
# cluster_method == aggl-ward -> liefert sklearn-AgglomerativeClustering mit Ward-Clustering
def get_cluster_model(cluster_method, num_clusters):
    if cluster_method == 'kmeans':
        return KMeans(n_clusters=num_clusters, n_init=10, init='k-means++', max_iter=1000000, verbose=False, n_jobs=-1)
    if cluster_method.startswith('aggl'):
        linkages = {
            'aggl-ward': 'ward',
            'aggl-avg': 'average',
            'aggl-avg-cos': 'average',
        }
        affinites = {
            'aggl-ward': 'euclidean',
            'aggl-avg': 'euclidean',
            'aggl-avg-cos': 'cosine',
        }
        # AgglomerativeClustering legt im Verzeichnis ".cache" einen Cache des Dendrogramms an -> verkürzt Berechnungsdauer erheblich, wenn 
        # verschiedene Clusteranzahlen desselben Dendrogramms gesucht!
        return AgglomerativeClustering(n_clusters=num_clusters, linkage=linkages[cluster_method], affinity=affinites[cluster_method], memory='.cache')
 

def main():
    parser = argparse.ArgumentParser(description='clusters documents of a given document-topics-file by their topics')
    parser.add_argument('--document-topics', type=argparse.FileType('r'), help='path to input document-topic-file (.npz)', required=True)
    parser.add_argument('--cluster-labels', type=argparse.FileType('w'), help='path to output JSON cluster labels file', required=True)
    cluster_methods = {
        'kmeans': 'kmeans algorithm with kmeans++',
        'aggl-ward': 'hierarchical agglomerative ward clustering',
        'aggl-avg': 'hierarchical agglomerative average clustering',
        'aggl-avg-cos': 'hierarchical agglomerative average clustering with cosine distance',
    }
    cm = parser.add_argument('--cluster-method', choices=cluster_methods, help='clustering algorithm: ' + str(cluster_methods), required=True)
    parser.add_argument('--num-clusters', type=int, help='number of clusters to create', required=True)
    
    args = parser.parse_args()
    input_document_topics_path = args.document_topics.name
    output_cluster_labels_path = args.cluster_labels.name
    cluster_method = args.cluster_method
    num_clusters = args.num_clusters
    
    logger.info('running with:\n{}'.format(pformat({'input_document_topics_path':input_document_topics_path, 'output_cluster_labels_path':output_cluster_labels_path, 'cluster_method':cluster_method, 'num_clusters':num_clusters})))
           
    # lade Dokument-Topic-Matrix
    logger.info('loading dense document-topics from {}'.format(input_document_topics_path))
    document_topics = load_npz(input_document_topics_path)
    logger.info('loaded document-topics-matrix of shape {}'.format(document_topics.shape))
    logger.debug('document-topics-matrix \n{}'.format(document_topics))
    
    # hole Modell zu cluster_method, num_clusters
    num_docs, num_topics = document_topics.shape
    logger.info('clustering on {} documents, {} topics'.format(num_docs, num_topics))
    cluster_model = get_cluster_model(cluster_method, num_clusters)
    logger.info('clustering model:\n{}'.format(cluster_model))
    
    # führe Clusteranalyse durch
    cluster_labels = cluster_model.fit_predict(document_topics)
    logger.info('{} labels'.format(len(cluster_labels)))
    logger.debug(cluster_labels)
    logger.info('{} different labels'.format(len(np.unique(cluster_labels))))
    logger.info('{} noise labels'.format((cluster_labels < 0).sum()))
    
    # speichere Labels
    logger.info('saving cluster labels')
    save_data_to_json(cluster_labels.tolist(), output_cluster_labels_path)
    
    
if __name__ == '__main__':
    main()
    
