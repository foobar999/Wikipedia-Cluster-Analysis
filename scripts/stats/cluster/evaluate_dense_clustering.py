import os, sys
import argparse
import json
import bz2
import numpy as np
from sklearn.metrics import silhouette_score, calinski_harabaz_score
from sklearn.metrics.pairwise import _VALID_METRICS 
from scripts.utils.utils import init_logger, load_npz
 
logger = init_logger()


def main():
    parser = argparse.ArgumentParser(description='calculates silhouette coefficient of a given clustering and its document-topic-matrix')
    parser.add_argument('--document-topics', type=argparse.FileType('r'), help='path to input document-topic-file (.npz)', required=True)
    parser.add_argument('--cluster-labels', type=argparse.FileType('r'), help='path to input .json.bz2 cluster labels file', required=True)
    parser.add_argument('--metric', choices=_VALID_METRICS, help='distance function to use', required=True)
    
    args = parser.parse_args()
    input_document_topics_path = args.document_topics.name
    input_cluster_labels_path = args.cluster_labels.name
    metric = args.metric
    
    logger.info('loading dense document-topics from {}'.format(input_document_topics_path))
    document_topics = load_npz(input_document_topics_path)
    logger.info('loaded document-topics-matrix of shape {}'.format(document_topics.shape))
    logger.debug('document-topics-matrix \n{}'.format(document_topics))
    
    logger.info('loading cluster labels from {}'.format(input_cluster_labels_path))
    with bz2.open(input_cluster_labels_path,'rt') as ifile:
        labels_list = json.load(ifile)
    logger.info('loaded {} labels'.format(len(labels_list)))
    logger.debug(labels_list)
    labels = np.asarray(labels_list)
    
    logger.info('calclating unsupervised evaluation metrics')
    sil_score = silhouette_score(document_topics, labels, metric=metric) # groß=gut
    logger.info('{} silhouette coefficient: {}'.format(metric, sil_score))
    ch_score = calinski_harabaz_score(document_topics, labels) # between-scatter durch within-scatter inkl. Straftermen -> groß=gut
    logger.info('calinski harabaz score: {}'.format(ch_score))
    
    
    
if __name__ == '__main__':
    main()
    