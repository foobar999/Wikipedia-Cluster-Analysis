import os, sys
import logging
import argparse
from pprint import pformat
from gensim.corpora import MmCorpus
from gensim.matutils import corpus2csc
from scipy.stats import itemfreq
from utils.utils import init_logger
import matplotlib.pyplot as plt
import scipy.sparse as sp
import numpy as np

logger = init_logger()


def render_hist(data, of_path, xlabel, ylabel):
    logger.info('saving hist of data of shape {} img file to {}'.format(data.shape, of_path))
    logger.info('min {} max {}'.format(data.min(), data.max()))
    logger.debug('data\n{}'.format(data))
    logger.debug('itemfreq\n{}'.format(itemfreq(data)))
    plt.figure(figsize=(10,5))
    plt.hist(data, bins=np.arange(min(data),max(data)+2)-0.5, edgecolor='black', linewidth=1, color='dodgerblue')
    #plt.xlim(0,max(data))
    plt.xticks(range(max(data)+1))
    plt.xlim([min(data)-1, max(data)+1])
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.savefig(of_path, bbox_inches='tight')
    plt.close()
    
    
def apply_quantile(data, quantile_order):
    logger.info('applying quantile {}'.format(quantile_order))
    logger.info('shape before quantile {}, min {} max {}'.format(data.shape, data.min(), data.max()))
    logger.debug('data before quantile {}'.format(data))
    hist = itemfreq(data.data)
    logger.debug('itemfreq hist {}'.format(hist))
    elements, counts = hist[:,0], hist[:,1]
    cumul = np.cumsum(counts)
    total_sum = np.sum(counts)
    quantile_y_index = np.where(cumul >= quantile_order*total_sum)[0][0]
    quantile = elements[quantile_y_index]
    res = data[data <= quantile].T
    logger.info('shape after quantile {}, min {} max {}'.format(res.shape, res.min(), res.max()))
    return res
    
    
def main():    
    plt.ioff()
    plt.rc('font',family='Calibri')
    parser = argparse.ArgumentParser(description='calculated various stats and of a given document-author-contribs file')
    parser.add_argument('--acc-contribs', type=argparse.FileType('r'), help='path to input MatrixMarket acc contributions file (.mm/.mm.bz2)', required=True)
    parser.add_argument('--img-prefix', help='prefix of output generated img files', required=True)
    parser.add_argument('--quantile-order', type=float, help='quantile of histrograms to consider', required=True)
    
    args = parser.parse_args()
    input_acc_contribs_dump_path = args.acc_contribs.name
    output_image_prefix = args.img_prefix
    quantile_order = args.quantile_order
    
    logger.info('running with:\n{}'.format(pformat({'input_acc_contribs_dump_path':input_acc_contribs_dump_path, 'output_image_prefix':output_image_prefix, 'quantile_order':quantile_order})))
        
    acc_contribs = MmCorpus(input_acc_contribs_dump_path)
    logger.info('reading corpus to sparse csr matrix')
    csr_corpus = corpus2csc(acc_contribs).T.tocsr()
    logger.info('generated sparse matrix of shape {}'.format(csr_corpus.shape))
    logger.debug('sparse matrix \n{}'.format(csr_corpus))    
    
    logger.info('calculating authors-per-docs-distribution')
    num_authors_per_doc = sp.find((csr_corpus > 0).sum(1))[2]
    num_authors_per_doc = apply_quantile(num_authors_per_doc, quantile_order)
    num_authors_per_doc_imgfile = output_image_prefix + '-num-auths-per-doc-dist.pdf'
    xlabel = 'Autoren je Dokument'
    ylabel = 'Häufigkeit'
    render_hist(num_authors_per_doc[:], num_authors_per_doc_imgfile, xlabel, ylabel)    
        
    logger.info('calculating docs-per-authors-distribution')
    num_docs_per_author = sp.find((csr_corpus > 0).sum(0).T)[2]
    num_docs_per_author = apply_quantile(num_docs_per_author, quantile_order)
    num_docs_per_author_imgfile = output_image_prefix + '-num-docs-per-auth-dist.pdf'
    xlabel = 'Dokumente je Autor'
    ylabel = 'Häufigkeit'
    render_hist(num_docs_per_author[:], num_docs_per_author_imgfile, xlabel, ylabel)
    
    #logger.debug('num authors per doc \n{}'.format(num_authors_per_doc))
    #num_authors_per_doc_dist = itemfreq(num_authors_per_doc.data)
    #logger.info('calculated authors-per-docs-distribution: shape {}'.format(num_authors_per_doc_dist.shape))
    #logger.debug('distribution authors per doc \n{}'.format(num_authors_per_doc_dist))
    
    
    
    
    
    
if __name__ == '__main__':
    main()
