import os, sys
import argparse
import logging
from pprint import pformat
from gensim.corpora import MmCorpus
from gensim.models.ldamulticore import LdaMulticore
from gensim.matutils import corpus2dense
from utils import init_logger, save_npz

logger = init_logger()


def main():
    parser = argparse.ArgumentParser(description='applies a trained lda model to a bag-of-words and saves the resulting corpus topics as a binary numpy dense matrix file (rows=documents, cols=topics)')
    parser.add_argument('--bow', type=argparse.FileType('r'), help='path to input bow file (.mm/.mm.bz2)', required=True)
    parser.add_argument('--model-prefix', type=argparse.FileType('r'), help='prefix of input binary lda model files', required=True)
    parser.add_argument('--document-topics', type=argparse.FileType('w'), help='path to output dense matrix .npz file')
    
    args = parser.parse_args()
    input_bow_path = args.bow.name
    input_model_prefix = args.model_prefix.name
    output_document_topics_path = args.document_topics.name
    
    logger.info('running with:\n{}'.format(pformat({'input_bow_path':input_bow_path, 'input_model_prefix':input_model_prefix, 'output_document_topics_path':output_document_topics_path})))
    
    logger.info('loading bow corpus from {}'.format(input_bow_path))
    bow = MmCorpus(input_bow_path)
    logger.info('loading topic model from {}'.format(input_model_prefix))
    model = LdaMulticore.load(input_model_prefix)
    
    logger.info('generating dense document-topic-matrix: {} docs, {} topics'.format(bow.num_docs, model.num_topics))
    document_topics = corpus2dense(model[bow], model.num_topics, bow.num_docs).T
    logger.info('generated dense matrix of shape {}'.format(document_topics.shape))
    logger.debug('dense matrix\n{}'.format(document_topics))
    
    logger.info('saving dense matrix to {}'.format(output_document_topics_path))
    save_npz(output_document_topics_path, document_topics)
    
    
if __name__ == '__main__':
    main()
    
