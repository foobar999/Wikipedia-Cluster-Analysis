import os, sys
import logging
import argparse
import json
from pprint import pformat
from gensim.utils import smart_open
from utils.utils import init_logger
import numpy as np
#from utils.mutual_information_scores import mutual_info_score, normalized_mutual_info_score, adjusted_rand_score
from sklearn.metrics import adjusted_rand_score, fowlkes_mallows_score, normalized_mutual_info_score, adjusted_mutual_info_score

logger = init_logger()
             

def load_clustering(clustering_path):
    with smart_open(clustering_path) as clustering_file:
        clustering = json.load(clustering_file)
        logger.debug('loaded clustering \n{}'.format(clustering))
        logger.info('loaded clustering of {} documents'.format(len(clustering)))
        return clustering
                 
score_funs = {
    'adjusted-rand': adjusted_rand_score,
    'fowlkes-mallows': fowlkes_mallows_score,
    'normalized-mutual-info': normalized_mutual_info_score,
    'adjusted-mutual-info': adjusted_mutual_info_score
}         
     
def main():
    parser = argparse.ArgumentParser(description='calculates a clustering comparison score of two clusterings/communitiy structures documenttitle->clusterlabel (comparison bases of intersection based on equal documenttitles)')
    parser.add_argument('--clusterings', nargs=2, type=argparse.FileType('r'), metavar=('CLUS1','CLUS2'), help='path to two titleclsuterings files (.json/.json.bz2)', required=True)
    
    args = parser.parse_args()
    input_clusterings_paths = (args.clusterings[0].name, args.clusterings[1].name)
    
    logger.info('running with:\n{}'.format(pformat({'input_clusterings_paths':input_clusterings_paths})))
    
    clustering1 = load_clustering(input_clusterings_paths[0])
    clustering2 = load_clustering(input_clusterings_paths[1])
    
    logger.info('intersecting clusterings by document titles')
    intersect_titles = sorted(clustering1.keys() & clustering2.keys())
    logger.debug('intersect titles \n{}'.format(intersect_titles))
    logger.info('number of intersect titles {}'.format(len(intersect_titles)))
    
    intsect_labels1 = [clustering1[title] for title in intersect_titles]
    logger.debug('labels of intersect titles in clustering 1 \n{}'.format(intsect_labels1))
    intsect_labels2 = [clustering2[title] for title in intersect_titles]
    logger.debug('labels of intersect titles in clustering 2 \n{}'.format(intsect_labels2))
    
    intsect_labels1 = np.array(intsect_labels1)
    intsect_labels2 = np.array(intsect_labels2)
    
    for score_name, score_fun in score_funs.items():
        score = score_fun(intsect_labels1, intsect_labels2)
        output = '{} {}'.format(score_name, score)
        logger.info(output)
        print(output)
        
        
        
if __name__ == '__main__':
    main()
