
import os
import sys
import argparse
import logging
from gensim.corpora import Dictionary, HashDictionary, MmCorpus, WikiCorpus
from gensim.models import TfidfModel

DEFAULT_SMART = 'ltn'   # tf: 1+log2(tf)  df: log2(N/df)  normalisierung: nö

def main():
    parser = argparse.ArgumentParser(description='creates a tf-idf model from a given gensim bag-of-words model', epilog='Example: ./{} mycorpus-bow.mm mycorpus-tfidf.mm --id2word mycorpus-wordids.txt --smart=ltn'.format(sys.argv[0]))
    parser.add_argument('bow', type=argparse.FileType('r'), help='path to input bow model .mm file')
    parser.add_argument('tfidf', type=argparse.FileType('w'), help='path to output tfidf model .mm file')
    parser.add_argument('--id2word', type=argparse.FileType('r'), help='optional path to input id2word mapping file (.txt); should fit to input bow model')
    parser.add_argument('--smart', default=DEFAULT_SMART, help='used wlocals,wglobal,normalize functions for tf-idf in SMART notation (as noted in gensim gensim.models.tfidfmodel doc) (default "{}")'.format(DEFAULT_SMART))
    
    args = parser.parse_args()
    input_bow_path = args.bow.name
    output_tfidf_path = args.tfidf.name
    input_id2word_path = args.id2word
    smart = args.smart
    
    program = os.path.basename(sys.argv[0])
    logger = logging.getLogger(program)
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')    
    logging.root.level = logging.INFO
    
    logger.info('running {} with input_bow_path {}, output_tfidf_path {}, input_id2word_path {}, smart {}'.format(program, input_bow_path, output_tfidf_path, input_id2word_path, smart))
    
    bow_corpus = MmCorpus(input_bow_path)
    id2word = Dictionary.load_from_text(input_id2word_path) if input_id2word_path else None
    tfidf_model = TfidfModel(bow_corpus, id2word=id2word, smartirs=smart)

    MmCorpus.serialize(output_tfidf_path, tfidf_model[bow_corpus], progress_cnt=10000)
    logger.info("finished running %s", program)
    
    
if __name__ == '__main__':
    main()
    
