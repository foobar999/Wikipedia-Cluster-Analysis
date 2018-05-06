import os, sys
import logging
import argparse
import networkx as nx
from networkx import bipartite
from pprint import pformat
from utils.utils import init_logger, log_graph_nwx, get_bipartite_nodes, simplify_graph_nwx
from heapq import nsmallest

logger = init_logger()
            
     
def jaccard(graph, v1, v2):
    neighbors1, neighbors2 = set(graph[v1]), set(graph[v2])
    counter = len(neighbors1 & neighbors2)
    denominator = len(neighbors1) + len(neighbors2) - counter
    return 0 if denominator == 0 else counter / denominator
     
     
def main():
    parser = argparse.ArgumentParser(description='maps a given bipartite graph to a co-authorship graph of documents')
    parser.add_argument('--bipart-graph', type=argparse.FileType('r'), help='path to input pickled networkx bipart graph file (.graph/.graph.bz2)', required=True)
    parser.add_argument('--coauth-graph', type=argparse.FileType('w'), help='path to output pickled networkx coauth graph file (.graph/.graph.bz2)', required=True)
    modes = {
        'mul': 'weight of edges between d1 and d2 is the number of authors contributing to both, normalized by number of authors',
        'jac': 'weight of edges between d1 and d2 is the jaccard similarity of shared authors',
        'coll': 'weight of edges between d1 and d2 is newmans collaboration weight',
    }
    parser.add_argument('--mode', choices=modes, help='co-authorship generation mode: ' + str(modes), required=True)
    parser.add_argument('--keep-max-edges', type=int, help='number of edges with highest weights to keep', required=True)
    
    args = parser.parse_args()
    input_bipart_path = args.bipart_graph.name
    output_coauth_graph_path = args.coauth_graph.name
    mode = args.mode
    keep_max_edges = args.keep_max_edges
    
    logger.info('running with:\n{}'.format(pformat({'input_bipart_path':input_bipart_path, 'output_coauth_graph_path':output_coauth_graph_path, 'mode':mode, 'keep_max_edges':keep_max_edges})))
    
    logger.info('reading bipartite graph from {}'.format(input_bipart_path))
    bipart_graph = nx.read_gpickle(input_bipart_path)
    log_graph_nwx(bipart_graph)
    doc_nodes, auth_nodes = get_bipartite_nodes(bipart_graph)
    logger.info('{} document nodes, {} author nodes'.format(len(doc_nodes), len(auth_nodes)))
    
    logger.info('running one-mode {} projection'.format(mode))
    if mode == 'mul':
        coauth_graph = bipartite.weighted_projected_graph(bipart_graph, doc_nodes, ratio=True)
    elif mode == 'jac':
        coauth_graph = bipartite.generic_weighted_projected_graph(bipart_graph, doc_nodes, weight_function=jaccard)
    elif mode == 'coll':
        coauth_graph = bipartite.collaboration_weighted_projected_graph(bipart_graph, doc_nodes)     
    log_graph_nwx(coauth_graph)    
        
    logger.info('pruning to {} highest edges'.format(keep_max_edges))
    num_edges_to_remove = len(coauth_graph.edges) - keep_max_edges
    min_edges = nsmallest(num_edges_to_remove, coauth_graph.edges(data='weight'), key=lambda edge: edge[2])
    coauth_graph.remove_edges_from(min_edges)
    log_graph_nwx(coauth_graph)
        
    simplify_graph_nwx(coauth_graph)
    
    logger.info('writing graph to {}'.format(output_coauth_graph_path))
    nx.write_gpickle(coauth_graph, output_coauth_graph_path)
    
        
if __name__ == '__main__':
    main()
