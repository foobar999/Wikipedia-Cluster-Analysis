import os, sys
import argparse
import logging
import json 
from pprint import pformat
from gensim.corpora import MmCorpus
from gensim.models.ldamulticore import LdaMulticore
from gensim.matutils import corpus2dense
from gensim.utils import smart_open
from sklearn.cluster import KMeans, AgglomerativeClustering
from utils.utils import init_logger, debug_mode_set
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
    parser = argparse.ArgumentParser(description='clusters documents of a corpus euclidean-based by applying a trained topic model to the corpus')
    parser.add_argument('--bow', type=argparse.FileType('r'), help='path to text-based input MatrixMarket bow corpus file (.mm/.mm.bz2)', required=True)
    parser.add_argument('--tm', type=argparse.FileType('r'), help='path to binary input topic model file', required=True)
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
    input_bow_path = args.bow.name
    input_tm_path = args.tm.name
    output_cluster_labels_path = args.cluster_labels.name
    cluster_method = args.cluster_method
    num_clusters = args.num_clusters
    
    logger.info('running with:\n{}'.format(pformat({'input_bow_path':input_bow_path, 'input_tm_path':input_tm_path, 'output_cluster_labels_path':output_cluster_labels_path, 'cluster_method':cluster_method, 'num_clusters':num_clusters})))
                
    logger.info('loading bow corpus from {}'.format(input_bow_path))
    bow = MmCorpus(input_bow_path)
    logger.info('loading topic model from {}'.format(input_tm_path))
    tm = LdaMulticore.load(input_tm_path)
    logger.info('combining both to dense document-topic-matrix')
    dense = corpus2dense(tm[bow], tm.num_topics, bow.num_docs).T  # TODO das wird nicht gestreamt -> probleme?
    logger.debug('dense array:\n{}'.format(dense))
    
    logger.info('cluestering on {} documents, {} topics, generating {} clusters'.format(bow.num_docs, tm.num_topics, num_clusters))
    cluster_model = get_cluster_model(cluster_method, num_clusters)
    logger.info('clustering model:\n{}'.format(cluster_model))
    
    cluster_labels = cluster_model.fit_predict(dense)
    logger.info('{} labels'.format(len(cluster_labels)))
    logger.debug(cluster_labels)
    logger.info('writing labels to {}'.format(output_cluster_labels_path))
    with open(output_cluster_labels_path, 'w') as output_cluster_labels_file:
        json.dump(cluster_labels.tolist(), output_cluster_labels_file, indent=1)
    
if __name__ == '__main__':
    main()
    
