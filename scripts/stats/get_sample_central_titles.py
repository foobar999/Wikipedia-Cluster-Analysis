import argparse
from pprint import pformat
from scripts.utils.utils import init_logger, load_compressed_json_data
from scripts.utils.comparison import get_equidistant_indices, get_max_num_titles_in_centrality_data, get_partitions_titles_matrix, display_matrix_as_csv

logger = init_logger()
    
     
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
    
    max_part_titles = get_max_num_titles_in_centrality_data(partitions)
    logger.info('removing partitions with less documents than this number of titles'.format(max_part_titles))
    partitions = [p for p in partitions if p['size'] >= max_part_titles]
    logger.info('filtered to {} partitions'.format(len(partitions)))
    logger.debug('filtered partition sizes {}'.format([p['size'] for p in partitions]))
               
    sample_indices = get_equidistant_indices(len(partitions), num_parts)
    logger.info('sample indices {}'.format(sample_indices))
    sample_partitions = [partitions[i] for i in sample_indices]
    logger.info('sample partitions:\n{}'.format(pformat(sample_partitions)))
    
    titles_matrix = get_partitions_titles_matrix(sample_partitions)
    display_matrix_as_csv(titles_matrix)
    
        
if __name__ == '__main__':
    main()
