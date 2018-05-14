import os, sys
import logging
import argparse
from pprint import pformat
from gensim.corpora import MmCorpus
from gensim.matutils import corpus2csc
from scipy.stats import itemfreq
from utils.utils import init_logger
import matplotlib.pyplot as plt
import numpy as np

logger = init_logger()


def render_hist(hist, of_path, xlabel, ylabel):
    logger.info('saving histogram of shape {} img file to {}'.format(hist.shape, of_path))
    plt.hist(hist, bins=20, align='left', edgecolor='black', linewidth=1, color='dodgerblue')
    plt.xlim(0,max(hist))
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.savefig(of_path, bbox_inches='tight')

    
def main():    
    plt.rc('font',family='Calibri')
    parser = argparse.ArgumentParser(description='calculated various stats and of a given document-author-contribs file')
    parser.add_argument('--acc-contribs', type=argparse.FileType('r'), help='path to input MatrixMarket acc contributions file (.mm/.mm.bz2)', required=True)
    parser.add_argument('--img-prefix', type=argparse.FileType('w'), help='prefix of output generated img files', required=True)
    
    args = parser.parse_args()
    input_acc_contribs_dump_path = args.acc_contribs.name
    output_image_prefix = args.img_prefix.name
    
    logger.info('running with:\n{}'.format(pformat({'input_acc_contribs_dump_path':input_acc_contribs_dump_path, 'output_image_prefix':output_image_prefix})))
        
    acc_contribs = MmCorpus(input_acc_contribs_dump_path)
    logger.info('reading corpus to sparse csc matrix')
    csr_corpus = corpus2csc(acc_contribs).T.tocsr()
    logger.info('generated sparse matrix of shape {}'.format(csr_corpus.shape))
    logger.debug('sparse matrix \n{}'.format(csr_corpus))
    
    logger.info('calculating authors-per-docs-distribution')
    num_authors_per_doc = (csr_corpus > 0).sum(1)
    logger.debug('num authors per doc \n{}'.format(num_authors_per_doc))
    num_authors_per_doc_dist = itemfreq(num_authors_per_doc.data)
    logger.info('calculated authors-per-docs-distribution: shape {}'.format(num_authors_per_doc_dist.shape))
    logger.debug('distribution authors per doc \n{}'.format(num_authors_per_doc_dist))
    
    num_authors_per_doc_imgfile = output_image_prefix + '-num-auths-per-doc-dist.pdf'
    xlabel = 'Autoren je Dokument'
    ylabel = 'Häufigkeit'
    render_hist(num_authors_per_doc[:], num_authors_per_doc_imgfile, xlabel, ylabel)
    
    
    
    
    
    
    
if __name__ == '__main__':
    main()
