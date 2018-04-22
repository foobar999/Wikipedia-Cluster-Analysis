import logging
import sys, os
import csv
from gensim.utils import tokenize


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
    
    
def log_graph(graph):
    logger.debug('GRAPH\n{}'.format(str(graph)))    
    for i, node in enumerate(graph.vs):
        logger.debug('node {} with name {}'.format(i, node['name']))
    for edge in graph.es:
        weight = edge['weight'] if 'weight' in edge.attribute_names() else ''
        logger.debug('edge {}--{}--{}'.format(graph.vs[edge.source]['name'], weight, graph.vs[edge.target]['name']))
    
    
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
        
        
        
        
        
        