# leichte Adaption von https://github.com/RaRe-Technologies/gensim/blob/master/gensim/scripts/make_wikicorpus.py

description = """
creates from a given .xml.bz2 MediaWiki dump multiple prefixed gensim files:
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

# TODO raus
DEFAULT_DICT_SIZE = 100000
DEFAULT_NO_BELOW = 5
DEFAULT_NO_ABOVE = 0.5
DEFAULT_ART_MIN_TOKENS = 50
DEFAULT_TOKEN_LEN_RANGE = [2,20]
DEFAULT_NAMESPACES = 0

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
    num_tokens = 0
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
                num_tokens += len(tokens)
                if metadata:
                    yield tokens, (title, pageid)
                else:
                    yield tokens
    logger.info('loaded {} articles (total), {} articles (filtered), {} tokens (filtered)'.format(num_articles_total,num_articles,num_tokens))
    
                    
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
    parser = argparse.ArgumentParser(description=description, epilog='Example: ./{} mycorpus-pages-articles.xml.bz2 output/mycorpus --keep-words 1000 --no-below=10 --no-above=0.5 --article-min-tokens 50 --token-len-range 2 20 --namespaces 0'.format(sys.argv[0]))
    parser.add_argument("articles_dump", type=argparse.FileType('r'), help='path to input .xml.bz2 articles dump')
    parser.add_argument("out_prefix", help='prefix of the generated output files')
    parser.add_argument("--keep-words", type=int, default=DEFAULT_DICT_SIZE, help='number of most frequent word types to keep (default {})'.format(DEFAULT_DICT_SIZE))
    parser.add_argument("--no-below", type=int, default=DEFAULT_NO_BELOW, help='Keep only tokes which appear in at least NO_BELOW documents (default {})'.format(DEFAULT_NO_BELOW))
    parser.add_argument("--no-above", type=float, default=DEFAULT_NO_ABOVE, help='Keep only tokes which appear in at most NO_ABOVE*CORPUSSIZE documents (default {})'.format(DEFAULT_NO_ABOVE))
    parser.add_argument("--article-min-tokens", type=int, default=DEFAULT_ART_MIN_TOKENS, help='Analyze only articles of >= ARTICLE_MIN_TOKENS tokens default {}). Should be >=1'.format(DEFAULT_ART_MIN_TOKENS))
    parser.add_argument("--token-len-range", type=int, nargs=2, default=DEFAULT_TOKEN_LEN_RANGE, metavar=('MIN','MAX'), help='Consider only tokens of at least MIN and at most MAX chars (default {} {})'.format(DEFAULT_TOKEN_LEN_RANGE[0],DEFAULT_TOKEN_LEN_RANGE[1]))
    parser.add_argument("--namespaces", nargs='+', type=int, default=(DEFAULT_NAMESPACES), help='Consider only given MediaWiki namespaces (default {})'.format(DEFAULT_NAMESPACES))    
    
    args = parser.parse_args()
    input_articles_path = args.articles_dump.name
    output_prefix = args.out_prefix
    keep_words = args.keep_words
    no_below,no_above = args.no_below,args.no_above
    article_min_tokens = args.article_min_tokens
    token_len_range = args.token_len_range
    namespaces = tuple(str(ns) for ns in args.namespaces)
    
    logger.info('running {} with:\n{}'.format(program,pformat({'input_articles_path':input_articles_path, 'output_prefix':output_prefix, 'keep_words':keep_words, 'no_below':no_below, 'no_above':no_above, 'article_min_tokens':article_min_tokens, 'token_len_range':token_len_range, 'namespaces':namespaces})))
            
    logger.info('generating vocabulary')
    #article_data = get_filtered_articles_data_from_path(input_articles_path, 1, 2, 20, ('Help:',), False)
    corpus = MediaWikiCorpus(input_articles_path, 1, 2, 20, ('Help:',))
    corpus.dictionary = Dictionary(corpus.get_texts())
    corpus.dictionary.filter_extremes(no_below=no_below, no_above=no_above, keep_n=keep_words)
    corpus.dictionary.compactify()
    output_id2word_path = output_prefix + '.id2word.cpickle'
    corpus.dictionary.save(output_id2word_path)    
    
    logger.info('generating bag of words corpus')
    output_corpus_path = output_prefix + '.mm'
    MmCorpus.serialize(output_corpus_path, corpus, progress_cnt=10000, metadata=True)
        
    
    #wiki = NoNamespaceWikiCorpus(input_articles_path, lemmatize=False, article_min_tokens=article_min_tokens, token_min_len=token_len_range[0], token_max_len=token_len_range[1], filter_namespaces=namespaces)
    #for dat in wiki.get_texts():
    #    print(dat)
    
    # return 
    
    # wiki.metadata = True    # schreibe Metadaten inkl. Titel?
    # wiki.dictionary.filter_extremes(no_below=no_below, no_above=no_above, keep_n=keep_words)
    # wiki.dictionary.compactify()
    # output_corpus_path = output_prefix + '.mm'
    # output_id2word_path = output_prefix + '.id2word.cpickle'
    # MmCorpus.serialize(output_corpus_path, wiki, progress_cnt=1000, metadata=True)
    # wiki.dictionary.save(output_id2word_path)
    # logger.info("finished running %s", program)
    
    
if __name__ == '__main__':
    main()
    
