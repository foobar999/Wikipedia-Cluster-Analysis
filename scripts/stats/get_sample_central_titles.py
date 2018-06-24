import argparse
import math
from pprint import pformat
from io import StringIO
import numpy as np
from scripts.utils.utils import init_logger, load_compressed_json_data

logger = init_logger()


def get_partitions_titles_matrix(sample_partitions):
    max_num_titles = max(len(sample_part['titles']) for sample_part in sample_partitions)
    titles_matrix = np.empty(shape=(max_num_titles+1, len(sample_partitions)), dtype=object)
    for i, sample_part in enumerate(sample_partitions):
        titles_matrix[0,i] = '$n={}$'.format(sample_part['size'])
        sample_part_titles = sample_part['titles']
        sample_part_titles_with_padding = sample_part_titles + [''] * (max_num_titles - len(sample_part_titles))
        titles_matrix[1:,i] = sample_part_titles_with_padding
    return titles_matrix
    
    
def display_matrix_as_csv(titles_matrix):
    strf = StringIO()
    np.savetxt(strf, titles_matrix, delimiter=";", fmt="%s")
    logger.info('CSV sample partition titles \n{}'.format(strf.getvalue()))
    
     
def main():
    parser = argparse.ArgumentParser(description='determines sample partitions and logs their most central document titles and centralities')
    parser.add_argument('--centrality-data', type=argparse.FileType('r'), help='path to input .json.bz2 community->centrality_data file', required=True)
    parser.add_argument('--num-parts', type=int, help='number of printed equidistant partitions', required=True)
    
    args = parser.parse_args()
    input_centrality_data_path = args.centrality_data.name
    num_parts = args.num_parts
    
    logger.info('running with:\n{}'.format(pformat({'input_centrality_data_path':input_centrality_data_path, 'num_parts':num_parts})))
    
    logger.info('loading centrality data')
    centrality_data = load_compressed_json_data(input_centrality_data_path)
    
    logger.info('sorting partitions descending by size')
    partitions = list(centrality_data.values())
    partitions.sort(key=lambda p:p['size'], reverse=True)
    logger.debug('partition sizes after sorting\n{}'.format([p['size'] for p in partitions]))
    
    max_part_titles = max(len(part['titles']) for part in partitions)
    logger.info('at most {} central titles in given partitions'.format(max_part_titles))
    logger.info('removing partitions with less documents than this number of titles'.format(max_part_titles))
    partitions = [p for p in partitions if p['size'] >= max_part_titles]
    logger.info('filtered to {} partitions'.format(len(partitions)))
    logger.debug('filtered partition sizes {}'.format([p['size'] for p in partitions]))
               
    N = len(partitions)
    K = num_parts
    logger.info('calculating K={} equidistant sample partition indices of N={} partitions'.format(N, K))
    if K > N:
        logger.warning('K is higher than N: setting K to N')
        K = N
    sample_indices = [math.floor(k*(N-1)/(K-1)) for k in range(0,K)]
    logger.info('sample indices {}'.format(sample_indices))
    sample_partitions = [partitions[i] for i in sample_indices]
    logger.info('sample partitions:\n{}'.format(pformat(sample_partitions)))
    
    titles_matrix = get_partitions_titles_matrix(sample_partitions)
    display_matrix_as_csv(titles_matrix)
    
        
if __name__ == '__main__':
    main()
