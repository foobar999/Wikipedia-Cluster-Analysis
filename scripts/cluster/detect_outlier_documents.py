import os, sys
import argparse
import json 
import numpy as np
from sklearn.neighbors import LocalOutlierFactor, NearestNeighbors
from scripts.utils.utils import init_logger 
from scripts.utils.documents import load_document_topics
 
logger = init_logger()
 

# https://github.com/scikit-learn/scikit-learn/blob/master/sklearn/neighbors/lof.py
def local_reachability_density(neighbors_distances, neighbors_indices, k):
    dist_k = neighbors_distances[neighbors_indices, k-1]
    reach_dist_array = np.maximum(neighbors_distances, dist_k)
    return 1. / (np.mean(reach_dist_array, axis=1) + 1e-10)
 
def local_outlier_factor(neighbors_distances, neighbors_indices, k):
    lrd = local_reachability_density(neighbors_distances, neighbors_indices, k)
    lrd_ratios_array = (lrd[neighbors_indices] / lrd[:, np.newaxis])
    return np.mean(lrd_ratios_array, axis=1)
 
def calc_max_lof_of_bounds(document_topics, metric, k_min, k_max):    
    num_docs = document_topics.shape[0]
    max_outlier_scores = np.zeros(num_docs)
    logger.info('calculating max outlier scores: k_min={}, k_max={}'.format(k_min, k_max))    
    model = LocalOutlierFactor(n_neighbors=k_max, metric=metric, n_jobs=2)
    logger.info('creating k_max-model {}'.format(model))
    model.fit(document_topics)
    neighbors_distances_k_max, neighbors_indices_k_max = (model.kneighbors(None, n_neighbors=k_max))
    max_outlier_scores = np.zeros(num_docs)
    for k in range(k_min, k_max+1):
        logger.debug('calculating {}-scores'.format(k))
        neighbors_distances = neighbors_distances_k_max[:,0:k]
        neighbors_indices = neighbors_indices_k_max[:,0:k]
        outlier_scores = local_outlier_factor(neighbors_distances, neighbors_indices, k)
        max_outlier_scores = np.maximum(max_outlier_scores, outlier_scores)
    return max_outlier_scores
 
def main():
    parser = argparse.ArgumentParser(description='calculates local outlier factors of given documents')
    parser.add_argument('--document-topics', type=argparse.FileType('r'), help='path to input document-topic-file (.npz)', required=True)
    parser.add_argument('--outlier-scores', type=argparse.FileType('w'), help='path to output JSON outlier scores file (.json)', required=True)
    parser.add_argument('--k-min', type=int, help='minimum number of considered neighbors per sample', required=True)
    parser.add_argument('--k-max', type=int, help='maximum number of considered neighbors per sample', required=True)
    parser.add_argument('--metric', help='distance metric of outlier detection', required=True)
    
    args = parser.parse_args()
    input_document_topics_path = args.document_topics.name
    output_outlier_scores_path = args.outlier_scores.name
    k_min, k_max = args.k_min, args.k_max
    metric = args.metric
    
    document_topics = load_document_topics(input_document_topics_path)    
    outlier_scores = calc_max_lof_of_bounds(document_topics, metric, k_min, k_max)
    logger.info('calculated {} LOF-scores'.format(len(outlier_scores)))
    logger.debug('scores \n{}'.format(outlier_scores))
    
    logger.info('writing scores to {}'.format(output_outlier_scores_path))
    with open(output_outlier_scores_path, 'w') as output_outlier_scores_file:
        json.dump(outlier_scores.tolist(), output_outlier_scores_file, indent=1)
    
    
if __name__ == '__main__':
    main()
    