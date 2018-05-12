import os, sys
import logging
import argparse
import json
from pprint import pformat
from gensim.utils import smart_open
from utils.utils import init_logger
import numpy as np
from sklearn.metrics import *

logger = init_logger()
             

def load_clustering(clustering_path):
    with smart_open(clustering_path) as clustering_file:
        clustering = json.load(clustering_file)
        logger.debug('loaded clustering \n{}'.format(clustering))
        logger.info('loaded clustering of {} documents'.format(len(clustering)))
        return clustering
           
           
     
def main():
    parser = argparse.ArgumentParser(description='calculates multiple clustering comparison scores of two clusterings/communitiy structures documenttitle->clusterlabel (comparison bases of intersection based on equal documenttitles)')
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
    
    score_funs = {
        'nmi': normalized_mutual_info_score,
        'ami': adjusted_mutual_info_score
    }    
    for score_name, score_fun in score_funs.items():
        logger.info('{} {}'.format(score_name, score_fun(intsect_labels1, intsect_labels2)))
        
        
        
if __name__ == '__main__':
    main()
