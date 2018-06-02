import os, sys
import argparse
import logging
from sklearn import decomposition
from sklearn.manifold import TSNE
from utils.utils import init_logger, load_document_topics, save_npz

logger = init_logger()


def main():
    parser = argparse.ArgumentParser(description='maps a given high-dimensional documents to 2d document representations with t-sne')
    parser.add_argument('--document-topics', type=argparse.FileType('r'), help='path to input document-topic-file (.npz)', required=True)
    parser.add_argument('--documents-2d', type=argparse.FileType('w'), help='path to output document-2d-data (.npz)', required=True)

    args = parser.parse_args()
    input_document_topics_path = args.document_topics.name
    output_documents_2d_path = args.documents_2d.name

    document_topics = load_document_topics(input_document_topics_path)
    #model = decomposition.PCA(n_components=2)
    model = TSNE(n_components=2, verbose=1, perplexity=100, n_iter=1000) 
    logger.info('running 2d-transformation with model {}'.format(model))
    documents_2d = model.fit_transform(document_topics)
    logger.debug('2d-transformation res\n{}'.format(documents_2d))
    
    logger.info('saving 2d-documents to {}'.format(output_documents_2d_path))
    save_npz(output_documents_2d_path, documents_2d)


if __name__ == '__main__':
    main()

