import os, sys
import argparse
import logging
from pprint import pformat
from gensim.corpora import MmCorpus
from gensim.models.ldamulticore import LdaMulticore
from gensim.matutils import corpus2dense
from gensim.utils import smart_open
import numpy as np
from utils.utils import init_logger
from sklearn.metrics import silhouette_score
 
logger = init_logger()


def main():
    parser = argparse.ArgumentParser(description='calculates silhouette coefficient for a previous clustering', epilog='Example: ./{} mycorpus-bow.mm.bz2 mycorpus-lda-model mycorpus-kmeans-labels.cpickle.bz2 --id2word mycorpus-wordids.txt.bz2 --passes 10 --iterations 100 '.format(sys.argv[0]))
    parser.add_argument('corpus', type=argparse.FileType('r'), help='path to text-based input MatrixMarket bow corpus file (.mm/.mm.bz2)')
    parser.add_argument('lda', type=argparse.FileType('r'), help='path to binary input gensim lda model file')
    parser.add_argument('cluster_labels', type=argparse.FileType('r'), help='path to input binary cluster labels file (.cpickle/.cpickle.bz2)')
    
    args = parser.parse_args()
    input_corpus_path = args.corpus.name
    input_lda_path = args.lda.name
    input_cluster_labels_path = args.cluster_labels.name
    
    logger.info('running with:\n{}'.format(pformat({'input_corpus_path':input_corpus_path, 'input_lda_path':input_lda_path, 'input_cluster_labels_path':input_cluster_labels_path})))
        
    corpus = MmCorpus(input_corpus_path)
    lda = LdaMulticore.load(input_lda_path)
    dense_corpus_topics = corpus2dense(lda[corpus], lda.num_topics, corpus.num_docs).T  # TODO das wird nicht gestreamt -> probleme?
    with smart_open(input_cluster_labels_path, 'rb') as ifile:
        labels = np.load(ifile)
    logger.info('calclating silhouette coefficient')
    logger.debug(corpus)
    logger.debug(lda)
    logger.debug(dense_corpus_topics.shape)
    logger.debug('{} labels'.format(labels.shape[0]))
    score = silhouette_score(dense_corpus_topics, labels, metric='euclidean')
    logger.info('score {}'.format(score))
    
    
    
if __name__ == '__main__':
    main()
    
