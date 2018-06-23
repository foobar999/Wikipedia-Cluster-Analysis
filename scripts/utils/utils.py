import logging
import sys, os
import csv, json
import argparse
import bz2
import numpy as np

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

def argparse_bool(value):
    if value in ('y', 'n'):
        return value == 'y'
    else:
        raise argparse.ArgumentTypeError('Exepected boolean value "y" or "n"')

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
        
def save_npz(ofname, mat):
    np.savez_compressed(ofname, arr=mat)
    
def load_npz(ifname):
    return np.load(ifname, mmap_mode='r')['arr']
    
# speichert Objekt als JSON-Datei
def save_data_to_json(data, output_json_path):
    logger.info('saving {} elements to {}'.format(len(data), output_json_path))
    logger.debug('saving data {}'.format(data))
    with open(output_json_path, 'w') as output_json_file:
        json.dump(data, output_json_file, indent=1)
        
# lädt Objekt aus bz2-komprimierter JSON-Datei
def load_compressed_json_data(input_json_bz2_path):
    logger.info('loading bz2-compressed json data from {}'.format(input_json_bz2_path))
    with bz2.open(input_json_bz2_path, 'rt') as input_json_bz2_file:
        data = json.load(input_json_bz2_file)
    logger.info('loaded {} elements'.format(len(data)))
    logger.debug('loaded {}'.format(data))
    return data
       
# lädt die Communitylabels als Datei
def load_communities(communities_path):
    logger.info('loading communities')
    communities = load_compressed_json_data(communities_path)
    logger.info('loaded {} different community labels'.format(len(set(communities))))
    return communities
       
# lädt eine Titeldatei
def load_titles(titles_path):
    logger.info('loading titles')
    return load_compressed_json_data(titles_path)
       
        
        
        