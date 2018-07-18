import logging
import sys, os
import csv, json
import argparse
import bz2
import numpy as np


# liefert True, falls DEBUG-Umgebungsvariable gesetzt, sonst false
def debug_mode_set():
    return 'DEBUG' in os.environ
    
# liefert einen initialisierten Logger
def init_logger():
    program = os.path.basename(sys.argv[0])
    logger = logging.getLogger(program)
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')    
    logging.root.level = logging.DEBUG if debug_mode_set() else logging.INFO
    mpl_logger = logging.getLogger('matplotlib') # deaktiviere matplotlib-debug-logging
    mpl_logger.setLevel(logging.INFO) 
    return logger

logger = init_logger()

# liefert True, falls value='y', liefert False, falls value='n'; wirft argparse-Exception sonst
def argparse_bool(value):
    if value in ('y', 'n'):
        return value == 'y'
    else:
        raise argparse.ArgumentTypeError('Exepected boolean value "y" or "n"')

# liefert die Zeilen von fname als Tupel von Strings
def read_lines(fname):
    with open(fname, 'r') as f:
        return tuple(f.read().splitlines())
    
# schreibt die Zeilen rows CSV-kodiert nach csv_filename
def write_rows(csv_filename, rows):
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=' ')
        csv_writer.writerows(rows)  
        
# liefert die CSV-kodierten Zeilen von csv_filename als Liste von Tupeln
def read_rows(csv_filename):   
    with open(csv_filename, 'r', newline='', encoding='utf-8') as csv_file:
        csvreader = csv.reader(csv_file, delimiter=' ')
        return [tuple(val for val in row) for row in csvreader]
        
# schreibt die numpy-Matrix mat in die Datei ofname komprimiert (.npz-Format)
def save_npz(ofname, mat):
    np.savez_compressed(ofname, arr=mat)
    
# lädt die komprimierte numpy-Matrix der Datei ifname (.npz-Format)
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
       
    
# lädt Communitylabels der Datei in communities_path 
# TODO in "load_partitions" umbenennen, da auch Clusterings so geladen werden
def load_communities(communities_path):
    logger.info('loading communities')
    communities = load_compressed_json_data(communities_path)
    logger.info('loaded {} different community labels'.format(len(set(communities))))
    return communities
       
# lädt eine Titeldatei
def load_titles(titles_path):
    logger.info('loading titles')
    return load_compressed_json_data(titles_path)
       
# erzeugt aus der Repräsentation eines Clusterings durch ein Label je Index eine Repräsentation des Clusterings als Liste von Listen
def get_clusters_from_labels(cluster_labels):
    num_clusters = len(np.unique(cluster_labels))
    logger.info('number of clusters {}'.format(num_clusters))
    clusters = [[] for _ in range(num_clusters)]
    for docid,label in enumerate(cluster_labels):
        clusters[label].append(docid)
    logger.debug('clusters \n{}'.format(clusters))
    return clusters
        
        
        