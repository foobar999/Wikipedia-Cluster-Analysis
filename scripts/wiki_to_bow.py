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
from gensim.corpora import Dictionary, HashDictionary, MmCorpus, WikiCorpus
from utils.utils import init_gensim_logger

DEFAULT_DICT_SIZE = 100000
DEFAULT_NO_BELOW = 5
DEFAULT_NO_ABOVE = 0.5
DEFAULT_ART_MIN_TOKENS = 50
DEFAULT_TOKEN_LEN_RANGE = [2,20]
DEFAULT_NAMESPACES = 0

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
    
    program, logger = init_gensim_logger()
    
    logger.info('running {} with:\n{}'.format(program,pformat({'input_articles_path':input_articles_path, 'output_prefix':output_prefix, 'keep_words':keep_words, 'no_below':no_below, 'no_above':no_above, 'article_min_tokens':article_min_tokens, 'token_len_range':token_len_range, 'namespaces':namespaces})))
    
    
    # mit Hashing-Trick -> schneller, weniger schön betrachtbar
    # dictionary = HashDictionary(id_range=keep_words, debug=False)
    # dictionary.allow_update = True  # start collecting document frequencies
    # wiki = WikiCorpus(input_articles_path, lemmatize=False, dictionary=dictionary, article_min_tokens=article_min_tokens, token_min_len=token_min_len, token_max_len=token_max_len, filter_namespaces=namespaces)
    # MmCorpus.serialize(output_files_prefix + '-bow.mm', wiki, progress_cnt=10000)
    # dictionary.filter_extremes(no_below=no_below, no_above=no_above, keep_n=keep_words) # im Original stand hier DEFAULT_DICT_SIZE?
    # dictionary.save_as_text(output_files_prefix + '-wordids.txt.bz2')
    # wiki.save(output_files_prefix + '-corpus.pkl.bz2')
    # ohne Hashing-Trick
    wiki = WikiCorpus(input_articles_path, lemmatize=False, article_min_tokens=article_min_tokens, token_min_len=token_len_range[0], token_max_len=token_len_range[1], filter_namespaces=namespaces)
    wiki.metadata = True    # schreibe Metadaten inkl. Titel?
    wiki.dictionary.filter_extremes(no_below=no_below, no_above=no_above, keep_n=keep_words)
    wiki.dictionary.compactify()
    output_corpus_path = output_prefix + '.mm'
    output_id2word_path = output_prefix + '.id2word.cpickle'
    MmCorpus.serialize(output_corpus_path, wiki, progress_cnt=1000, metadata=True)
    wiki.dictionary.save(output_id2word_path)
    logger.info("finished running %s", program)
    
    
if __name__ == '__main__':
    main()
    
