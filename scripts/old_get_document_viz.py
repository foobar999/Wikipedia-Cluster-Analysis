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
from get_contribs_stats import render_hist
from utils.utils import init_logger, load_npz, load_cluster_labels, load_document_topics

logger = init_logger()


def transform_pca(document_topics):
    logger.info('running pca')
    pca = decomposition.PCA(n_components=2)
    #pca = decomposition.PCA(n_components=3)
    documents_2d = pca.fit_transform(document_topics)
    logger.debug('pca res\n{}'.format(documents_2d))
    return documents_2d

    
def scatter_plot(data, ofpath, xlabel, ylabel):
    logger.info('plotting of shape {} to {}'.format(data.shape, ofpath))
    plt.rc('font',family='Calibri')     
    plt.figure(figsize=(5,2.5))
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.scatter(np.arange(len(data)), data, c='dodgerblue', s=1)
    plt.savefig(ofpath, bbox_inches='tight')
    

def main():
    parser = argparse.ArgumentParser(description='plots 1. pca-transformed dense document-topic-vectors 2. average probalities per topic 3. cdf of these probabilities')
    parser.add_argument('--document-topics', type=argparse.FileType('r'), help='path to input document-topic-file (.npz)', required=True)
    parser.add_argument('--doc-data', type=argparse.FileType('w'), help='path to output pca data plot file', required=True)
    parser.add_argument('--topic-avg-probs', type=argparse.FileType('w'), help='path to output avg prop plot file', required=True)
    parser.add_argument('--topic-avg-probs-cdf', type=argparse.FileType('w'), help='path to output avg prob cdf plot file', required=True)

    args = parser.parse_args()
    input_document_topics_path = args.document_topics.name
    output_doc_data_path = args.doc_data.name
    output_topic_avg_probs_path = args.topic_avg_probs.name
    output_topic_avg_probs_cdf_path = args.topic_avg_probs_cdf.name
    
    logger.info('running with:\n{}'.format(pformat({'input_document_topics_path':input_document_topics_path,'output_doc_data_path':output_doc_data_path, 'output_topic_avg_probs_path':output_topic_avg_probs_path, 'output_topic_avg_probs_cdf_path':output_topic_avg_probs_cdf_path})))

    document_topics = load_document_topics(input_document_topics_path)
    documents_2d = transform_pca(document_topics)

    #from mpl_toolkits.mplot3d import Axes3D
    #ax = plt.figure().gca(projection='3d')
    #ax.scatter(documents_2d[:,0], documents_2d[:,1], documents_2d[:,2], c='dodgerblue', s=1, rasterized=True)
    #plt.show()
    logger.info('plotting pca documents')
    plt.scatter(documents_2d[:,0], documents_2d[:,1], c='dodgerblue', s=1, rasterized=True)
    logger.info('saving img to {}'.format(output_doc_data_path))
    plt.savefig(output_doc_data_path, bbox_inches='tight', dpi=400)
    
    # logger.info('calculating average probability per topic')
    # average_topic_props = np.average(document_topics, axis=0)
    # logger.info('shape of average res {}'.format(average_topic_props.shape))
    # average_topic_props[::-1].sort()
    # logger.info('sum over averages {}'.format(average_topic_props.sum()))    
    # scatter_plot(average_topic_props, output_topic_avg_probs_path, 'Topic', 'Ø Anteil')
    
    # avg_prop_cdf = np.cumsum(average_topic_props)
    # scatter_plot(avg_prop_cdf, output_topic_avg_probs_cdf_path, 'Topic', 'CDF-Anteil')
    
    # K = 5
    # logger.info('calculating {} topic indices of highest probability'.format(K))
    # top_k_topics = average_topic_props.argsort()[-K:][::-1]
    # logger.info('max topics:\n indices \n{} \n props \n{}'.format(top_k_topics, average_topic_props[top_k_topics]))
    

if __name__ == '__main__':
    main()

