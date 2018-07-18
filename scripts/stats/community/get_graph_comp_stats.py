import os, sys
import logging
import argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pprint import pprint, pformat
from igraph import Graph
import numpy as np
from scipy.stats import itemfreq
from scripts.utils.utils import init_logger
from scripts.utils.graph import log_igraph
from scripts.utils.plot import get_quantile, bar_plot, histogram_plot

logger = init_logger()


def render_hist(data, of_path, xlabel, ylabel):
    logger.info('saving hist of data of shape {} img file to {}'.format(data.shape, of_path))
    logger.info('min {} max {}'.format(data.min(), data.max()))
    logger.debug('data\n{}'.format(data))
    logger.debug('itemfreq\n{}'.format(itemfreq(data)))
    plt.figure(figsize=(5,2.5))
    plt.hist(data, bins=np.arange(min(data),max(data)+2)-0.5, edgecolor='black', linewidth=1, color='dodgerblue')
    xticks = range(0,max(data)+1,2) if max(data) >= 10 else range(0,max(data)+1) # hack
    plt.xticks(xticks)
    plt.xlim([min(data)-1, max(data)+1])
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.savefig(of_path, bbox_inches='tight')
    plt.close()
    
    
def apply_quantile(data, quantile_order):
    logger.info('applying quantile {}'.format(quantile_order))
    logger.info('shape before quantile {}, min {} max {}'.format(data.shape, data.min(), data.max()))
    logger.debug('data before quantile {}'.format(data))
    hist = itemfreq(data.data)
    logger.debug('itemfreq hist {}'.format(hist))
    elements, counts = hist[:,0], hist[:,1]
    cumul = np.cumsum(counts)
    total_sum = np.sum(counts)
    quantile_y_index = np.where(cumul >= quantile_order*total_sum)[0][0]
    quantile = elements[quantile_y_index]
    res = data[data <= quantile].T
    logger.info('shape after quantile {}, min {} max {}'.format(res.shape, res.min(), res.max()))
    return res
    


def main():
    parser = argparse.ArgumentParser(description='plots connected components size distribution of a given graph')
    parser.add_argument('--graph', type=argparse.FileType('r'), help='path to input pickled .cpickle.gz graph file ', required=True)
    parser.add_argument('--img', type=argparse.FileType('w'), help='path of output img file', required=True)
    parser.add_argument('--quantile-order', type=float, help='quantile of histrograms to consider', required=True)
    
    args = parser.parse_args()
    input_graph_path = args.graph.name
    output_img_path = args.img.name
    quantile_order = args.quantile_order
    
    logger.info('running with:\n{}'.format(pformat({'input_graph_path':input_graph_path, 'output_img_path':output_img_path, 'quantile_order':quantile_order})))
    
    graph = Graph.Read_Picklez(input_graph_path)        
    logger.info('loaded graph')
    log_igraph(graph)
        
    logger.info('calculating connected components')
    components = graph.components()
    logger.debug(components)
    components_sizes = np.array([len(comp) for comp in components])
    logger.info('max component size {}'.format(components_sizes.max()))
        
    logger.info('component size distribution of {}-quantile'.format(quantile_order))
    sizes, sizes_counts = np.unique(components_sizes, return_counts=True)
    logger.info('frequencies:\n{}'.format(np.vstack((sizes, sizes_counts)).T))
    
    quantile = get_quantile(components_sizes, quantile_order)
    components_sizes = components_sizes[components_sizes <= quantile]
    sizes, sizes_counts = np.unique(components_sizes, return_counts=True)
    xlabel = 'Knotenanzahl Zusammenhangskomponente'
    ylabel = 'Häufigkeit'
    bar_plot(sizes, sizes_counts, output_img_path, xlabel, ylabel)
    
    
    
        
        
if __name__ == '__main__':
    main()
