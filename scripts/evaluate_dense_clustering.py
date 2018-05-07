import os, sys
import argparse
import logging
import json
from pprint import pformat
from gensim.corpora import MmCorpus
from gensim.models.ldamulticore import LdaMulticore
from gensim.matutils import corpus2dense
from gensim.utils import smart_open
import numpy as np
from utils.utils import init_logger
from sklearn.metrics import silhouette_score, calinski_harabaz_score
 
logger = init_logger()


def main():
    parser = argparse.ArgumentParser(description='calculates silhouette coefficient for a previous clustering')
    parser.add_argument('--bow', type=argparse.FileType('r'), help='path to text-based input bow file (.mm/.mm.bz2)', required=True)
    parser.add_argument('--tm', type=argparse.FileType('r'), help='gensim topic model prefix/path', required=True)
    parser.add_argument('--cluster-labels', type=argparse.FileType('r'), help='path to input .json cluster labels file', required=True)
    
    args = parser.parse_args()
    input_bow_path = args.bow.name
    input_tm_path = args.tm.name
    input_cluster_labels_path = args.cluster_labels.name
    
    logger.info('running with:\n{}'.format(pformat({'input_bow_path':input_bow_path, 'input_tm_path':input_tm_path, 'input_cluster_labels_path':input_cluster_labels_path})))
    
    logger.info('loading bow-corpus from {}'.format(input_bow_path))
    bow = MmCorpus(input_bow_path)
    logger.info('loaded bow-corpus {}'.format(bow))
    logger.info('loading topic model from {}'.format(input_tm_path))
    lda = LdaMulticore.load(input_tm_path)
    logger.info('loaded topic model {}'.format(lda))
    logger.info('combining both to dense document-topic-matrix')
    dense_bow_topics = corpus2dense(lda[bow], lda.num_topics, bow.num_docs).T  # TODO das wird nicht gestreamt -> probleme?
    logger.info('created dense matrix of shape {}'.format(dense_bow_topics.shape))
    logger.info('loading cluster labels from {}'.format(input_cluster_labels_path))
    with smart_open(input_cluster_labels_path, 'r') as ifile:
        labels_list = json.load(ifile)
    logger.info('loaded {} labels'.format(len(labels_list)))
    logger.debug(labels_list)
    labels = np.asarray(labels_list)
    
    logger.info('calclating unsupervised evaluation metrics')
    sil_score = silhouette_score(dense_bow_topics, labels, metric='euclidean') # groß=gut
    logger.info('euclidean silhouette coefficient: {}'.format(sil_score))
    ch_score = calinski_harabaz_score(dense_bow_topics, labels) # between-scatter durch within-scatter inkl. Straftermen -> groß=gut
    logger.info('calinski harabaz score: {}'.format(ch_score))
    
    
    
if __name__ == '__main__':
    main()
    
