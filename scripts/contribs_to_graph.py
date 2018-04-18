import os, sys
import logging
import argparse
from pprint import pformat
from itertools import combinations
from gensim.utils import smart_open
from gensim.corpora import  MmCorpus
from igraph import Graph
from utils.utils import init_gensim_logger

program, logger = init_gensim_logger()

# TODO gewichteten kram:
# - simplify aufsummieren lassen
# - option für paarweises maß 
# - für gewichtet kann man im Grunde edge_attrs=('weight') in TupleList setzen
# TODO option für paarweise maß einbauen?


def get_cooccurence_pairs(ys_weights):    
    for x,ys_weights in enumerate(ys_weights):
        logger.debug('contribs for {}: {}'.format(x, ys_weights))
        for (y1,w1), (y2,w2) in combinations(ys_weights, 2):
            co_occurrence_degree = min(w1, w2)
            yield str(y1), str(y2), co_occurrence_degree

           
def log_graph(graph):
    logger.debug('GRAPH\n{}'.format(str(graph)))    
    for i, node in enumerate(graph.vs):
        logger.debug('node {} with name {}'.format(i, node['name']))
    for edge in graph.es:
        weight = edge['weight'] if 'weight' in edge.attribute_names() else ''
        logger.debug('edge {}--{}--{}'.format(edge.source, weight, edge.target))
     

def main():
    parser = argparse.ArgumentParser(description='maps a given contribution file [(x1,y1,wa),(x1,y2,wb),...,(x2,y1,wc),...] to a co-occurence graph of yi-nodes; must be sorted by x,y; w-values are conjuncted by minimum', epilog='Example: ./{} --contribs=enwiki-auth-doc-contribs.mm.bz2 --graph=enwiki-document-graph.cpickle '.format(sys.argv[0]))
    parser.add_argument('--contribs', type=argparse.FileType('r'), help='path to input contribution MatrixMarket file (.mm/.mm.bz2)', required=True)
    parser.add_argument('--graph', type=argparse.FileType('w'), help='path to output co-occurence .mm MatrixMarket file', required=True)
    parser.add_argument('--weighted', action='store_true')
    
    args = parser.parse_args()
    input_contribs_path = args.contribs.name
    output_graph_path = args.graph.name
    is_weighted = args.weighted
    
    logger.info('running {} with:\n{}'.format(program, pformat({'input_contribs_path':input_contribs_path, 'output_graph_path':output_graph_path, 'is_weighted':is_weighted})))
    
    contribs = MmCorpus(input_contribs_path)
    edge_attrs = ('weight') if is_weighted else None
    graph = Graph.TupleList(get_cooccurence_pairs(contribs), edge_attrs=edge_attrs)
    logger.info('created graph with {} nodes, {} edges'.format(graph.vcount(), graph.ecount()))
    log_graph(graph)
    graph.simplify(multiple=True, loops=True, combine_edges={'weight': 'sum'})
    logger.info('simplified graph to {} nodes, {} edges'.format(graph.vcount(), graph.ecount()))
    log_graph(graph)
        
        
        
        
if __name__ == '__main__':
    main()
