import os, sys
import argparse
import logging
import json 
from pprint import pformat
from sklearn.cluster import KMeans, AgglomerativeClustering
from utils.utils import init_logger, debug_mode_set, load_npz
import numpy as np
 
logger = init_logger()
 
 
def get_cluster_model(cluster_method, num_clusters):
    if cluster_method == 'kmeans':
        return KMeans(n_clusters=num_clusters, n_init=10, init='k-means++', max_iter=1000000, verbose=False)
    if cluster_method.startswith('aggl'):
        linkages = {
            'aggl-ward': 'ward',
            'aggl-avg': 'average',
            'aggl-compl': 'complete'
        }
        return AgglomerativeClustering(n_clusters=num_clusters, linkage=linkages[cluster_method], affinity='euclidean')
 

def main():
    parser = argparse.ArgumentParser(description='clusters documents of a given document-topics-file by euclidean distance of their topics')
    parser.add_argument('--document-topics', type=argparse.FileType('r'), help='path to input document-topic-file (.npz)', required=True)
    parser.add_argument('--cluster-labels', type=argparse.FileType('w'), help='path to output JSON cluster labels file', required=True)
    cluster_methods = {
        'kmeans': 'kmeans algorithm with kmeans++',
        'aggl-ward': 'hierarchical agglomerative ward clustering',
        'aggl-avg': 'hierarchical agglomerative average clustering',
        'aggl-compl': 'hierarchical agglomerative complete clustering',
    }
    parser.add_argument('--cluster-method', choices=cluster_methods, help='clustering algorithm: ' + str(cluster_methods), required=True)
    parser.add_argument('--num-clusters', type=int, help='number of clusters to create', required=True)
    
    args = parser.parse_args()
    input_document_topics_path = args.document_topics.name
    output_cluster_labels_path = args.cluster_labels.name
    cluster_method = args.cluster_method
    num_clusters = args.num_clusters
    
    logger.info('running with:\n{}'.format(pformat({'input_document_topics_path':input_document_topics_path, 'output_cluster_labels_path':output_cluster_labels_path, 'cluster_method':cluster_method, 'num_clusters':num_clusters})))
                
    logger.info('loading dense document-topics from {}'.format(input_document_topics_path))
    document_topics = load_npz(input_document_topics_path)
    logger.info('loaded document-topics-matrix of shape {}'.format(document_topics.shape))
    logger.debug('document-topics-matrix \n{}'.format(document_topics))
    
    num_docs, num_topics = document_topics.shape
    logger.info('cluetering on {} documents, {} topics, generating {} clusters'.format(num_docs, num_topics, num_clusters))
    cluster_model = get_cluster_model(cluster_method, num_clusters)
    logger.info('clustering model:\n{}'.format(cluster_model))
    
    cluster_labels = cluster_model.fit_predict(document_topics)
    logger.info('{} labels'.format(len(cluster_labels)))
    logger.debug(cluster_labels)
    logger.info('writing labels to {}'.format(output_cluster_labels_path))
    with open(output_cluster_labels_path, 'w') as output_cluster_labels_file:
        json.dump(cluster_labels.tolist(), output_cluster_labels_file, indent=1)
    
    
if __name__ == '__main__':
    main()
    
