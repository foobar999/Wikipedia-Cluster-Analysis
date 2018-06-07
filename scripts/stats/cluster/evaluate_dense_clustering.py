import argparse
from sklearn.metrics import silhouette_score, calinski_harabaz_score
from sklearn.metrics.pairwise import _VALID_METRICS 
from scripts.utils.utils import init_logger, load_npz
from scripts.utils.documents import load_cluster_labels
 
logger = init_logger()


def main():
    parser = argparse.ArgumentParser(description='calculates silhouette coefficient of a given clustering and its document-topic-matrix')
    parser.add_argument('--document-topics', type=argparse.FileType('r'), help='path to input document-topic-file (.npz)', required=True)
    parser.add_argument('--cluster-labels', type=argparse.FileType('r'), help='path to input .json.bz2 cluster labels file', required=True)
    parser.add_argument('--metric', choices=_VALID_METRICS, help='distance function to use', required=True)
    
    args = parser.parse_args()
    input_document_topics_path = args.document_topics.name
    input_cluster_labels_path = args.cluster_labels.name
    metric = args.metric
    
    logger.info('loading dense document-topics from {}'.format(input_document_topics_path))
    document_topics = load_npz(input_document_topics_path)
    logger.info('loaded document-topics-matrix of shape {}'.format(document_topics.shape))
    logger.debug('document-topics-matrix \n{}'.format(document_topics))
    
    logger.info('loading cluster labels from {}'.format(input_cluster_labels_path))
    cluster_labels = load_cluster_labels(input_cluster_labels_path)
    logger.debug(cluster_labels)
    
    logger.info('calclating unsupervised evaluation metrics')
    sil_score = silhouette_score(document_topics, cluster_labels, metric=metric) # groß=gut
    logger.info('{} silhouette coefficient: {}'.format(metric, sil_score))
    ch_score = calinski_harabaz_score(document_topics, cluster_labels) # between-scatter durch within-scatter inkl. Straftermen -> groß=gut
    logger.info('calinski harabaz score: {}'.format(ch_score))
    
    
    
if __name__ == '__main__':
    main()
    
