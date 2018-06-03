import networkx as nx
import numpy as np
from igraph import Histogram
from collections import Counter
from scripts.utils.utils import init_logger, debug_mode_set

logger = init_logger()


def log_np_distribution(values, numbins):
    counts,bin_edges = np.histogram(values, bins=numbins)
    for i,count in enumerate(counts):
        left,right = bin_edges[i],bin_edges[i+1] 
        logger.info('[{0:.5f},{1:.5f}{2} : {3} elements'.format(left, right, '[' if i != len(counts)-1 else ']', count))
    
def log_discrete_sparse_distribution(values):
    eles,counts = zip(*sorted(Counter(values).items()))    
    for ele,count in zip(eles,counts):
        logger.info('{}: {} elements'.format(ele,count))     

def log_graph_data(numnodes, numedges, components, degrees, edge_weights):         
    logger.info('{} nodes, {} edges'.format(numnodes, numedges))
    density = numedges / (numnodes*(numnodes-1)/2)
    logger.info('density {}'.format(density))
    component_sizes = tuple(len(comp) for comp in components)
    logger.info('{} connected components'.format(len(component_sizes)))
    numbins = 20
    logger.info('histogram of connected components sizes:')
    log_discrete_sparse_distribution(component_sizes)    
    logger.info('histogram of node degrees:')
    log_np_distribution(degrees, numbins)
    logger.info('histogram of edge weights:')
    log_np_distribution(edge_weights, numbins)    
    
def log_graph_data_edges(weighted_edges):
    weighted_edges = ((n1,n2,w) if n1<=n2 else (n2,n1,w) for n1,n2,w in weighted_edges)
    for edge in sorted(weighted_edges):
        logger.debug(edge)        
         
def log_igraph(graph):
    log_graph_data(graph.vcount(), graph.ecount(), graph.components(), graph.degree(), graph.es['weight'])  
    if debug_mode_set():
        weighted_edges = ((graph.vs[edge.source]['name'],graph.vs[edge.target]['name'],edge['weight']) for edge in graph.es)
        log_graph_data_edges(weighted_edges)
        
def log_nwx(graph):
    degrees = tuple(deg for node,deg in graph.degree(weight=None))
    edge_weights = tuple(w for n1,n2,w in graph.edges(data='weight'))
    log_graph_data(graph.number_of_nodes(), graph.number_of_edges(), nx.connected_components(graph), degrees, edge_weights) 
    if debug_mode_set():
        log_graph_data_edges(graph.edges(data='weight'))
        
def log_communities(communities, graph):
    if debug_mode_set():
        logger.debug('communities: \n{}'.format(communities))
    logger.info('{} communities'.format(len(communities)))
    logger.info('size distribution:')
    log_discrete_sparse_distribution(communities.sizes())
    modularity = graph.modularity(communities, weights='weight')    
    logger.info('modularity: {}'.format(modularity))
        
# entfernt Knoten ohne Kanten, summiert Mehrfachkanten zwischen Knoten zu 1 Kante auf
def simplify_graph_igraph(graph):
    # summiere mehrfache Kanten auf 
    graph.simplify(multiple=True, loops=True, combine_edges={'weight': 'sum'})
    logger.info('simplified multiedges to single edges by accumulating')
    # entferne Knoten ohne inzidente Kanten
    nodes_without_edges = tuple(n for n, degree in enumerate(graph.degree()) if degree == 0)
    graph.delete_vertices(nodes_without_edges) 
    logger.info('removed nodes with degree==0')
        
# entfernt Knoten ohne Kanten
def simplify_graph_nwx(graph):
    logger.info('simplifying graph: removing isolated nodes')
    graph.remove_nodes_from(set(nx.isolates(graph)))        
        
# liefert Liste aller Dokumentknoten, Liste aller Autorknoten eines bipartiten Graphen
def get_bipartite_nodes(bipart_graph):
    doc_nodes = frozenset(node for node,bipartite in bipart_graph.nodes(data='bipartite') if bipartite==0)
    auth_nodes = frozenset(node for node,bipartite in bipart_graph.nodes(data='bipartite') if bipartite==1)
    return doc_nodes, auth_nodes        
        
# liefert #Dokumentknoten, #Autorknoten        
def get_bipartite_node_counts(bipartite_graph):
    doc_nodes, auth_nodes = get_bipartite_nodes(bipartite_graph)
    return len(doc_nodes), len(auth_nodes)
    
    
    
    
    