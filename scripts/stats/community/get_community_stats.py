import argparse
import numpy as np
from pprint import pformat
from scripts.utils.utils import init_logger, load_communities
from scripts.utils.plot import scatter_plot

logger = init_logger()
             
     
def main():
    parser = argparse.ArgumentParser(description='calculates a graph of descending community sizes and writes it to an img file')
    parser.add_argument('--communities', type=argparse.FileType('r'), help='path to input .json.bz2 communities file', required=True)
    parser.add_argument('--img', type=argparse.FileType('w'), help='path of output img file', required=True)
    
    args = parser.parse_args()
    input_communities_path = args.communities.name
    output_img_path = args.img.name
    
    logger.info('running with:\n{}'.format(pformat({'input_communities_path':input_communities_path, 'output_img_path':output_img_path})))
    
    logger.info('loading communties')
    communities = load_communities(input_communities_path)
        
    labels, counts = np.unique(list(communities.values()), return_counts=True)
    logger.info('{} different communities'.format(labels.shape[0]))
    logger.debug('labels \n{}'.format(labels))
    logger.debug('counts \n{}'.format(counts))
    counts[::-1].sort()
    
    xlabel = 'Communities'
    ylabel = 'Anzahl Knoten'
    figsize = (6,2)
    size = 7.5
    scatter_plot(counts, output_img_path, xlabel, ylabel, size=size, figsize=figsize)
    
        
if __name__ == '__main__':
    main()
