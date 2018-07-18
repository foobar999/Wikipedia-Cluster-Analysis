import argparse
import numpy as np
from scripts.utils.utils import init_logger, load_communities
from scripts.utils.plot import scatter_plot

logger = init_logger()


def main():
    parser = argparse.ArgumentParser(description='plots cluster sizes, sorted descending')
    parser.add_argument('--cluster-labels', type=argparse.FileType('r'), help='path to input .json.bz2 cluster labels file', required=True)
    parser.add_argument('--img', type=argparse.FileType('w'), help='path of output img file', required=True)
    
    args = parser.parse_args()
    input_cluster_labels_path = args.cluster_labels.name
    output_img_path = args.img.name
    
    logger.info('loading cluster labels')
    cluster_labels = load_communities(input_cluster_labels_path)
        
    labels, counts = np.unique(cluster_labels, return_counts=True)
    counts[::-1].sort()
    
    logger.info('plotting sorted cluster sizes')
    xlabel = 'Cluster'
    ylabel = 'Anzahl Dokumente'
    scatter_plot(counts, output_img_path, xlabel, ylabel, False, 3)
    
        
if __name__ == '__main__':
    main()
