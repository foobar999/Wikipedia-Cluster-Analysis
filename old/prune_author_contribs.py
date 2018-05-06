import os, sys
import logging
import argparse
from pprint import pformat
from heapq import nlargest
from gensim.matutils import MmWriter
from gensim.corpora import MmCorpus
from utils.utils import init_logger
     
logger = init_logger()
    
def prune_contribs_of_authors(contribs, N):
    for author, author_contribs in enumerate(contribs):
        logger.debug('author {}'.format(author))
        logger.debug('from {}'.format(author_contribs))
        max_contribs = nlargest(N, author_contribs, key=lambda contrib: contrib[1]) # bestimme die N wichtigsten Beiträge
        max_contribs = sorted(max_contribs, key=lambda contrib: contrib[0]) # sortiere wieder absteigend nach DocID
        logger.debug('from {}'.format(max_contribs))
        yield max_contribs
    
def main():
    parser = argparse.ArgumentParser(description='prunes contribs of a given author-document-contribs file, storing only top N max. contributions per authot')
    parser.add_argument('--author-doc-contribs', type=argparse.FileType('r'), help='path to input contribution MatrixMarket file (.mm/.mm.bz2)', required=True)
    parser.add_argument('--pruned-contribs', type=argparse.FileType('w'), help='path to output MatrixMarket .mm file', required=True)
    parser.add_argument('--top-n-contribs', type=int, help='keep only N contribs with highes values per author', required=True)
    
    args = parser.parse_args()
    input_author_doc_contribs_path = args.author_doc_contribs.name
    output_pruned_contribs_path = args.pruned_contribs.name
    top_n_contribs = args.top_n_contribs
    
    logger.info('running with:\n{}'.format(pformat({'input_author_doc_contribs_path':input_author_doc_contribs_path, 'output_pruned_contribs_path':output_pruned_contribs_path, 'top_n_contribs':top_n_contribs})))
        
    contribs = MmCorpus(input_author_doc_contribs_path)
    num_authors = contribs.num_docs
    num_docs = contribs.num_terms
    logger.info('processing contributions of {} authors, {} docs'.format(num_authors, num_docs))
    pruned_contribs = prune_contribs_of_authors(contribs, top_n_contribs)
    logger.info('writing pruned corpus')
    MmWriter.write_corpus(output_pruned_contribs_path, pruned_contribs, num_terms=num_docs, index=False, progress_cnt=10000, metadata=False)
    
    
    
        
if __name__ == '__main__':
    main()
