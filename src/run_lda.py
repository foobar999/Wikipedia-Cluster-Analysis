import os, sys
import argparse
import logging
from pprint import pformat
from gensim.corpora import MmCorpus, Dictionary
from gensim.models.ldamulticore import LdaMulticore
from utils.utils import init_gensim_logger

DEFAULT_PASSES = 100
DEFAULT_ITERATIONS = 1000

def main():
    parser = argparse.ArgumentParser(description='trains an lda model from a given bag-of-words corpus and saves several binary model files; no corpus data is saved, only the trained model file to save space', epilog='Example: ./{} mycorpus-bow.mm.bz2 mycorpus-lda-model 7 --id2word mycorpus-wordids.txt.bz2 --passes 10 --iterations 100 '.format(sys.argv[0]))
    parser.add_argument('corpus', type=argparse.FileType('r'), help='path to input MatrixMarket corpus file (bow or tfidf, .mm or .mm.bz2)')
    parser.add_argument('model_prefix', type=argparse.FileType('w'), help='prefix of output binary lda model files')
    parser.add_argument('numtopics', type=int, help='number of latent topics')
    parser.add_argument('--id2word', type=argparse.FileType('r'), help='optional path to corresponding input id2word mapping file (.txt or .txt.bz2)')
    parser.add_argument('--passes', type=int, help='set number of passes of each document (default {})'.format(DEFAULT_PASSES))
    parser.add_argument('--iterations', type=int, help='set training epochs (default {})'.format(DEFAULT_ITERATIONS))

    args = parser.parse_args()
    input_corpus_path = args.corpus.name
    output_model_prefix = args.model_prefix.name
    numtopics = args.numtopics
    input_id2word_path = args.id2word.name if args.id2word else None
    passes,iterations = args.passes,args.iterations
    
    program, logger = init_gensim_logger()
    logging.root.level = logging.DEBUG  # TODO produktiv raus
    
    logger.info('running {} with:\n{}'.format(program, pformat({'input_corpus_path':input_corpus_path, 'output_model_prefix':output_model_prefix, 'numtopics':numtopics, 'input_id2word_path':input_id2word_path, 'passes':passes, 'iterations':iterations})))
    
    mmcorpus = MmCorpus(input_corpus_path)
    dictionary = Dictionary.load_from_text(input_id2word_path) if input_id2word_path else None
    
    #lda_model = LdaMulticore(corpus=mmcorpus, num_topics=numtopics, id2word=dictionary, passes=passes, iterations=iterations, chunksize=2000, alpha='symmetric', eval_every=None)
    
    from gensim.models import LdaModel # TODO produktiv durch LdaMulticore ersetzen
    lda_model = LdaModel(corpus=mmcorpus, num_topics=numtopics, id2word=dictionary, passes=passes, iterations=iterations, chunksize=2000, alpha='symmetric', eval_every=None)
    
    
    # TODO id2word nicht mitspeichern?
    lda_model.save(output_model_prefix) # speichert NUR Modelldateien, keine eigentlichen Daten
    
    logger.info("finished running %s", program)
    
    
if __name__ == '__main__':
    main()
    
