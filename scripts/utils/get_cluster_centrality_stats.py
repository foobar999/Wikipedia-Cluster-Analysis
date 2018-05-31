import os, sys
import logging
import argparse
import math
from io import StringIO
import numpy as np
from scipy.spatial.distance import cdist
from utils import init_logger, load_document_topics, load_cluster_labels, load_titles

logger = init_logger()


def get_clusters_from_labels(cluster_labels):
    num_clusters = len(np.unique(cluster_labels))
    logger.info('number of clusters {}'.format(num_clusters))
    clusters = [[] for _ in range(num_clusters)]
    for docid,label in enumerate(cluster_labels):
        clusters[label].append(docid)
    logger.debug('clusters \n{}'.format(clusters))
    return clusters
            

def get_clusters_of_min_size(id_clusters, J):     
    id_clusters = sorted(id_clusters, key=lambda t:len(t[1]), reverse=True)
    logger.debug('cluster sizes, sorted descending\n{}'.format([len(cluster) for clusterid,cluster in id_clusters]))
    logger.info('filtering to clusters of at least {} nodes'.format(J))
    id_clusters = [(clusterid,cluster) for clusterid,cluster in id_clusters if len(cluster) >= J]
    logger.info('filtered to {} cluster'.format(len(id_clusters)))     
    return id_clusters
    
    
def get_clusters_of_equaldistant_sizes(id_clusters, K):
    N = len(id_clusters)
    logger.info('calculating considered clusters number with N={}, considering K={} equidistant clusters'.format(N, K))
    considered_indices = [math.floor(k*(N-1)/(K-1)) for k in range(0,K)]
    logger.info('considering indices {}'.format(considered_indices))
    considered_clusters = [id_clusters[i][1] for i in considered_indices]
    logger.info('considering {} clusters with sizes {}'.format(len(considered_clusters), [len(cluster) for cluster in considered_clusters]))
    return considered_clusters
    
     
def get_top_central_cluster_docs(cluster, document_topics, J):
    logger.info('cluster of size {}: finding {} nearest docs to centroid'.format(len(cluster), J))
    cluster_documents = document_topics[cluster]
    logger.debug('submatrix shape {}'.format(cluster_documents.shape))
    cluster_centroid = np.mean(cluster_documents, axis=0)
    cluster_centroid = cluster_centroid.reshape((1,len(cluster_centroid)))
    logger.debug('cluster centroid shape {}'.format(cluster_centroid.shape))
    document_centroid_dists = cdist(cluster_documents, cluster_centroid, metric='euclidean').flatten()
    logger.debug('nearest index {}'.format(np.argmin(document_centroid_dists)))
    logger.debug('document_centroid_dists shape {}'.format(document_centroid_dists.shape))
    central_doc_indices = np.argsort(document_centroid_dists)[:J].tolist()
    logger.debug('central_doc_indices {}'.format(central_doc_indices))
    central_docids = [cluster[i] for i in central_doc_indices]
    logger.debug('central doc ids {}'.format(central_docids))
    return central_docids
     
     
def get_document_titles(docids, document_titles):
    return [document_titles[str(docid)] for docid in docids]
    
     
def main():
    parser = argparse.ArgumentParser(description='creates a file of clusterings: clusters are sorted descending by size, cluster elements are sorted by distance to cluster centroid')    
    parser.add_argument('--document-topics', type=argparse.FileType('r'), help='path to input document-topic-file (.npz)', required=True)
    parser.add_argument('--cluster-labels', type=argparse.FileType('r'), help='path to input .json.bz2 clustering file', required=True)
    parser.add_argument('--titles', type=argparse.FileType('r'), help='path to input .json.bz2 titles file', required=True)    
    parser.add_argument('--K', type=int, help='number of considered, equaldistant clusters 0,floor(1*(N-1)/K),...,N-1', required=True)
    parser.add_argument('--J', type=int, help='maxiumum number of highest clusters nodes per community', required=True)
    
    args = parser.parse_args()
    input_document_topics_path = args.document_topics.name
    input_cluster_labels_path = args.cluster_labels.name
    input_titles_path = args.titles.name
    K = args.K
    J = args.J
        
    document_topics = load_document_topics(input_document_topics_path)
    cluster_labels = load_cluster_labels(input_cluster_labels_path)
    document_titles = load_titles(input_titles_path)
        
    clusters = get_clusters_from_labels(cluster_labels)
    id_clusters = list(enumerate(clusters))
    logger.debug('id_clusters \n{}'.format(id_clusters))
    
    id_clusters = get_clusters_of_min_size(id_clusters, J)
    considered_clusters = get_clusters_of_equaldistant_sizes(id_clusters, K)
        
    matrix = np.empty(shape=(J+1,len(considered_clusters)), dtype=object)
    for i, cluster in enumerate(considered_clusters):
        matrix[0,i] = '$n={}$'.format(len(cluster))
        central_docids = get_top_central_cluster_docs(cluster, document_topics, J)
        central_titles = get_document_titles(central_docids, document_titles)
        logger.info('top-{}-central titles of cluster:'.format(J))
        for title in central_titles:
            logger.info(title)
        matrix[1:,i] = central_titles
    strf = StringIO()
    np.savetxt(strf, matrix, delimiter=";", fmt="%s")
    logger.info('CSV \n{}'.format(strf.getvalue()))
        
        
if __name__ == '__main__':
    main()
