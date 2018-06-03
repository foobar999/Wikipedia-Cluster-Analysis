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
    
# lädt die Communitylabels als Datei
def load_communities(communities_path):
    logger.info('loading communities from {}'.format(communities_path))
    with bz2.open(communities_path, 'rt') as communities_file:
        communities = json.load(communities_file)
        
    logger.info('loaded {} labels'.format(len(communities)))
    logger.info('loaded {} different labels'.format(len(set(communities))))
    logger.debug('communities:\n{}'.format(communities))
    return communities
       
# lädt eine Titeldatei
def load_titles(titles_path):
    logger.info('loading titles from {}'.format(titles_path))
    with bz2.open(titles_path, 'rt') as titles_file:
        titles = json.load(titles_file)
    logger.info('loaded {} titles'.format(len(titles)))
    return titles
       
       
       
       
       
       
        
        
        