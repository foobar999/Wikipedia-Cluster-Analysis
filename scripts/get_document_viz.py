import os, sys
import argparse
import logging
import json
from pprint import pformat
from sklearn import decomposition
from sklearn.preprocessing import Normalizer
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from utils.utils import init_logger, load_npz, load_cluster_labels, load_document_topics

logger = init_logger()


def transform_pca(document_topics):
    logger.info('running pca')
    pca = decomposition.PCA(n_components=2)
    #pca = decomposition.PCA(n_components=3)
    documents_2d = pca.fit_transform(document_topics)
    logger.debug('pca res\n{}'.format(documents_2d))
    return documents_2d


def main():
    parser = argparse.ArgumentParser(description='plots the pca-transformed dense document-topic-vectors')
    parser.add_argument('--document-topics', type=argparse.FileType('r'), help='path to input document-topic-file (.npz)', required=True)
    parser.add_argument('--img-file', type=argparse.FileType('w'), help='path to output img file', required=True)

    args = parser.parse_args()
    input_document_topics_path = args.document_topics.name
    output_img_path = args.img_file.name

    logger.info('running with:\n{}'.format(pformat({'input_document_topics_path':input_document_topics_path,'output_img_path':output_img_path})))

    document_topics = load_document_topics(input_document_topics_path)
    #document_topics = Normalizer(norm='l2', copy=True).transform(document_topics)
    documents_2d = transform_pca(document_topics)

    #from mpl_toolkits.mplot3d import Axes3D
    #ax = plt.figure().gca(projection='3d')
    #ax.scatter(documents_2d[:,0], documents_2d[:,1], documents_2d[:,2], c='dodgerblue', s=1, rasterized=True)
    #plt.show()
    logger.info('plotting pca documents')
    plt.scatter(documents_2d[:,0], documents_2d[:,1], c='dodgerblue', s=1, rasterized=True)
    logger.info('saving img to {}'.format(output_img_path))
    plt.savefig(output_img_path, bbox_inches='tight', dpi=400)
    

if __name__ == '__main__':
    main()

