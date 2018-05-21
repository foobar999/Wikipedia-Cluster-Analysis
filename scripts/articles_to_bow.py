# leichte Adaption von https://github.com/RaRe-Technologies/gensim/blob/master/gensim/scripts/make_wikicorpus.py

description = """
creates from a given .xml.bz2 MediaWiki dump multiple prefixed gensim files (only mainspace articles):
1. a text-based <PREFIX>.mm bag-of-words corpus representation file
2. a binary <PREFIX>-id2word.txt text-based id-to-word dictionary file
3. a binary <PREFIX>.mm.metadata.cpickle file which maps internal gensim document IDs to article titles of the dump
"""

import os
import sys
import argparse
import logging
from pprint import pformat
from mw import xml_dump
from gensim.utils import smart_open
from gensim.matutils import MmWriter
from gensim.corpora import Dictionary, MmCorpus, TextCorpus
from gensim.parsing.preprocessing import STOPWORDS
from utils.utils import init_logger, is_mainspace_page, read_lines, get_tokens

logger = init_logger()

        
def get_page_data(page):
    text = str(next(page).text)
    return page.title, text, page.id       
    
def get_filtered_articles_data(articles_dump, article_min_tokens, token_min_len, stopwords, namespace_prefixes, metadata):
    num_articles_total = 0
    num_articles_mainspace = 0
    num_articles_mainspace_long = 0
    num_tokens_mainspace = 0
    num_tokens_mainspace_long = 0
    num_tokens_mainspace_long_minlen = 0
    num_tokens_mainspace_long_minlen_nstop = 0
    for page in articles_dump:
        logger.debug('article {}'.format(page.title))
        num_articles_total += 1
        if is_mainspace_page(page, namespace_prefixes):
            logger.debug('article {} considered mainspace'.format(page.title))
            num_articles_mainspace += 1
            title, text, pageid = get_page_data(page)
            tokens = get_tokens(text) 
            logger.debug('article {} having {} tokens, needing >= {} tokens'.format(page.title, len(tokens), article_min_tokens))
            num_tokens_mainspace += len(tokens)
            if len(tokens) >= article_min_tokens:
                num_articles_mainspace_long += 1
                num_tokens_mainspace_long += len(tokens)
                tokens_long = tuple(token for token in tokens if len(token) >= token_min_len)            
                logger.debug('article {} having {} tokens with len >= {}'.format(page.title, len(tokens_long), token_min_len))
                num_tokens_mainspace_long_minlen += len(tokens_long)
                tokens_nstop = tuple(token for token in tokens_long if token not in stopwords)   
                logger.debug('article {} having {} non-stopword tokens with len >= {}'.format(page.title, len(tokens_nstop), token_min_len))    
                num_tokens_mainspace_long_minlen_nstop += len(tokens_nstop)
                if metadata:
                    yield tokens_nstop, title
                else:
                    yield tokens_nstop
                    
    logger.info('{} articles total'.format(num_articles_total))
    logger.info('{} articles mainspace'.format(num_articles_mainspace))
    logger.info('{} articles mainspace with >= {} tokens (long enough)'.format(num_articles_mainspace_long, article_min_tokens))
    logger.info('{} tokens in mainspace articles'.format(num_tokens_mainspace))
    logger.info('{} tokens in long enough mainspace articles'.format(num_tokens_mainspace_long))
    logger.info('{} tokens of len >= {} in long enough mainspace articles'.format(num_tokens_mainspace_long_minlen, token_min_len))
    logger.info('{} non-stopword tokens of len >= {} in long enough mainspace articles'.format(num_tokens_mainspace_long_minlen_nstop, token_min_len))
    
                    
def get_filtered_articles_data_from_path(articles_path, article_min_tokens, token_min_len, stopwords, namespace_prefixes, metadata):
    articles_dump_file = smart_open(articles_path)
    articles_dump = xml_dump.Iterator.from_file(articles_dump_file)
    return get_filtered_articles_data(articles_dump, article_min_tokens, token_min_len, stopwords, namespace_prefixes, metadata)
            
            
            

