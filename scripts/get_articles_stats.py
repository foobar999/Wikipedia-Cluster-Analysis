import os
import sys
import argparse
import logging
from collections import Counter
from pprint import pformat
from gensim.corpora import Dictionary, MmCorpus
from gensim.parsing.preprocessing import STOPWORDS
from utils.utils import init_logger, is_mainspace_page, read_lines, get_tokens
from articles_to_bow import get_filtered_articles_data_from_path

logger = init_logger()

def numterms(document_tokens):
    terms = set()
    for docid, tokens in enumerate(document_tokens):
        terms.update(tokens)
    logger.info('number of terms {}'.format(len(terms)))
    
    
# eher problematisch, article_min_tokens als letzte operation anzuwenden
# entspricht __iter__
def get_long_documents(dok_tokens, id2word, article_min_tokens):
    for tokens, metadata in dok_tokens:
        bow = id2word.doc2bow(tokens)
        bow_len = sum(count for id,count in bow)
        if bow_len >= article_min_tokens:
            yield bow, metadata
   
   

def get_stats(articles_path, stopwords, token_min_len, token_max_len, article_min_tokens, no_below, no_above, namespace_prefixes):
    # dok_tokens = get_filtered_articles_data_from_path(articles_path, article_min_tokens, token_min_len, token_max_len, stopwords, namespace_prefixes, False)
    # term_dict = Dictionary(dok_tokens)
    # term_dict.filter_extremes(no_below=no_below, no_above=no_above, keep_n=None, keep_tokens=None)
    # xyz = term_dict.doc2bow(get_filtered_articles_data_from_path(articles_path, article_min_tokens, token_min_len, token_max_len, stopwords, namespace_prefixes, False))
    # num_docs, num_terms, num_nnz = term_dict.num_docs, len(term_dict), term_dict.num_nnz
    # logger.info("%ix%i matrix, density=%.3f%% (%i/%i)", num_docs, num_terms, 100.0 * num_nnz / (num_docs * num_terms), num_nnz, num_docs * num_terms)
    # logger.info('')
    dok_tokens = get_filtered_articles_data_from_path(articles_path, 0, token_min_len, token_max_len, stopwords, namespace_prefixes, False)
    term_dict = Dictionary(dok_tokens)
    term_dict.filter_extremes(no_below=no_below, no_above=no_above, keep_n=None, keep_tokens=None)
    bow_data = get_long_documents(get_filtered_articles_data_from_path(articles_path, 0, token_min_len, token_max_len, stopwords, namespace_prefixes, True), term_dict, article_min_tokens)
    num_docs = 0
    num_terms = len(term_dict)
    num_nnz = 0
    for doc_bow, metadata in bow_data:
        num_docs += 1
        num_nnz += len(doc_bow)
    logger.info("%ix%i matrix, density=%.3f%% (%i/%i)", num_docs, num_terms, 100.0 * num_nnz / (num_docs * num_terms), num_nnz, num_docs * num_terms)
    logger.info('')
    
   
