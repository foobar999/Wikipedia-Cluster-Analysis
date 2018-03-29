import os, sys
import argparse
import logging
from pprint import pformat
from gensim.corpora import MmCorpus, Dictionary
from gensim.models.ldamulticore import LdaMulticore
from gensim.matutils import corpus2dense
import numpy as np
from utils import init_gensim_logger

def main():
    parser = argparse.ArgumentParser(description='applies a pickled lda model to a saved .mm corpus and saves the resulting corpus topics as a text-based dense matrix file (rows=documents, cols=topics)', epilog='Example: ./{} mycorpus-bow.mm.bz2 mycorpus-lda-model mycorpus-corpus-topics.txt'.format(sys.argv[0]))
    parser.add_argument('corpus', type=argparse.FileType('r'), help='path to input bag-of-words .mm/.mm.bz2 corpus file')
    parser.add_argument('model_prefix', type=argparse.FileType('r'), help='prefix of input binary lda model files')
    parser.add_argument('corpus_topics', type=argparse.FileType('w'), help='path to output dense matrix text file')
    
    args = parser.parse_args()
    input_corpus_path = args.corpus.name
    input_model_prefix = args.model_prefix.name
    output_corpus_topics_path = args.corpus_topics.name
    
    program, logger = init_gensim_logger()
    
    logger.info('running {} with:\n{}'.format(program, pformat({'input_corpus_path':input_corpus_path, 'input_model_prefix':input_model_prefix, 'output_corpus_topics_path':output_corpus_topics_path})))
    
    mmcorpus = MmCorpus(input_corpus_path)
    lda_model = LdaMulticore.load(input_model_prefix)
    np.savetxt(output_corpus_topics_path, corpus2dense(lda_model[mmcorpus], num_terms=lda_model.num_topics, num_docs=mmcorpus.num_docs).T)
    
if __name__ == '__main__':
    main()
    
