import os, sys
import logging
import argparse
import json
import bz2
from pprint import pformat
from utils.utils import init_logger
import numpy as np
import matplotlib.pyplot as plt

logger = init_logger()
             
     
def main():
    parser = argparse.ArgumentParser(description='calculates a graph of descending community sizes and writes it to an img file')
    parser.add_argument('--communities', type=argparse.FileType('r'), help='path to input .json.bz2 communities file', required=True)
    parser.add_argument('--img', type=argparse.FileType('w'), help='path of output img file', required=True)
    
    args = parser.parse_args()
    input_communities_path = args.communities.name
    output_img_path = args.img.name
    
    logger.info('running with:\n{}'.format(pformat({'input_communities_path':input_communities_path, 'output_img_path':output_img_path})))
    
    with bz2.open(input_communities_path, 'rt') as input_communities_file:
        communities = json.load(input_communities_file)
        
    logger.info('{} communities'.format(len(communities)))
    logger.debug('communities \n{}'.format(communities))
        
    labels,counts = np.unique(list(communities.values()), return_counts=True)
    logger.info('{} different communities'.format(labels.shape[0]))
    logger.debug('labels \n{}'.format(labels))
    logger.debug('counts \n{}'.format(counts))
        
    counts[::-1].sort()
   
    plt.rc('font',family='Calibri')     
    plt.figure(figsize=(6,2))
    plt.xlabel('Communities')
    plt.ylabel('Anzahl Knoten')
    plt.scatter(np.arange(len(counts)), counts, c='b', s=7.5)
    logger.info('writing to {}'.format(output_img_path))
    plt.savefig(output_img_path, bbox_inches='tight')
    
    #plt.show()
    
        
if __name__ == '__main__':
    main()
