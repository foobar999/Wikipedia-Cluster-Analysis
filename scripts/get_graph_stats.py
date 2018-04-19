import os, sys
import logging
import argparse
from pprint import pformat
from gensim.utils import smart_open
from utils.utils import init_logger, log_graph
from igraph import Graph

logger = init_logger()

           
    
def main():
    parser = argparse.ArgumentParser(description='calculates connected component stats from given graph')
    parser.add_argument('--graph', type=argparse.FileType('r'), help='path to input pickled .cpickle.gz graph file ', required=True)
    
    args = parser.parse_args()
    input_graph_path = args.graph.name
    
    logger.info('running with:\n{}'.format(pformat({'input_graph_path':input_graph_path})))
    
    graph = Graph.Read_Picklez(input_graph_path)        
    logger.info('loaded graph')
    log_graph(graph)
        
    logger.info('calculating connected components')
    components = graph.components()
    logger.debug(components)
    logger.info('size histogram')
    logger.info(components.size_histogram())
    degree_histogram = graph.degree_distribution()
    logger.info('node degree distribution')
    logger.info(degree_histogram)
    logger.info('mean degree: {}'.format(degree_histogram.mean))
    
        
        
if __name__ == '__main__':
    main()
