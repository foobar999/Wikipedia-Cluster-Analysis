import os, sys
import argparse
import logging
import bz2
from pprint import pformat

def main():
    parser = argparse.ArgumentParser(description='creates a lda model from a given bag-of-words or tf-idf model', epilog='Example: ./{} mycorpus-bow.mm.bz2 mycorpus-topics.mm --id2word mycorpus-wordids.txt.bz2 '.format(sys.argv[0]))
    parser.add_argument('model', type=argparse.FileType('r'), help='path to input model file (bow or tfidf, .mm or .mm.bz2)')
    parser.add_argument('lda', type=argparse.FileType('w'), help='path to output lda topic model .mm file')
    parser.add_argument('numtopics', type=int, help='number of latent topics')
    parser.add_argument('--id2word', type=argparse.FileType('r'), help='optional path to input id2word mapping file (.txt or .txt.bz2); should fit to input model')
    
    args = parser.parse_args()
    input_model_path = args.model.name
    output_lda_path = args.lda.name
    numtopics = args.numtopics
    input_id2word_path = args.id2word.name
    
    program = os.path.basename(sys.argv[0])
    logger = logging.getLogger(program)
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')    
    logging.root.level = logging.INFO
    
    logger.info('running {} with:\n{}'.format(program, pformat({'input_model_path':input_model_path, 'output_lda_path':output_lda_path, 'numtopics':numtopics, 'input_id2word_path':input_id2word_path})))
    
    
    corpus = MmCorpus(input_bow_path)
    #id2word = Dictionary.load_from_text(input_id2word_path) if input_id2word_path else None
    #tfidf_model = TfidfModel(bow_corpus, id2word=id2word, smartirs=smart)

    #MmCorpus.serialize(output_tfidf_path, tfidf_model[bow_corpus], progress_cnt=10000)
    logger.info("finished running %s", program)
    
    
if __name__ == '__main__':
    main()
    
