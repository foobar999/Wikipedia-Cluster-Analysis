import argparse
import math
from heapq import nlargest
from pprint import pformat
import numpy as np
from io import StringIO
from scripts.utils.utils import init_logger, load_compressed_json_data

logger = init_logger()

     
def main():
    parser = argparse.ArgumentParser(description='determines sample partitions and logs their most central document titles and centralities')
    parser.add_argument('--centrality-data', type=argparse.FileType('r'), help='path to input .json.bz2 community->centrality_data file', required=True)
    parser.add_argument('--num-parts', type=int, help='number of printed equidistant partitions', required=True)
    parser.add_argument('--min-part-size', type=int, help='consider only partitions of minimum size', required=True)
    
    args = parser.parse_args()
    input_centrality_data_path = args.centrality_data.name
    num_parts = args.num_parts
    min_part_size = args.min_part_size
    
    logger.info('running with:\n{}'.format(pformat({'input_centrality_data_path':input_centrality_data_path, 'num_parts':num_parts, 'min_part_size':min_part_size})))
    
    logger.info('loading centrality data')
    centrality_data = load_compressed_json_data(input_centrality_data_path)
    
    logger.info('sorting partitions descending by size')
    partitions = list(centrality_data.values())
    partitions.sort(key=lambda p:p['size'], reverse=True)
    logger.debug('partition sizes after sortig\n{}'.format([p['size'] for p in partitions]))
    
    logger.info('filtering to partitions of at least {} documents'.format(min_part_size))
    partitions = [p for p in partitions if p['size'] >= min_part_size]
    logger.info('filtered to {} partitions'.format(len(partitions)))
    logger.debug('filtered partition sizes {}'.format([p['size'] for p in partitions]))
               
    N = len(partitions)
    K = num_parts
    logger.info('calculating K={} equidistant sample partition indices of N={} partitions'.format(N, K))
    if N < K:
        logger.warning('K is higher than N: setting K to N')
        K = N
    sample_indices = [math.floor(k*(N-1)/(K-1)) for k in range(0,K)]
    logger.info('sample indices {}'.format(sample_indices))
    sample_partititions = [partitions[i] for i in sample_indices]
    logger.info('sample partitions:\n{}'.format(pformat(sample_partititions)))
    
    max_sample_part_num_titles = max(len(sp['titles']) for sp in sample_partititions)
    title_matrix = np.empty(shape=(max_sample_part_num_titles+1, len(sample_partititions)), dtype=object)
    for i, sample_part in enumerate(sample_partititions):
        title_matrix[0,i] = '$n={}$'.format(sample_part['size'])
        title_matrix[1:,i] = sample_part['titles']
    strf = StringIO()
    np.savetxt(strf, title_matrix, delimiter=";", fmt="%s")
    logger.info('CSV sample partition titles \n{}'.format(strf.getvalue()))
    
        
if __name__ == '__main__':
    main()
