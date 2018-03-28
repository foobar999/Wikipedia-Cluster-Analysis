import os
import sys
import argparse
import logging
import bz2
from gensim.corpora import MmCorpus
from gensim.models import TfidfModel

DEFAULT_SMART = 'ltn'   # tf: 1+log2(tf)  df: log2(N/df)  normalisierung: nö

def main():
    parser = argparse.ArgumentParser(description='creates a binary .pkl/.pkl.bz2 tf-idf model file from a given binary .pkl/.pkl.bz2 bag-of-words model file', epilog='Example: ./{} mycorpus-bow.pkl.bz2 mycorpus-tfidf.pkl.bz2 --smart=ltn'.format(sys.argv[0]))
    parser.add_argument('model_bow', type=argparse.FileType('r'), help='path to input bow model file (.pkl or .pkl.bz2)')
    parser.add_argument('model_tfidf', type=argparse.FileType('w'), help='path to output tfidf model file (.pkl of .pkl.bz2)')
    parser.add_argument('--smart', default=DEFAULT_SMART, help='used wlocals,wglobal,normalize functions for tf-idf in SMART notation (as noted in gensim gensim.models.tfidfmodel doc) (default "{}")'.format(DEFAULT_SMART))
    
    args = parser.parse_args()
    input_bow_path = args.model_bow.name
    output_tfidf_path = args.model_tfidf.name
    smart = args.smart
    
    program = os.path.basename(sys.argv[0])
    logger = logging.getLogger(program)
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')    
    logging.root.level = logging.INFO
    
    logger.info('running {} with input_bow_path {}, output_tfidf_path {}, smart {}'.format(program, input_bow_path, output_tfidf_path, smart))   
    bow_model = MmCorpus.load(input_bow_path)
    tfidf_model = TfidfModel(bow_model, smartirs=smart)
    tfidf_corpus = tfidf_model[bow_model]
    tfidf_corpus.save(output_tfidf_path)
    
    logger.info("finished running %s", program)
        
    
if __name__ == '__main__':
    main()
    
