# leichte Adaption von https://github.com/RaRe-Technologies/gensim/blob/master/gensim/scripts/make_wikicorpus.py

description = """
creates from a given .xml.bz2 MediaWiki dump multiple prefixed gensim files (only mainspace articles):
1. a text-based <PREFIX>.mm bag-of-words corpus representation file
2. a binary <PREFIX>.mm.index file of the corpus
3. a binary <PREFIX>.id2word.cpickle pickled id-to-word dictionary file
4. a binary <PREFIX>.mm.metadata.cpickle file which maps internal gensim document IDs to article titles and page IDs of th dump
"""

import os
import sys
import argparse
import logging
from pprint import pformat
from mw import xml_dump
from gensim.utils import smart_open
from gensim.corpora.wikicorpus import filter_wiki, tokenize
from gensim.corpora import Dictionary, MmCorpus, TextCorpus
from utils.utils import init_gensim_logger


program, logger = init_gensim_logger()


def is_mainspace_page(page, namespace_prefixes):
    if page.namespace:
        return page.namespace == 0
    else:
        return not any(page.title.startswith(prefix) for prefix in namespace_prefixes)

def get_page_data(page):
    text = str(next(page).text)
    return page.title, text, page.id       

def get_tokens(text, token_min_len, token_max_len):
    text = filter_wiki(text)
    return tokenize(text, token_min_len, token_max_len, True)
    
def get_filtered_articles_data(articles_dump, article_min_tokens, token_min_len, token_max_len, namespace_prefixes, metadata):
    num_articles_total = 0
    num_articles = 0
    num_positions = 0
    for page in articles_dump:
        logger.debug('article "{}"'.format(page.title))
        num_articles_total += 1
        if is_mainspace_page(page, namespace_prefixes):
            logger.debug('article "{}" considered mainspace'.format(page.title))
            title, text, pageid = get_page_data(page)
            tokens = get_tokens(text, token_min_len, token_max_len)
            if len(tokens) >= article_min_tokens:
                logger.debug('article "{}" considered long enough'.format(page.title))
                num_articles += 1
                num_positions += len(tokens)
                if metadata:
                    yield tokens, (title, pageid)
                else:
                    yield tokens
    logger.info('loaded {} articles (total), {} articles (filtered), {} positions (filtered)'.format(num_articles_total,num_articles,num_positions))
    
                    
def get_filtered_articles_data_from_path(articles_path, article_min_tokens, token_min_len, token_max_len, namespace_prefixes, metadata):
    with smart_open(articles_path) as articles_dump_file:  
        articles_dump = xml_dump.Iterator.from_file(articles_dump_file)
        return get_filtered_articles_data(articles_dump, article_min_tokens, token_min_len, token_max_len, namespace_prefixes, metadata)
            
            
            

class MediaWikiCorpus(TextCorpus):
    def __init__(self, articles_path, article_min_tokens, token_min_len, token_max_len, namespace_prefixes):
        self.articles_path = articles_path
        self.article_min_tokens = article_min_tokens
        self.token_min_len = token_min_len
        self.token_max_len = token_max_len
        self.namespace_prefixes = namespace_prefixes
        self.metadata = False
        
    def get_texts(self):
        return get_filtered_articles_data_from_path(self.articles_path, self.article_min_tokens, self.token_min_len, self.token_max_len, self.namespace_prefixes, self.metadata)
       


def main():
    parser = argparse.ArgumentParser(description=description, epilog='Example: ./{} enwiki-pages-articles.xml.bz2 output/enwiki-corpus --keep-words 1000 --no-below=10 --no-above=0.5 --article-min-tokens 50 --token-len-range 2 20'.format(sys.argv[0]))
    parser.add_argument("--articles-dump", type=argparse.FileType('r'), help='path to input .xml.bz2 articles dump', required=True)
    parser.add_argument("--out-prefix", help='prefix of the generated output files', required=True)
    parser.add_argument("--keep-words", type=int, help='number of most frequent word types to keep (default {})', required=True)
    parser.add_argument("--no-below", type=int, help='Keep only tokes which appear in at least NO_BELOW documents (default {})', required=True)
    parser.add_argument("--no-above", type=float, help='Keep only tokes which appear in at most NO_ABOVE*CORPUSSIZE documents (default {})', required=True)
    parser.add_argument("--article-min-tokens", type=int, help='Analyze only articles of >= ARTICLE_MIN_TOKENS tokens default {}). Should be >=1', required=True)
    parser.add_argument("--token-len-range", type=int, nargs=2, metavar=('MIN','MAX'), help='Consider only tokens of at least MIN and at most MAX chars', required=True)
    
    args = parser.parse_args()
    input_articles_path = args.articles_dump.name
    output_prefix = args.out_prefix
    keep_words = args.keep_words
    no_below,no_above = args.no_below,args.no_above
    article_min_tokens = args.article_min_tokens
    token_len_range = args.token_len_range
    
    logger.info('running {} with:\n{}'.format(program,pformat({'input_articles_path':input_articles_path, 'output_prefix':output_prefix, 'keep_words':keep_words, 'no_below':no_below, 'no_above':no_above, 'article_min_tokens':article_min_tokens, 'token_len_range':token_len_range})))
            
    logger.info('generating vocabulary')
    corpus = MediaWikiCorpus(input_articles_path, article_min_tokens, token_len_range[0], token_len_range[1], ('Help:',))
    corpus.dictionary = Dictionary(corpus.get_texts())
    corpus.dictionary.filter_extremes(no_below=no_below, no_above=no_above, keep_n=keep_words)
    corpus.dictionary.compactify()
    output_id2word_path = output_prefix + '.id2word.cpickle'
    corpus.dictionary.save(output_id2word_path)    
    
    logger.info('generating bag of words corpus')
    corpus.metadata = True
    output_corpus_path = output_prefix + '.mm'
    MmCorpus.serialize(output_corpus_path, corpus, progress_cnt=10000, metadata=True)
        
    
    
    
if __name__ == '__main__':
    main()
    
