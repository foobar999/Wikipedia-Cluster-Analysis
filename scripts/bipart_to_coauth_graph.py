import os, sys
import logging
import argparse
from pprint import pformat
from igraph import Graph
from utils.utils import init_logger, log_graph, get_bipartite_node_counts, simplify_graph

logger = init_logger()
            
     
def main():
    parser = argparse.ArgumentParser(description='maps a given bipartite graph to a co-authorship graph of documents')
    parser.add_argument('--bipart-graph', type=argparse.FileType('r'), help='path to input pickled, gzipped graph file', required=True)
    parser.add_argument('--coauth-graph', type=argparse.FileType('w'), help='path to output pickled, gzipped graph file', required=True)
    modes = {
        'one': 'unweighted coauth graph: edge between d1 and d2 if at least one author contributed to both',
        'mul': 'weighted coauth graph: weight of edges between d1 and d2 is the number of authors contributing to both'
    }
    parser.add_argument('--mode', choices=modes, help='co-authorship generation mode: ' + str(modes), required=True)
    
    args = parser.parse_args()
    input_bipart_path = args.bipart_graph.name
    output_coauth_graph_path = args.coauth_graph.name
    mode = args.mode
    
    logger.info('running with:\n{}'.format(pformat({'input_bipart_path':input_bipart_path, 'output_coauth_graph_path':output_coauth_graph_path, 'mode':mode})))
    
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
    
    # entferne einsame Knoten, 
    simplify_graph(coauth_graph)
    logger.info('simplified graph')
    log_graph(coauth_graph)
    
    coauth_graph.write_picklez(output_coauth_graph_path)
    
        
if __name__ == '__main__':
    main()