def main():
    parser = argparse.ArgumentParser(description='calcualtes some stats from a givena articles dump and plots them')
    parser.add_argument("--articles-dump", type=argparse.FileType('r'), help='path to input .xml.bz2 articles dump', required=True)
    parser.add_argument("--no-below", type=int, help='Keep only tokes which appear in at least NO_BELOW documents (default {})', required=True)
    parser.add_argument("--no-above", type=float, help='Keep only tokes which appear in at most NO_ABOVE*CORPUSSIZE documents (default {})', required=True)
    parser.add_argument("--token-len-range", type=int, nargs=2, metavar=('MIN','MAX'), help='Consider only tokens of at least MIN and at most MAX chars', required=True)
    parser.add_argument("--article-min-tokens", type=int, help='Analyze only articles of >= ARTICLE_MIN_TOKENS tokens default {}). Should be >=1', required=True)
    parser.add_argument("--namespace-prefixes", type=argparse.FileType('r'), help='file of namespace prefixes to ignore', required=True)
    
    args = parser.parse_args()
    input_articles_path = args.articles_dump.name
    no_below,no_above = args.no_below,args.no_above
    token_len_range = args.token_len_range    
    article_min_tokens = args.article_min_tokens
    namespace_prefixes = read_lines(args.namespace_prefixes.name) if args.namespace_prefixes else ()
    
    logger.info('running with:\n{}'.format(pformat({'input_articles_path':input_articles_path, 'no_below':no_below, 'no_above':no_above,'token_len_range':token_len_range, 'article_min_tokens':article_min_tokens, 'namespace_prefixes':namespace_prefixes})))
            
    logger.info('analyzing vocabulary')
    stopwords = STOPWORDS 
    # term_docs = Counter()
    # term_positions = Counter()
    # document_tokens = get_filtered_articles_data_from_path(input_articles_path, 50, token_len_range[0], token_len_range[1], stopwords, namespace_prefixes, False)
    # for docid, tokens in enumerate(document_tokens):
        # term_positions.update(tokens)
        # term_docs.update(set(tokens))
    # logger.info('number of term->numdoc entries {}'.format(len(term_docs))) 
    # logger.info('number of term->numpos entries {}'.format(len(term_positions))) 
    
    # logger.info('stats without filtering')
    # tlr = token_len_range
    # get_stats(input_articles_path, (), 0, 100, 0, 0, 1, namespace_prefixes)
    # logger.info('stats with stopwords')
    # get_stats(input_articles_path, stopwords, 0, 100, 0, 0, 1, namespace_prefixes)
    # logger.info('stats with stopwords, min_len={}'.format(tlr[0]))
    # get_stats(input_articles_path, stopwords, tlr[0], 100, 0, 0, 1, namespace_prefixes)
    # logger.info('stats with stopwords, min_len={}, min_tokens={}'.format(tlr[0],article_min_tokens))
    # get_stats(input_articles_path, stopwords, tlr[0], 100, article_min_tokens, 0, 1, namespace_prefixes)
    # logger.info('stats with stopwords, min_len={}, min_tokens={}, no_below={}'.format(tlr[0],article_min_tokens, no_below))
    # get_stats(input_articles_path, stopwords, tlr[0], 100, article_min_tokens, no_below, 1, namespace_prefixes)
    # logger.info('stats with stopwords, min_len={}, min_tokens={}, no_below={}, no_above={}'.format(tlr[0],article_min_tokens, no_below, no_above))
    # get_stats(input_articles_path, stopwords, tlr[0], 100, article_min_tokens, no_below, no_above, namespace_prefixes)
    
    logger.info('stats without filtering')
    tlr = token_len_range
    get_stats(input_articles_path, (), 0, 100, 0, 0, 1, namespace_prefixes)
    logger.info('stats with stopwords')
    get_stats(input_articles_path, stopwords, 0, 100, 0, 0, 1, namespace_prefixes)
    logger.info('stats with stopwords, min_len={}'.format(tlr[0]))
    get_stats(input_articles_path, stopwords, tlr[0], 100, 0, 0, 1, namespace_prefixes)
    logger.info('stats with stopwords, min_len={}'.format(tlr[0]))
    get_stats(input_articles_path, stopwords, tlr[0], 100, 0, 0, 1, namespace_prefixes)
    logger.info('stats with stopwords, min_len={}, no_below={}'.format(tlr[0], no_below))
    get_stats(input_articles_path, stopwords, tlr[0], 100, 0, no_below, 1, namespace_prefixes)
    logger.info('stats with stopwords, min_len={}, no_below={}, no_above={}'.format(tlr[0], no_below, no_above))
    get_stats(input_articles_path, stopwords, tlr[0], 100, 0, no_below, no_above, namespace_prefixes)
    logger.info('stats with stopwords, min_len={}, no_below={}, no_above={}, min_toks={}'.format(tlr[0], no_below, no_above,article_min_tokens))
    get_stats(input_articles_path, stopwords, tlr[0], 100, article_min_tokens, no_below, no_above, namespace_prefixes)
    
    
           
           
    
    
    
if __name__ == '__main__':
    main()
    

    
