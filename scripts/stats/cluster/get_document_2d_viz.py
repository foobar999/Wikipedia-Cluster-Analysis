import os, sys
import argparse
import logging
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scripts.utils.utils import init_logger, load_npz
from scripts.utils.documents import load_cluster_labels

logger = init_logger()



def main():
    parser = argparse.ArgumentParser(description='plots document data / documents data with clusters by given 2d-data')
    parser.add_argument('--documents-2d', type=argparse.FileType('r'), help='path to input document-2d-data (.npz)', required=True)
    parser.add_argument('--cluster-labels', type=argparse.FileType('r'), help='path to input cluster labels .json.bz2 file')
    parser.add_argument('--img-file', type=argparse.FileType('w'), help='path to output im file', required=True)

    args = parser.parse_args()
    input_documents_2d_path = args.documents_2d.name
    input_cluster_labels_path = args.cluster_labels.name if args.cluster_labels else None
    output_img_path = args.img_file.name

    logger.info('loading document 2d data from {}'.format(input_documents_2d_path))
    documents_2d = load_npz(input_documents_2d_path)     
    logger.info('loaded data of shape {}'.format(documents_2d.shape))
    
    if input_cluster_labels_path:
        logger.info('plotting labeled data')
        cluster_labels = load_cluster_labels(input_cluster_labels_path)   
        cluster_labels = np.array(cluster_labels)
        non_noise = documents_2d[cluster_labels >= 0]
        non_noise_labels = cluster_labels[cluster_labels >= 0]
        noise = documents_2d[cluster_labels < 0]
        plt.scatter(noise[:,0], noise[:,1], c='k', s=1, rasterized=True) # plotte noise schwarz 
        plt.scatter(non_noise[:,0], non_noise[:,1], c=non_noise_labels, cmap='prism', s=1, rasterized=True) # plotte nicht-noise je nach labels
        
    else:
        logger.info('plotting unlabeled data')
        plt.scatter(documents_2d[:,0], documents_2d[:,1], c='dodgerblue', s=1, rasterized=True)        
        
    logger.info('saving img to {}'.format(output_img_path))
    plt.savefig(output_img_path, bbox_inches='tight', dpi=400)


if __name__ == '__main__':
    main()

