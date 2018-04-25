import os, sys
import logging
import argparse
from pprint import pformat
from itertools import combinations
from gensim.utils import smart_open, chunkize_serial
from gensim.corpora import MmCorpus
from igraph import Graph
from utils.utils import init_logger, log_graph

logger = init_logger()

# TODO gewichteten kram:
# - simplify aufsummieren lassen
# - option für paarweises maß 
# - für gewichtet kann man im Grunde edge_attrs=('weight') in TupleList setzen
# TODO option für paarweise maß einbauen?


# erzeugt einen Graphen mit den Knotenlabeln node_names (d.h. len(node_names) Knoten), 0 Kanten, wahlweise gewichtet
def create_graph(node_names, is_weighted):
    if is_weighted:
        return Graph(n=len(node_names), directed=False, vertex_attrs={'name': node_names}, edge_attrs={'weight': []})
    else:
        return Graph(n=len(node_names), directed=False, vertex_attrs={'name': node_names})
        

# erzeugt zu den Dokumenten (yi) basierend auf gemeinsamen Autoren (xj) Co-Authorship-Werte 
def get_co_occurence_pairs(ys_weights):    
    for x,ys_weights in enumerate(ys_weights):
        logger.debug('contribs for {}: {}'.format(x, ys_weights))
        for (y1,w1), (y2,w2) in combinations(ys_weights, 2):
            co_occurrence_degree = min(w1, w2)
            yield str(y1), str(y2), co_occurrence_degree           
     

# wandelt die Kanten [(n1,n2,w1),...,(nx,ny,wz)] in zwei separate Listen [(n1,n2),...,(nx,ny)] und [w1,...,wz] um
def get_edges_weights_lists(weighted_edges):
    edges = []
    weights = []
    for n1, n2, weight in weighted_edges:
        edges.append((n1,n2))
        weights.append(weight)
    return edges, weights
     
     
def main():
    parser = argparse.ArgumentParser(description='maps a given contribution file [(x1,y1,wa),(x1,y2,wb),...,(x2,y1,wc),...] to a co-occurence graph of yi-nodes; must be sorted by x,y; w-values are conjuncted by minimum')
    parser.add_argument('--contribs', type=argparse.FileType('r'), help='path to input contribution MatrixMarket file (.mm/.mm.bz2)', required=True)
    parser.add_argument('--graph', type=argparse.FileType('w'), help='path to output pickled, gzip graph file', required=True)
    parser.add_argument('--weighted', action='store_true')
    
    args = parser.parse_args()
    input_contribs_path = args.contribs.name
    output_graph_path = args.graph.name
    is_weighted = args.weighted
    
    logger.info('running with:\n{}'.format(pformat({'input_contribs_path':input_contribs_path, 'output_graph_path':output_graph_path, 'is_weighted':is_weighted})))
    
    #contribs = MmCorpus(input_contribs_path)
    #edge_attrs = ('weight') if is_weighted else None
    #graph = Graph.TupleList(get_co_occurence_pairs(contribs), edge_attrs=edge_attrs)
    #logger.info('created graph with {} nodes, {} edges'.format(graph.vcount(), graph.ecount()))
    #log_graph(graph)
    #graph.simplify(multiple=True, loops=True, combine_edges={'weight': 'sum'})
    #logger.info('simplified graph to {} nodes, {} edges'.format(graph.vcount(), graph.ecount()))
    #log_graph(graph)
    #graph.write_picklez(fname=output_graph_path)
     
    contribs = MmCorpus(input_contribs_path)
    num_nodes = contribs.num_terms # Anzahl Dokumente bzw. Knoten
    node_names = tuple(str(i) for i in range(num_nodes))
    graph = create_graph(node_names, is_weighted)
    logger.info('created graph with {} nodes, {} edges'.format(graph.vcount(), graph.ecount()))
    log_graph(graph)
    for chunknr, weighted_edges_chunk in enumerate(chunkize_serial(get_co_occurence_pairs(contribs), 100000)): 
        # lade Kanten häppchenweise und füge sie in Graph ein 
        logger.info('processing chunk {}'.format(chunknr+1))
        edges, weights = get_edges_weights_lists(weighted_edges_chunk)
        graph.add_edges(edges) # füge Kanten ein
        graph.es[-len(edges):]['weight'] = weights # aktualisiere Gewichte
        graph.simplify(multiple=True, loops=True, combine_edges={'weight': 'sum'}) # kombiniere Kanten mit denselben Start- und Zielknoten
    nodes_without_edges = [n for n, degree in enumerate(graph.degree()) if degree == 0]
    graph.delete_vertices(nodes_without_edges) # entferne Knoten ohne inzidente Kanten
    logger.info('simplified graph to {} nodes, {} edges'.format(graph.vcount(), graph.ecount()))
    log_graph(graph)
    graph.write_picklez(fname=output_graph_path)
    
    
    
        
if __name__ == '__main__':
    main()
