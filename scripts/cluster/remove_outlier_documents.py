import os, sys
import argparse
import numpy as np
from scipy.stats import scoreatpercentile
from scripts.utils.utils import init_logger, save_npz
from scripts.utils.documents import load_document_topics, load_cluster_labels
 
logger = init_logger()
 
 
def get_filtered_documents(documents, outlier_scores, contamination):
    threshold = scoreatpercentile(outlier_scores, 100.*(1.-contamination))
    inliers = outlier_scores < threshold
    logger.debug('outliers {}'.format(np.argwhere(~inliers)))
    return documents[inliers]

def main():
    parser = argparse.ArgumentParser(description='removes outliers of documents by a given outlier labeling file')
    parser.add_argument('--documents', type=argparse.FileType('r'), help='path to input documents file (.npz)', required=True)
    parser.add_argument('--outlier-scores', type=argparse.FileType('r'), help='path to input JSON outlier scores file', required=True)
    parser.add_argument('--filtered-documents', type=argparse.FileType('w'), help='path to output filtered documents file (.npz)', required=True)
    parser.add_argument('--contamination', type=float, help='relative amount of most noisy samples to remove', required=True)
    
    args = parser.parse_args()
    input_document_path = args.documents.name
    input_outlier_scores_path = args.outlier_scores.name
    output_filtered_documents_path = args.filtered_documents.name
    contamination = args.contamination
    
    documents = load_document_topics(input_document_path)
    outlier_scores = load_cluster_labels(input_outlier_scores_path)
    logger.info('filtering documents of shape {} with contamination {}'.format(documents.shape, contamination))
    filtered_documents = get_filtered_documents(documents, outlier_scores, contamination)
    logger.info('shape of filtered documents {}'.format(filtered_documents.shape))
    
    logger.info('saving filtered documents to {}'.format(output_filtered_documents_path))
    save_npz(output_filtered_documents_path, filtered_documents)
    
    
if __name__ == '__main__':
    main()
    
