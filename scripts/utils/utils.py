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
    #for edge in graph.es:
    #weight = edge['weight'] if 'weight' in edge.attribute_names() else ''
    #logger.debug('edge {}--{}--{}'.format(graph.vs[edge.source]['name'], weight, graph.vs[edge.target]['name']))
        
         
def log_graph(graph):
    log_graph_data(graph.vcount(), graph.ecount(), graph.components(), graph.degree(), graph.strength(weights='weight'))  
    if debug_mode_set():
        weighted_edges = ((graph.vs[edge.source]['name'],graph.vs[edge.target]['name'],edge['weight']) for edge in graph.es)
        log_graph_data_edges(weighted_edges)
            
    # logger.info('{} nodes, {} edges'.format(graph.vcount(), graph.ecount()))
    # logger.info('density {}'.format(graph.density()))
    # components = graph.components()
    # logger.info('number of conn components {}'.format(len(components)))
    # logger.info('conn components sizes histogram')
    # for lval,rval,count in components.size_histogram().bins():
        # if count > 0:
            # logger.info('[{},{}[ : {}'.format(lval, rval,count))
    # degree_distribution = graph.degree_distribution()
    # logger.info('node degrees: mean {}, sd {}'.format(degree_distribution.mean, degree_distribution.sd))
    # if debug_mode_set():
        # logger.debug(str(graph))
        # for i, node in enumerate(graph.vs):
            # logger.debug('node {} with name {}'.format(i, node['name']))
        # for edge in graph.es:
            # weight = edge['weight'] if 'weight' in edge.attribute_names() else ''
            # logger.debug('edge {}--{}--{}'.format(graph.vs[edge.source]['name'], weight, graph.vs[edge.target]['name']))
        
def log_graph_nwx(graph):
    degrees = [deg for node,deg in graph.degree(weight=None)]
    weighted_degrees = [deg for node,deg in graph.degree(weight='weight')]
    log_graph_data(graph.number_of_nodes(), graph.number_of_edges(), nx.connected_components(graph), degrees, weighted_degrees) 
    if debug_mode_set():
        log_graph_data_edges(graph.edges(data='weight'))
    # if debug_mode_set and len(graph.edges) > 0:
        # edges = graph.edges(data='weight')
        # edges = [(n1,n2,w) if n1<=n2 else (n2,n1,w) for n1,n2,w in edges]
        # logger.debug('\n{}'.format(pformat(sorted(edges))))
    # logger.info('number of nodes {}'.format(graph.number_of_nodes()))
    # logger.info('number of edges {}'.format(graph.number_of_edges()))
    # logger.info('density {}'.format(nx.density(graph)))
    # degrees = [deg for node,deg in graph.degree(weight=None)]
    # avg_degree = sum(degrees) / graph.number_of_nodes()
    # logger.info('average degree {}'.format(avg_degree))
    # weighted_degrees = [deg for node,deg in graph.degree(weight='weight')]
    # avg_weighted_degree = sum(weighted_degrees) / graph.number_of_nodes()
    # logger.info('average weighted degree {}'.format(avg_weighted_degree))
        
        
# entfernt Knoten ohne Kanten, summiert Mehrfachkanten zwischen Knoten zu 1 Kante auf
def simplify_graph(graph):
    # summiere mehrfache Kanten auf 
    graph.simplify(multiple=True, loops=True, combine_edges={'weight': 'sum'})
    logger.info('simplified multiedges to single edges by accumulating')
    # entferne Knoten ohne inzidente Kanten
    nodes_without_edges = tuple(n for n, degree in enumerate(graph.degree()) if degree == 0)
    graph.delete_vertices(nodes_without_edges) 
    logger.info('removed nodes with degree==0')
        
        
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
            
        
def log_communities(communities, graph):
    if debug_mode_set():
        logger.debug('communities: \n{}'.format(communities))
    logger.info('{} communities'.format(len(communities)))
    logger.info('size distribution:')
    log_sparse_histogram(communities.size_histogram())
    modularity = graph.modularity(communities, weights='weight')    
    logger.info('modularity: {}'.format(modularity))
        
                
def simplify_graph_nwx(graph):
    logger.info('simplifying graph: removing isolated nodes')
    graph.remove_nodes_from(set(nx.isolates(graph)))
        
        
        
        
        
        