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
        
        
if __name__ == '__main__':
    main()
