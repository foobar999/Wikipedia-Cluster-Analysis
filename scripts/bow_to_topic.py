import os, sys
import argparse
import logging
from pprint import pformat
from gensim.corpora import MmCorpus, Dictionary
from gensim.models import LdaModel
from gensim.models.ldamulticore import LdaMulticore
from utils.utils import init_logger

logger = init_logger()


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
    parser = argparse.ArgumentParser(description='trains a topic model from a given bag-of-words corpus file and an id2word dictionary; no corpus data, only the trained model is saved, to save space')
    parser.add_argument('--bow', type=argparse.FileType('r'), help='path to input text-based MatrixMarket bow corpus file (.mm/.mm.bz2)', required=True)
    parser.add_argument('--id2word', type=argparse.FileType('r'), help='path to input text-based id2word dictionary file (.txt/.txt.bz2)', required=True)
    model_types = {
        'lda': 'latent dirichlet allocation',
        'at': 'author-topic model'
    }
    parser.add_argument('--model-type', choices=model_types, help='topic model to use', required=True)
    parser.add_argument('--model-prefix', type=argparse.FileType('w'), help='prefix of output binary lda model files', required=True)
    parser.add_argument('--num-topics', type=int, help='number of latent topics', required=True)
    parser.add_argument('--passes', type=int, help='set number of passes of each document', required=True)
    parser.add_argument('--iterations', type=int, help='set training epochs', required=True)
    parser.add_argument('--alpha', type=valid_gensim_prior, help='distribution-over-topics prior: must be float, "symmetric" or "auto"', required=True)
    parser.add_argument('--beta', type=valid_gensim_prior, help='distribution-over-vocabulary prior: must be float, "symmetric" or "auto"', required=True)
    
    args = parser.parse_args()
    input_bow_path = args.bow.name
    input_id2word_path = args.id2word.name
    model_type = args.model_type
    output_model_prefix = args.model_prefix.name
    num_topics = args.num_topics
    passes,iterations = args.passes,args.iterations
    alpha, beta = args.alpha, args.beta
    
    logger.info('running with:\n{}'.format(pformat({'input_bow_path':input_bow_path, 'input_id2word_path':input_id2word_path, 'model_type':model_type,  'output_model_prefix':output_model_prefix, 'num_topics':num_topics, 'passes':passes, 'iterations':iterations, 'alpha':alpha, 'beta':beta})))
        
    if model_type != 'lda':
        logger.info('{} not implemented'.format(model_type))
        return -1
        
    corpus = MmCorpus(input_bow_path)
    id2word = Dictionary.load_from_text(input_id2word_path)    
    model = LdaModel if 'DEBUG' in os.environ else LdaMulticore
    lda_model = model(corpus=corpus, num_topics=num_topics, id2word=id2word, passes=passes, iterations=iterations, chunksize=2000, alpha=alpha, eta=beta, eval_every=None)    
    
    # TODO id2word nicht mitspeichern?
    lda_model.save(output_model_prefix) # speichert NUR Modelldateien, keine eigentlichen Daten    
    
    max_printed_terms = 10
    topics = lda_model.show_topics(num_topics=num_topics, num_words=max_printed_terms, log=False, formatted=True)
    for topicid,phi in topics:
        logger.info(phi)
    
    
    
if __name__ == '__main__':
    main()
    
