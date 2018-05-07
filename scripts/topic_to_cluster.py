import os, sys
import argparse
import logging
import json 
from pprint import pformat
from gensim.corpora import MmCorpus
from gensim.models.ldamulticore import LdaMulticore
from gensim.matutils import corpus2dense
from gensim.utils import smart_open
from sklearn.cluster import MiniBatchKMeans
from utils.utils import init_logger
import numpy as np
 
logger = init_logger()
 

def main():
    parser = argparse.ArgumentParser(description='clusters documents of a corpus with k-means by applying a trained topic model to the corpus')
    parser.add_argument('--bow', type=argparse.FileType('r'), help='path to text-based input MatrixMarket bow corpus file (.mm/.mm.bz2)', required=True)
    parser.add_argument('--tm', type=argparse.FileType('r'), help='path to binary input topic model file', required=True)
    parser.add_argument('--cluster-labels', type=argparse.FileType('w'), help='path to output JSON cluster labels file', required=True)
    cluster_methods = {
        'kmeans': 'minibatch kmeans algorithm with kmeans++',
        'aggl': 'hierarchicalm agglomerative clustering'
    }
    parser.add_argument('--cluster-method', choices=cluster_methods, help='clustering algorithm: ' + str(cluster_methods), required=True)
    parser.add_argument('--num-clusters', type=int, help='number of clusters to create', required=True)
    parser.add_argument('--batch-size', type=int, help='size of mini batches', required=True)
    
    args = parser.parse_args()
    input_bow_path = args.bow.name
    input_tm_path = args.tm.name
    output_cluster_labels_path = args.cluster_labels.name
    cluster_method = args.cluster_method
    num_clusters = args.num_clusters
    batch_size = args.batch_size
    
    logger.info('running with:\n{}'.format(pformat({'input_bow_path':input_bow_path, 'input_tm_path':input_tm_path, 'output_cluster_labels_path':output_cluster_labels_path, 'cluster_method':cluster_method, 'num_clusters':num_clusters, 'batch_size':batch_size})))
        
    if cluster_method != 'kmeans':
        logger.error('{} not implemented'.format(cluster_method))
        return 1
        
    bow = MmCorpus(input_bow_path)
    tm = LdaMulticore.load(input_tm_path)
    dense = corpus2dense(tm[bow], tm.num_topics, bow.num_docs).T  # TODO das wird nicht gestreamt -> probleme?
    logger.debug('dense array:\n{}'.format(dense))
    verbose = 'DEBUG' in os.environ
    kmeans = MiniBatchKMeans(n_clusters=num_clusters, n_init=10, init='k-means++', max_iter=1000000, batch_size=batch_size, verbose=verbose, compute_labels=True)
    logger.info('running k-means on {} documents, {} topics, generating {} clusters'.format(bow.num_docs,tm.num_topics,num_clusters))
    logger.info(kmeans)
    cluster_labels = kmeans.fit_predict(dense)
    logger.info('{} labels'.format(len(cluster_labels)))
    logger.debug(cluster_labels)
    logger.info('writing labels to {}'.format(output_cluster_labels_path))
    with open(output_cluster_labels_path, 'w') as output_cluster_labels_file:
        json.dump(cluster_labels.tolist(), output_cluster_labels_file, indent=1)
    
if __name__ == '__main__':
    main()
    
