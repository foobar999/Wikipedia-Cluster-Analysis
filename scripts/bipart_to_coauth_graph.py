import os, sys
import logging
import argparse
from pprint import pformat
from igraph import Graph
from utils.utils import init_logger, log_graph, get_bipartite_node_counts, simplify_graph
from heapq import nlargest

logger = init_logger()
            
     
def main():
    parser = argparse.ArgumentParser(description='maps a given bipartite graph to a co-authorship graph of documents')
    parser.add_argument('--bipart-graph', type=argparse.FileType('r'), help='path to input pickled, gzipped graph file', required=True)
    parser.add_argument('--coauth-graph', type=argparse.FileType('w'), help='path to output pickled, gzipped graph file', required=True)
    modes = {
        'mul': 'weighted coauth graph: weight of edges between d1 and d2 is the number of authors contributing to both'
    }
    parser.add_argument('--mode', choices=modes, help='co-authorship generation mode: ' + str(modes), required=True)
    parser.add_argument('--keep-max-edges', type=int, help='number of edges with highest weights to keep', required=True)
    
    args = parser.parse_args()
    input_bipart_path = args.bipart_graph.name
    output_coauth_graph_path = args.coauth_graph.name
    mode = args.mode
    keep_max_edges = args.keep_max_edges
    
    logger.info('running with:\n{}'.format(pformat({'input_bipart_path':input_bipart_path, 'output_coauth_graph_path':output_coauth_graph_path, 'mode':mode, 'keep_max_edges':keep_max_edges})))
    
    # lade bipartiten Graph
    bipart_graph = Graph.Read_Picklez(input_bipart_path)
    logger.info('read bipartite graph')
    log_graph(bipart_graph)
    logger.info('{} document nodes, {} author nodes'.format(*get_bipartite_node_counts(bipart_graph)))
    
    # erzeugt Co-Authorship-Graph der Dokumente
    calc_multiplicity = mode == 'mul'
    logger.info('applying bipartite projection, multiplicity? {}'.format(calc_multiplicity))
    coauth_graph = bipart_graph.bipartite_projection(types='type', multiplicity=calc_multiplicity, probe1=-1, which=0)
    logger.info('created co-authorship graph')
    log_graph(coauth_graph)
        
        
    # entferne alle Kanten außer den keep_max_edges Kanten mit den größten Gewichten
    logger.info('pruning graph to {} edges'.format(keep_max_edges))
    edgeids_weights = enumerate(coauth_graph.es['weight'])
    max_edges = nlargest(keep_max_edges, edgeids_weights, key=lambda edge: edge[1])
    max_edge_ids = set(edgeid for edgeid,weight in max_edges)
    logger.debug('edges with largest weights: {}'.format(max_edges))
    min_edge_ids = set(range(0, coauth_graph.ecount())) - max_edge_ids
    logger.debug('removing edges: {}'.format(min_edge_ids))
    coauth_graph.delete_edges(min_edge_ids)
    log_graph(coauth_graph)
    
    # entferne einsame Knoten
    logger.info('simplifiying graph')
    simplify_graph(coauth_graph)
    log_graph(coauth_graph)
    
    logger.info('writing graph to {}'.format(output_coauth_graph_path))
    coauth_graph.write_picklez(output_coauth_graph_path)
    
        
if __name__ == '__main__':
    main()
