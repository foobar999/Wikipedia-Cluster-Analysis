import os, sys
import argparse
import logging
from pprint import pformat
from gensim.corpora import MmCorpus, Dictionary
from gensim.models import LdaModel
from gensim.models.ldamulticore import LdaMulticore
from utils.utils import init_logger

logger = init_logger()

DEFAULT_PASSES = 100
DEFAULT_ITERATIONS = 1000

def valid_gensim_prior(prior):
    possible_prior_modes = ('symmetric','auto')
    if prior in possible_prior_modes:
        return prior
    else:
        try:
            return float(prior)
        except ValueError:
            raise argparse.ArgumentTypeError('{} not float nor in {}'.format(prior, possible_prior_modes))

def main():
    parser = argparse.ArgumentParser(description='trains an lda model from a given bag-of-words corpus file and an id2word dictionary; no corpus data, only the trained model is saved, to save space', epilog='Example: ./{} mycorpus-bow.mm.bz2 mycorpus-lda-model 7 --id2word mycorpus-wordids.txt.bz2 --passes 10 --iterations 100 --alpha=symmetric --beta=0.01'.format(sys.argv[0]))
    parser.add_argument('corpus', type=argparse.FileType('r'), help='path to text-based input MatrixMarket bow corpus file (.mm/.mm.bz2)')
    parser.add_argument('id2word', type=argparse.FileType('r'), help='path to binary input id2word dictionary file (.cpickle/.cpickle.bz2)')
    parser.add_argument('model_prefix', type=argparse.FileType('w'), help='prefix of output binary lda model files')
    parser.add_argument('numtopics', type=int, help='number of latent topics')
    parser.add_argument('--passes', type=int, help='set number of passes of each document (default {})'.format(DEFAULT_PASSES))
    parser.add_argument('--iterations', type=int, help='set training epochs (default {})'.format(DEFAULT_ITERATIONS))
    parser.add_argument('--alpha', type=valid_gensim_prior, help='distribution-over-topics prior: must be float, "symmetric" or "auto"', required=True)
    parser.add_argument('--beta', type=valid_gensim_prior, help='distribution-over-vocabulary prior: must be float, "symmetric" or "auto"', required=True)
    
    args = parser.parse_args()
    input_corpus_path = args.corpus.name
    input_id2word_path = args.id2word.name
    output_model_prefix = args.model_prefix.name
    numtopics = args.numtopics
    passes,iterations = args.passes,args.iterations
    alpha, beta = args.alpha, args.beta
    
    logger.info('running with:\n{}'.format(pformat({'input_corpus_path':input_corpus_path, 'input_id2word_path':input_id2word_path, 'output_model_prefix':output_model_prefix, 'numtopics':numtopics, 'passes':passes, 'iterations':iterations, 'alpha':alpha, 'beta':beta})))
        
    corpus = MmCorpus(input_corpus_path)
    id2word = Dictionary.load(input_id2word_path)    
    model = LdaModel if 'DEBUG' in os.environ else LdaMulticore
    lda_model = model(corpus=corpus, num_topics=numtopics, id2word=id2word, passes=passes, iterations=iterations, chunksize=2000, alpha=alpha, eta=beta, eval_every=None)    
    
    # TODO id2word nicht mitspeichern?
    lda_model.save(output_model_prefix) # speichert NUR Modelldateien, keine eigentlichen Daten    
    
    
if __name__ == '__main__':
    main()
    
