import argparse
import scipy.sparse as sp
import numpy as np
from pprint import pformat
from gensim.corpora import MmCorpus
from gensim.matutils import corpus2csc
from scripts.utils.utils import init_logger
from scripts.utils.plot import get_quantile, bar_plot

logger = init_logger()

    
def main():    
    parser = argparse.ArgumentParser(description='calculates various stats and of a given document-author-contribs file')
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
    quantile = get_quantile(num_authors_per_doc, quantile_order)
    num_authors_per_doc = num_authors_per_doc[num_authors_per_doc <= quantile]
    num_authors_per_doc_imgfile = output_image_prefix + '-num-auths-per-doc-dist.pdf'
    xlabel = 'Autoren je Dokument'
    ylabel = 'Häufigkeit'
    num_authors, num_authors_counts = np.unique(num_authors_per_doc, return_counts=True)
    bar_plot(num_authors, num_authors_counts, num_authors_per_doc_imgfile, xlabel, ylabel)
        
    logger.info('calculating docs-per-authors-distribution')
    num_docs_per_author = sp.find((csr_corpus > 0).sum(0).T)[2]
    quantile = get_quantile(num_docs_per_author, quantile_order)
    num_docs_per_author = num_docs_per_author[num_docs_per_author <= quantile]
    num_docs_per_author_imgfile = output_image_prefix + '-num-docs-per-auth-dist.pdf'
    xlabel = 'Dokumente je Autor'
    ylabel = 'Häufigkeit'
    num_docs, num_docs_counts = np.unique(num_docs_per_author, return_counts=True)
    bar_plot(num_docs, num_docs_counts, num_docs_per_author_imgfile, xlabel, ylabel)
        
    
if __name__ == '__main__':
    main()
