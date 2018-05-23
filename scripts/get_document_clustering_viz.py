import os, sys
import argparse
import logging
import json
import bz2
from pprint import pformat
from sklearn import decomposition
import matplotlib.pyplot as plt
import numpy as np
from get_document_viz import transform_pca
from utils.utils import init_logger, debug_mode_set, load_cluster_labels, load_document_topics

logger = init_logger()



def main():
    parser = argparse.ArgumentParser(description='plots a k-distance graph of a given dataset')
    parser.add_argument('--document-topics', type=argparse.FileType('r'), help='path to input document-topic-file (.npz)', required=True)
    parser.add_argument('--cluster-labels', type=argparse.FileType('r'), help='path to input cluster labels .json.bz2 file ', required=True)
    parser.add_argument('--img-file', type=argparse.FileType('w'), help='path to output im file', required=True)

    args = parser.parse_args()
    input_document_topics_path = args.document_topics.name
    input_cluster_labels_path = args.cluster_labels.name
    output_img_path = args.img_file.name

    logger.info('running with:\n{}'.format(pformat({'input_document_topics_path':input_document_topics_path,'input_cluster_labels_path':input_cluster_labels_path,'output_img_path':output_img_path})))

    cluster_labels = load_cluster_labels(input_cluster_labels_path)
    document_topics = load_document_topics(input_document_topics_path)
    documents_2d = transform_pca(document_topics)

    cluster_labels = np.array(cluster_labels)
    non_noise = documents_2d[cluster_labels >= 0]
    non_noise_labels = cluster_labels[cluster_labels >= 0]
    noise = documents_2d[cluster_labels < 0]
    plt.scatter(noise[:,0], noise[:,1], c='k', s=1) # plotte noise schwarz 
    plt.scatter(non_noise[:,0], non_noise[:,1], c=non_noise_labels, cmap='prism', s=1) # plotte nicht-noise je nach labels
    logger.info('saving img to {}'.format(output_img_path))
    plt.savefig(output_img_path, bbox_inches='tight')


if __name__ == '__main__':
    main()

