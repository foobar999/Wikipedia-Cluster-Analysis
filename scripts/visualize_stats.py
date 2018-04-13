import os, sys
import logging
import argparse
from pprint import pformat
import matplotlib.pyplot as plt
from utils.utils import init_gensim_logger, read_rows
import numpy as np
    
#i = 0
#ctr, mysum = 0, sum(data_y)
#while ctr/mysum < quantile_of:
#    print(ctr/mysum,i,mysum)
#    ctr += data_y[i]
#    i += 1
#quantile = data_x[i]    
#quantile = np.percentile(data_y, 95, interpolation='lower', axis=0)
    
    
def main():
    parser = argparse.ArgumentParser(description='creates a matplotlib image from given data', epilog='Example: ./{} --stats=enwiki-num-auth-per-doc.csv --viz=enwiki-num-auth-per-doc.pdf --quantile=0.95'.format(sys.argv[0]))
    parser.add_argument('--stats', type=argparse.FileType('r'), help='path to input CSV stats', required=True)
    parser.add_argument('--viz', type=argparse.FileType('w'), help='path to output PDF visualization', required=True)
    parser.add_argument('--quantile', type=float, help='quantile of values to draw', required=True)
    
    args = parser.parse_args()
    input_stats_path = args.stats.name
    output_viz_prefix = args.viz.name
    quantile_of = args.quantile
    
    program, logger = init_gensim_logger()
    logger.info('running {} with:\n{}'.format(program, pformat({'input_stats_path':input_stats_path, 'output_viz_prefix':output_viz_prefix})))
         
    data = read_rows(input_stats_path)
    logger.info('read {} rows'.format(len(data)))
    data = [tuple(int(v) for v in row) for row in data]
    logger.debug('data\n{}'.format(data))
    data_x, data_y = [row[0] for row in data], [row[1] for row in data]
    cumul = np.cumsum(data_y)
    logger.debug(cumul)
    quantile_y_index = np.where(cumul >= quantile_of*np.sum(data_y))[0][0]
    logger.debug('{}-quantile in y at index {}'.format(quantile_of,quantile_y_index))
    quantile = data_x[quantile_y_index]    
    logger.info('{}-quantile: {}'.format(quantile_of, quantile))
    
    plt.bar(data_x[:quantile], data_y[:quantile])
    plt.show()
        
if __name__ == '__main__':
    main()
