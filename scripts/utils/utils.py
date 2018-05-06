import logging
import sys, os
import csv
import argparse
from pprint import pformat
import networkx as nx
from igraph import Histogram
from gensim.corpora.wikicorpus import filter_wiki, tokenize


def debug_mode_set():
    return 'DEBUG' in os.environ

    
def init_logger():
    program = os.path.basename(sys.argv[0])
    logger = logging.getLogger(program)
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')    
    logging.root.level = logging.DEBUG if debug_mode_set() else logging.INFO
    mpl_logger = logging.getLogger('matplotlib') # deaktiviere matplotlib-debug-logging
    mpl_logger.setLevel(logging.INFO) 
    return logger

logger = init_logger()
        
def get_tokens(text, token_min_len=1, token_max_len=100):
    text = filter_wiki(text)
    return tokenize(text, token_min_len, token_max_len, True)        
            
def is_mainspace_page(page, namespace_prefixes):
    if page.namespace:
        return page.namespace == 0
    else:
        return not any(page.title.startswith(prefix) for prefix in namespace_prefixes)
        
# registrierter, eingeloggter Nutzer mit ID, Benutzernamen
def is_valid_contributor(contributor):
    return contributor.id is not None and contributor.user_text is not None 
    
def read_lines(fname):
    with open(fname, 'r') as f:
        return tuple(f.read().splitlines())
    
def write_rows(csv_filename, rows):
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=' ')
        csv_writer.writerows(rows)  
        
def read_rows(csv_filename):   
    with open(csv_filename, 'r', newline='', encoding='utf-8') as csv_file:
        csvreader = csv.reader(csv_file, delimiter=' ')
        return [tuple(val for val in row) for row in csvreader]
        
def argparse_bool(value):
    if value in ('y', 'n'):
        return value == 'y'
    else:
        raise argparse.ArgumentTypeError('Exepected boolean value "y" or "n"')
         
         
def log_sparse_histogram(hist):
    for left,right,count in hist.bins():
        if count > 0:
            logger.info('[{0:.2f},{1:.2f}[ : {2} elements'.format(left, right, count))
            

# TODO igraph überall dranhängen
def log_graph_data(numnodes, numedges, components, degrees, weighted_degrees):         
    logger.info('{} nodes, {} edges'.format(numnodes, numedges))
    density = numedges / (numnodes*(numnodes-1)/2)
    logger.info('density {}'.format(density))
    component_sizes = [len(comp) for comp in components]
    logger.info('{} connected components'.format(component_sizes))
    component_sizes_histogram = Histogram(data=component_sizes)
    logger.info('histogram of connected components sizes:')
    log_sparse_histogram(component_sizes_histogram)
    degree_distribution = Histogram(data=degrees)
    logger.info('average node degree {}'.format(degree_distribution.mean))
    logger.info('histogram of node degrees:')
    log_sparse_histogram(degree_distribution)
    weighted_degree_distribution = Histogram(bin_width=0.1, data=weighted_degrees)
    logger.info('average weighted node degreee {}'.format(weighted_degree_distribution.mean))
    logger.info('histogram of weighted node degrees:')
    log_sparse_histogram(weighted_degree_distribution)
    
def log_graph_data_edges(weighted_edges):
    weighted_edges = ((n1,n2,w) if n1<=n2 else (n2,n1,w) for n1,n2,w in weighted_edges)
    for edge in sorted(weighted_edges):
        logger.debug(edge)        
         
def log_igraph(graph):
    log_graph_data(graph.vcount(), graph.ecount(), graph.components(), graph.degree(), graph.strength(weights='weight'))  
    if debug_mode_set():
        weighted_edges = ((graph.vs[edge.source]['name'],graph.vs[edge.target]['name'],edge['weight']) for edge in graph.es)
        log_graph_data_edges(weighted_edges)
        
def log_nwx(graph):
    degrees = [deg for node,deg in graph.degree(weight=None)]
    weighted_degrees = [deg for node,deg in graph.degree(weight='weight')]
    log_graph_data(graph.number_of_nodes(), graph.number_of_edges(), nx.connected_components(graph), degrees, weighted_degrees) 
    if debug_mode_set():
        log_graph_data_edges(graph.edges(data='weight'))
        
def log_communities(communities, graph):
    if debug_mode_set():
        logger.debug('communities: \n{}'.format(communities))
    logger.info('{} communities'.format(len(communities)))
    logger.info('size distribution:')
    log_sparse_histogram(communities.size_histogram())
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
#    document_nodes = tuple(nodeid for nodeid,type in enumerate(bipartite_graph.vs['type']) if type==0)
#    author_nodes = tuple(nodeid for nodeid,type in enumerate(bipartite_graph.vs['type']) if type==1)
#    return document_nodes, author_nodes
    doc_nodes = frozenset(node for node,bipartite in bipart_graph.nodes(data='bipartite') if bipartite==0)
    auth_nodes = frozenset(node for node,bipartite in bipart_graph.nodes(data='bipartite') if bipartite==1)
    return doc_nodes, auth_nodes
        
        
# liefert #Dokumentknoten, #Autorknoten        
def get_bipartite_node_counts(bipartite_graph):
    doc_nodes, auth_nodes = get_bipartite_nodes(bipartite_graph)
    return len(doc_nodes), len(auth_nodes)
            
        
        
                
        
        
        
        
        
        