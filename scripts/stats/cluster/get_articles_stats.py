import argparse
from pprint import pformat
from gensim.corpora import Dictionary, MmCorpus
from gensim.parsing.preprocessing import STOPWORDS
from scripts.cluster.articles_to_bow import get_filtered_articles_data_from_path
from scripts.utils.utils import init_logger, read_lines
from scripts.utils.documents import is_mainspace_page, get_tokens

logger = init_logger()


def get_corpus_stats(corpus, id2word):
    num_docs = 0
    num_nnz = 0
    num_terms = len(id2word)
    sum_elements = 0
    for doc in corpus:
        num_docs += 1
        bow = id2word.doc2bow(doc)
        num_nnz += len(bow)
        sum_elements += sum(cnt for id,cnt in bow)
    logger.info("%ix%i matrix, density=%.3f%% (%i/%i), sum_elements %i", num_docs, num_terms, 100.0 * num_nnz / (num_docs * num_terms), num_nnz, num_docs * num_terms, sum_elements) 
    logger.info('')
   

def get_stats(articles_path, article_min_tokens, token_min_len, stopwords, no_below, no_above, namespace_prefixes):
    dok_tokens = get_filtered_articles_data_from_path(articles_path, article_min_tokens, token_min_len, stopwords, namespace_prefixes, False)
    id2word = Dictionary(dok_tokens)
    logger.info('no_below {} discarding'.format(no_below))
    id2word.filter_extremes(no_below=no_below, no_above=1, keep_n=None, keep_tokens=None)
    logger.info('no_above {} discarding'.format(no_above))
    id2word.filter_extremes(no_below=0, no_above=no_above, keep_n=None, keep_tokens=None)
    get_corpus_stats(get_filtered_articles_data_from_path(articles_path, article_min_tokens, token_min_len, stopwords, namespace_prefixes, False), id2word)
   
   
def main():
    parser = argparse.ArgumentParser(description='calculates stats of various bag-of-word-models, adding more preprocessing steps incrementally')
    parser.add_argument("--articles-dump", type=argparse.FileType('r'), help='path to input .xml.bz2 articles dump', required=True)
    parser.add_argument("--no-below", type=int, help='Keep only tokes which appear in at least NO_BELOW documents (default {})', required=True)
    parser.add_argument("--no-above", type=float, help='Keep only tokes which appear in at most NO_ABOVE*CORPUSSIZE documents (default {})', required=True)
    parser.add_argument("--token-min-len", type=int, help='Consider only tokens of >= TOKEN_MIN_LEN chars', required=True)
    parser.add_argument("--article-min-tokens", type=int, help='Analyze only articles of >= ARTICLE_MIN_TOKENS tokens default {}). Should be >=1', required=True)
    parser.add_argument("--namespace-prefixes", type=argparse.FileType('r'), help='file of namespace prefixes to ignore', required=True)
    
    args = parser.parse_args()
    input_articles_path = args.articles_dump.name
    no_below,no_above = args.no_below,args.no_above
    token_min_len = args.token_min_len    
    article_min_tokens = args.article_min_tokens
    namespace_prefixes = read_lines(args.namespace_prefixes.name) if args.namespace_prefixes else ()
    
    logger.info('running with:\n{}'.format(pformat({'input_articles_path':input_articles_path, 'no_below':no_below, 'no_above':no_above,'token_min_len':token_min_len, 'article_min_tokens':article_min_tokens, 'namespace_prefixes':namespace_prefixes})))
            
    logger.info('analyzing vocabulary')
    stopwords = STOPWORDS 
    
    logger.info('stats without filtering')
    get_stats(input_articles_path, 0, 0, (), 0, 1, namespace_prefixes)
    logger.info('stats with art_toks>={}'.format(article_min_tokens))
    get_stats(input_articles_path, article_min_tokens, 0, (), 0, 1, namespace_prefixes)
    logger.info('stats with art_toks>={}, tok_len>={}'.format(article_min_tokens,token_min_len))
    get_stats(input_articles_path, article_min_tokens, token_min_len, (), 0, 1, namespace_prefixes)
    logger.info('stats with art_toks>={}, tok_len>={}, stopwords'.format(article_min_tokens,token_min_len))
    get_stats(input_articles_path, article_min_tokens, token_min_len, stopwords, 0, 1, namespace_prefixes)
    logger.info('stats with art_toks>={}, tok_len>={}, stopwords, df>={}'.format(article_min_tokens,token_min_len,no_below))
    get_stats(input_articles_path, article_min_tokens, token_min_len, stopwords, no_below, 1, namespace_prefixes)
    logger.info('stats with art_toks>={}, tok_len>={}, stopwords, df>={}, df<={}'.format(article_min_tokens,token_min_len,no_below,no_above))
    get_stats(input_articles_path, article_min_tokens, token_min_len, stopwords, no_below, no_above, namespace_prefixes)
    
    
if __name__ == '__main__':
    main()
    

    