class MediaWikiCorpus(TextCorpus):
    def __init__(self, articles_path, article_min_tokens, token_min_len, stopwords, namespace_prefixes):
        self.articles_path = articles_path
        self.article_min_tokens = article_min_tokens
        self.token_min_len = token_min_len
        self.stopwords = stopwords
        self.namespace_prefixes = namespace_prefixes
        self.metadata = False
        
    def get_texts(self):
        return get_filtered_articles_data_from_path(self.articles_path, self.article_min_tokens, self.token_min_len, self.stopwords, self.namespace_prefixes, self.metadata)
       


def main():
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--articles-dump", type=argparse.FileType('r'), help='path to input .xml.bz2 articles dump', required=True)
    parser.add_argument("--out-prefix", help='prefix of the generated output files', required=True)
    parser.add_argument("--keep-words", type=int, help='number of most frequent word types to keep (default {})', required=True)
    parser.add_argument("--no-below", type=int, help='Keep only tokes which appear in at least NO_BELOW documents (default {})', required=True)
    parser.add_argument("--no-above", type=float, help='Keep only tokes which appear in at most NO_ABOVE*CORPUSSIZE documents (default {})', required=True)
    parser.add_argument("--article-min-tokens", type=int, help='Analyze only articles of >= ARTICLE_MIN_TOKENS tokens default {}). Should be >=1', required=True)
    parser.add_argument("--token-min-len", type=int, help='Consider only tokens of at least MIN chars', required=True)
    parser.add_argument('--remove-stopwords', action='store_true', help='remove english stopwords with gensims stoplist')
    parser.add_argument("--namespace-prefixes", type=argparse.FileType('r'), help='file of namespace prefixes to ignore')
    
    args = parser.parse_args()
    input_articles_path = args.articles_dump.name
    output_prefix = args.out_prefix
    keep_words = args.keep_words
    no_below,no_above = args.no_below,args.no_above
    article_min_tokens = args.article_min_tokens
    token_min_len = args.token_min_len
    remove_stopwords = args.remove_stopwords
    namespace_prefixes = read_lines(args.namespace_prefixes.name) if args.namespace_prefixes else ()
    
    logger.info('running with:\n{}'.format(pformat({'input_articles_path':input_articles_path, 'output_prefix':output_prefix, 'keep_words':keep_words, 'no_below':no_below, 'no_above':no_above, 'article_min_tokens':article_min_tokens, 'token_min_len':token_min_len, 'remove_stopwords':remove_stopwords, 'namespace_prefixes':namespace_prefixes})))
            
    logger.info('generating vocabulary')
    stopwords = STOPWORDS if remove_stopwords else ()
    corpus = MediaWikiCorpus(input_articles_path, article_min_tokens, token_min_len, stopwords, namespace_prefixes)
    corpus.dictionary = Dictionary(corpus.get_texts())
    logger.info('filtering dictionary: removing terms in less than {} docs'.format(no_below))
    corpus.dictionary.filter_extremes(no_below=no_below, no_above=1, keep_n=keep_words)
    logger.info('filtering dictionary: removing terms in more than {} of all docs'.format(no_above))
    corpus.dictionary.filter_extremes(no_below=0, no_above=no_above, keep_n=keep_words)
    corpus.dictionary.compactify()
    output_id2word_path = output_prefix + '-id2word.txt'
    corpus.dictionary.save_as_text(output_id2word_path)    
    
    logger.info('generating bag of words corpus')
    corpus.metadata = True
    output_corpus_path = output_prefix + '.mm'
    #MmCorpus.serialize(output_corpus_path, corpus, progress_cnt=10000, metadata=True)
    MmWriter.write_corpus(output_corpus_path, corpus=corpus, index=False, progress_cnt=10000, metadata=True)  
        
    
    
    
if __name__ == '__main__':
    main()
    
