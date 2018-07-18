import argparse
import numpy as np
from scripts.utils.utils import init_logger, load_communities
from scripts.utils.documents import load_document_topics
from scripts.utils.plot import scatter_2d_plot

logger = init_logger()


def main():
    parser = argparse.ArgumentParser(description='plots given 2d-transformed documents represented by their topic distributions (optional: with clusters)')
    parser.add_argument('--documents-2d', type=argparse.FileType('r'), help='path to input document-2d-data (.npz)', required=True)
    parser.add_argument('--cluster-labels', type=argparse.FileType('r'), help='path to input cluster labels .json.bz2 file')
    parser.add_argument('--img-file', type=argparse.FileType('w'), help='path to output im file', required=True)

    args = parser.parse_args()
    input_documents_2d_path = args.documents_2d.name
    input_cluster_labels_path = args.cluster_labels.name if args.cluster_labels else None
    output_img_path = args.img_file.name

    logger.info('loading 2d-transformed document topics')
    documents_2d = load_document_topics(input_documents_2d_path)     
    
    if input_cluster_labels_path:
        logger.info('loading cluster labels')
        cluster_labels = load_communities(input_cluster_labels_path)
        cluster_labels = np.array(cluster_labels)
    else:
        logger.info('no cluster labels given')
        cluster_labels = None
        
    logger.info('plotting 2d-documents')
    size = 1
    scatter_2d_plot(documents_2d[:,0], documents_2d[:,1], output_img_path, labels=cluster_labels, rasterized=True, size=size)


if __name__ == '__main__':
    main()

