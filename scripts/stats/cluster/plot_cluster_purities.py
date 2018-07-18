import argparse
import numpy as np
from scipy.spatial.distance import cosine
from scripts.utils.utils import init_logger, load_communities, get_clusters_from_labels
from scripts.utils.documents import load_document_topics
from scripts.utils.plot import scatter_plot

logger = init_logger()

     
def get_cluster_centroid(cluster, document_topics):
    logger.debug('finding centroid of cluster of size {}'.format(len(cluster)))
    cluster_documents = document_topics[cluster]
    logger.debug('submatrix shape {}'.format(cluster_documents.shape))
    cluster_centroid = np.mean(cluster_documents, axis=0)
    logger.debug('centroid of cluster {}: {}'.format(cluster, cluster_centroid))
    return cluster_centroid
     
def get_cluster_purity(cluster, document_topics):
    cluster_centroid = get_cluster_centroid(cluster, document_topics)
    highest_topic = np.argmax(cluster_centroid)
    logger.debug('highest topic {}, value {}'.format(highest_topic, cluster_centroid[highest_topic]))
    pure_topic_distribution = np.zeros(cluster_centroid.shape)
    pure_topic_distribution[highest_topic] = 1
    purity = 1 - cosine(cluster_centroid, pure_topic_distribution) # cosine entspricht hier Kosinusunähnlichkeit
    logger.debug('purity {}'.format(purity))
    return purity
     
def main():
    parser = argparse.ArgumentParser(description='plots the descending purities of each cluster (purity: highest cosine similarity to a [0,...,0,1,0,...,0] topic vector)')    
    parser.add_argument('--document-topics', type=argparse.FileType('r'), help='path to input document-topic-file (.npz)', required=True)
    parser.add_argument('--cluster-labels', type=argparse.FileType('r'), help='path to input .json.bz2 clustering file', required=True)
    parser.add_argument('--plot', type=argparse.FileType('w'), help='path to output purity plot file', required=True)
    
    args = parser.parse_args()
    input_document_topics_path = args.document_topics.name
    input_cluster_labels_path = args.cluster_labels.name
    output_plot_path = args.plot.name
        
    document_topics = load_document_topics(input_document_topics_path)
    cluster_labels = load_communities(input_cluster_labels_path)
        
    clusters = get_clusters_from_labels(cluster_labels)
    logger.info('calculating purity of {} clusters'.format(len(clusters)))
    cluster_purities = [get_cluster_purity(cluster, document_topics) for cluster in clusters]
    logger.info('calculated {} purity values'.format(len(cluster_purities)))
    
    cluster_purities = np.array(cluster_purities)
    cluster_purities[::-1].sort()
    
    xlabel = 'Cluster'
    ylabel = 'Reinheit'
    logger.info('plotting purities to {}'.format(output_plot_path))
    scatter_plot(cluster_purities, output_plot_path, xlabel, ylabel)
    
        
if __name__ == '__main__':
    main()
