import os, sys
import argparse
import logging
from pprint import pformat
from gensim.corpora import MmCorpus
from gensim.models.ldamulticore import LdaMulticore
from gensim.matutils import corpus2dense
from gensim.utils import smart_open
from sklearn.cluster import MiniBatchKMeans
from utils.utils import init_gensim_logger
import numpy as np
 

def main():
    parser = argparse.ArgumentParser(description='clusters documents of a corpus with k-means by applying a trained lda model to the corpus', epilog='Example: ./{} mycorpus-bow.mm.bz2 mycorpus-lda-model mycorpus-clusters.cpickle.bz2 --id2word mycorpus-wordids.txt.bz2 --passes 10 --iterations 100 '.format(sys.argv[0]))
    parser.add_argument('corpus', type=argparse.FileType('r'), help='path to text-based input MatrixMarket bow corpus file (.mm/.mm.bz2)')
    parser.add_argument('lda', type=argparse.FileType('r'), help='path to binary input lda model file')
    parser.add_argument('cluster_labels', type=argparse.FileType('w'), help='path to output binary cluster labels file (.cpickle/.cpickle.bz2)')
    parser.add_argument('numclusters', type=int, help='number of clusters to create')
    args = parser.parse_args()
    input_corpus_path = args.corpus.name
    input_lda_path = args.lda.name
    output_cluster_labels_path = args.cluster_labels.name
    numclusters = args.numclusters
    
    program, logger = init_gensim_logger()  
    logger.info('running {} with:\n{}'.format(program, pformat({'input_corpus_path':input_corpus_path, 'input_lda_path':input_lda_path, 'output_cluster_labels_path':output_cluster_labels_path, 'numclusters':numclusters})))
        
    corpus = MmCorpus(input_corpus_path)
    lda = LdaMulticore.load(input_lda_path)
    dense = corpus2dense(lda[corpus], lda.num_topics, corpus.num_docs).T  # TODO das wird nicht gestreamt -> probleme?
    verbose = 'DEBUG' in os.environ
    kmeans = MiniBatchKMeans(n_clusters=numclusters, init='k-means++', max_iter=1000000, batch_size=100, verbose=verbose, compute_labels=True, tol=0.0, max_no_improvement=10, n_init=3, reassignment_ratio=0.01)
    logger.info('running k-means on {} documents, {} topics -> {} clusters'.format(corpus.num_docs,lda.num_topics,numclusters))
    logger.info(kmeans)
    cluster_labels = kmeans.fit_predict(dense)
    logger.info('labels')
    logger.info(type(cluster_labels))
    with smart_open(output_cluster_labels_path, 'wb') as ofile:
        np.save(ofile, cluster_labels)
    #np.savetxt(output_cluster_labels_path + '.txt', cluster_labels) # TODO entfernen
    
    logger.info("finished running %s", program)
    
    
if __name__ == '__main__':
    main()
    
