import os, sys
import logging
import argparse
from pprint import pformat
import matplotlib.pyplot as plt
from utils.utils import init_logger, read_rows
import numpy as np
    
logger = init_logger()
    
    
def main():
    parser = argparse.ArgumentParser(description='creates a matplotlib image from given data', epilog='Example: ./{} --stats=enwiki-num-auth-per-doc.csv --viz=enwiki-num-auth-per-doc.pdf --quantile=0.95'.format(sys.argv[0]))
    parser.add_argument('--stats', type=argparse.FileType('r'), help='path to input CSV stats', required=True)
    parser.add_argument('--viz', type=argparse.FileType('w'), help='path to output PDF visualization', required=True)
    parser.add_argument('--quantile', type=float, help='quantile of values to draw', required=True)
    
    args = parser.parse_args()
    input_stats_path = args.stats.name
    output_viz_path = args.viz.name
    quantile_of = args.quantile
    
    logger.info('running with:\n{}'.format(pformat({'input_stats_path':input_stats_path, 'output_viz_path':output_viz_path})))
         
    data = read_rows(input_stats_path)
    logger.info('read {} rows'.format(len(data)))
    data = [tuple(int(v) for v in row) for row in data]
    logger.debug('data\n{}'.format(data))
    data_x, data_y = np.array([row[0] for row in data],dtype=int), np.array([row[1] for row in data],dtype=int)
    cumul = np.cumsum(data_y)
    total_sum = np.sum(data_y)
    quantile_y_index = np.where(cumul >= quantile_of*total_sum)[0][0]
    logger.debug('{}-quantile in y at index {}'.format(quantile_of,quantile_y_index))
    quantile = data_x[quantile_y_index]    
    logger.info('sum of y-values {}'.format(total_sum))
    logger.info('{}-quantile at x={}'.format(quantile_of, quantile))
    
    logger.info('saving plot to {}'.format(output_viz_path))
    
    plt.bar(data_x[:quantile], data_y[:quantile])
    #plt.xticks(data_x[:quantile_y_index])
    #plt.yticks(data_y[:quantile_y_index])
    plt.savefig(output_viz_path)
    logger.info('plot saved')
    
        
if __name__ == '__main__':
    main()
    
    
    
#i = 0
#ctr, mysum = 0, sum(data_y)
#while ctr/mysum < quantile_of:
#    print(ctr/mysum,i,mysum)
#    ctr += data_y[i]
#    i += 1
#quantile = data_x[i]    
#quantile = np.percentile(data_y, 95, interpolation='lower', axis=0)
