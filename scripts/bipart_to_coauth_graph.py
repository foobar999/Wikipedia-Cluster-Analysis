import os, sys
import logging
import argparse
from pprint import pformat
from igraph import Graph
from utils.utils import init_logger, log_graph, get_bipartite_nodes, simplify_graph
from heapq import nlargest

logger = init_logger()
           
# TODO jaccard-option (beachte: jaccard vor prnuning nötig)
# TODO normalisieren           
     
def main():
    parser = argparse.ArgumentParser(description='maps a given bipartite graph to a co-authorship graph of documents')
    parser.add_argument('--bipart-graph', type=argparse.FileType('r'), help='path to input pickled, gzipped graph file', required=True)
    parser.add_argument('--coauth-graph', type=argparse.FileType('w'), help='path to output pickled, gzipped graph file', required=True)
    modes = {
        'mul': 'weight of edges between d1 and d2 is the number of authors contributing to both, normalized by number of authors',
        'jac': 'weight of edges between d1 and d2 is the jaccard similarity of shared authors'
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
    doc_nodes, auth_nodes = get_bipartite_nodes(bipart_graph)
    logger.info('{} document nodes, {} author nodes'.format(len(doc_nodes), len(auth_nodes)))
    
    # erzeugt Co-Authorship-Graph der Dokumente
    logger.info('applying bipartite projection')
    coauth_graph = bipart_graph.bipartite_projection(types='type', multiplicity=True, probe1=-1, which=0)
    logger.info('created co-authorship graph')
    log_graph(coauth_graph)    
        
    if mode == 'mul':
        # normalisiere: teile durch #Autoren
        num_authors = len(auth_nodes)
        logger.info('normalizing edge weights, divinding by number of authors {}'.format(num_authors))
        for edgeid,weight in enumerate(coauth_graph.es['weight']):
            coauth_graph.es[edgeid]['weight'] /= num_authors
        
    if mode == 'jac':
        # bp. Projektion entspricht Berechnung des Jaccard-Zählers -> teile noch durch Nenner
        logger.info('updating jaccard denominators')
        
        # erzeuge Mapping {nodeid in coauth-graph -> degree in bipart-graph}
        doc_node_names = tuple(bipart_graph.vs['name'][nodeid] for nodeid in doc_nodes)
        doc_node_degrees = dict(zip(doc_node_names, bipart_graph.degree(doc_nodes)))   
        doc_node_degrees = {doc_id:doc_node_degrees[doc_name] for doc_id, doc_name in enumerate(coauth_graph.vs['name'])}
        #logger.debug('document node degrees: {}'.format(doc_node_degrees))
        
        for edgeid in range(len(coauth_graph.es)):
            degree_src = doc_node_degrees[coauth_graph.es[edgeid].source]
            degree_tar = doc_node_degrees[coauth_graph.es[edgeid].target]
            # teile durch Nenner
            coauth_graph.es[edgeid]['weight'] /= (degree_src + degree_tar - coauth_graph.es[edgeid]['weight'])
    
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
