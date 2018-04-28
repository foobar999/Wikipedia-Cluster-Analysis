import logging
import sys, os
import csv
import argparse
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
        
def get_tokens(text, token_min_len, token_max_len):
    text = filter_wiki(text)
    return tokenize(text, token_min_len, token_max_len, True)        
        
def number_of_tokens(str):
    return sum(1 for token in tokenize(str))
    
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
         
def log_graph(graph):
    logger.info('{} nodes, {} edges'.format(graph.vcount(), graph.ecount()))
    logger.info('density {}'.format(graph.density()))
    if debug_mode_set():
        logger.debug(str(graph))
        for i, node in enumerate(graph.vs):
            logger.debug('node {} with name {}'.format(i, node['name']))
        for edge in graph.es:
            weight = edge['weight'] if 'weight' in edge.attribute_names() else ''
            logger.debug('edge {}--{}--{}'.format(graph.vs[edge.source]['name'], weight, graph.vs[edge.target]['name']))
        
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
def get_bipartite_nodes(bipartite_graph):
    document_nodes = tuple(nodeid for nodeid,type in enumerate(bipartite_graph.vs['type']) if type==0)
    author_nodes = tuple(nodeid for nodeid,type in enumerate(bipartite_graph.vs['type']) if type==1)
    return document_nodes, author_nodes
        
        
# liefert #Dokumentknoten, #Autorknoten        
def get_bipartite_node_counts(bipartite_graph):
    doc_nodes, auth_nodes = get_bipartite_nodes(bipartite_graph)
    return len(doc_nodes), len(auth_nodes)
        
        
        
        
        
        