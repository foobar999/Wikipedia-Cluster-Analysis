import os, sys
import logging
import argparse
from pprint import pprint, pformat
from igraph import Graph
import numpy as np
from scipy.stats import itemfreq
import matplotlib.pyplot as plt
from get_contribs_stats import apply_quantile, render_hist
from utils.utils import init_logger, log_igraph

logger = init_logger()


def main():
    parser = argparse.ArgumentParser(description='calculates connected component stats from given graph')
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
    logger.info('frequencies:\n{}'.format(itemfreq(components_sizes.data)))    
    components_sizes = apply_quantile(components_sizes, quantile_order)
    xlabel = 'Knotenanzahl Zusammenhangskomponente'
    ylabel = 'Häufigkeit'
    render_hist(components_sizes[:], output_img_path, xlabel, ylabel)
    
    #sizes,counts = zip(*sorted(Counter(components_sizes).items()))  
    #for size,count in zip(sizes,counts):
    #    logger.info('size {}: {}x'.format(size,count))
    
    # nodes = graph.vs
    # print(nodes)
    # print(graph.es)
    # nx_graph = nx.Graph()
    # nx_graph.add_nodes_from(range(0,graph.vcount()))
    # nx_graph.add_edges_from(edge.tuple for edge in graph.es)
    # nx.draw(nx_graph)
    # plt.show()
    # plt.savefig("output/stats/mygraph.pdf")
    
    #logger.info('size histogram')
    #logger.info(components.size_histogram())
    #degree_histogram = graph.degree_distribution()
    #logger.info('node degree distribution')
    #logger.info(degree_histogram)
    #logger.info('mean degree: {}'.format(degree_histogram.mean))
    
    
        
        
if __name__ == '__main__':
    main()
