# leichte Adaption von https://github.com/RaRe-Technologies/gensim/blob/master/gensim/scripts/make_wikicorpus.py

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
DEFAULT_TOKEN_MIN_LEN = 2
DEFAULT_TOKEN_MAX_LEN = 20
DEFAULT_NAMESPACES = 0

def main():
    parser = argparse.ArgumentParser(description='creates from a given xml.bz2 MediaWiki dump a text-based gensim bag-of-words .mm corpus representation file, a .txt/.txt.bz2 id2word dictionary file and a binary .metadata.cpickle ID->(PageID, document title) mapping file', epilog='Example: ./{} mycorpus-pages-articles.xml.bz2 mycorpus-bow.mm mycorpus-dict.txt.bz2 --keep-words 1000 --no-below=10 --no-above=0.5 --article-min-tokens 50 --token-min-len 2 --token-max-len 20 --namespaces 0 '.format(sys.argv[0]))
    parser.add_argument("articles_dump", type=argparse.FileType('r'), help='path to input .xml.bz2 articles dump')
    parser.add_argument("corpus", type=argparse.FileType('w'), help='path to output bow .mm corpus ((MatrixMarket representation, .mm.bz2 is not supported)')
    parser.add_argument("id2word", type=argparse.FileType('w'), help='path to output id2word .txt/.txt.bz2 dictionary')
    parser.add_argument("--keep-words", type=int, default=DEFAULT_DICT_SIZE, help='number of most frequent word types to keep (default {})'.format(DEFAULT_DICT_SIZE))
    parser.add_argument("--no-below", type=int, default=DEFAULT_NO_BELOW, help='Keep only tokes which appear in at least NO_BELOW documents (default {})'.format(DEFAULT_NO_BELOW))
    parser.add_argument("--no-above", type=float, default=DEFAULT_NO_ABOVE, help='Keep only tokes which appear in at most NO_ABOVE*CORPUSSIZE documents (default {})'.format(DEFAULT_NO_ABOVE))
    parser.add_argument("--article-min-tokens", type=int, default=DEFAULT_ART_MIN_TOKENS, help='Analyze only articles of >= ARTICLE_MIN_TOKENS tokens default {}). Should be >=1'.format(DEFAULT_ART_MIN_TOKENS))
    parser.add_argument("--token-min-len", type=int, default=DEFAULT_TOKEN_MIN_LEN, help='Consider only tokens of at least TOKEN_MIN_LEN chars (default {})'.format(DEFAULT_TOKEN_MIN_LEN))
    parser.add_argument("--token-max-len", type=int, default=DEFAULT_TOKEN_MAX_LEN, help='Consider only tokens of at most TOKEN_MAX_LEN chars (default {})'.format(DEFAULT_TOKEN_MAX_LEN))
    parser.add_argument("--namespaces", nargs='+', type=int, default=(DEFAULT_NAMESPACES), help='Consider only given MediaWiki namespaces (default {})'.format(DEFAULT_NAMESPACES))    
    parser.add_argument("--save-titles", action='store_true', help='save to binary <corpus>.metadata.cpickle file document id mappings: {docID: (pageID,document title)}')
    
    args = parser.parse_args()
    input_articles_path = args.articles_dump.name
    output_corpus_path = args.corpus.name
    output_id2word_path = args.id2word.name
    keep_words = args.keep_words
    no_below,no_above = args.no_below,args.no_above
    article_min_tokens = args.article_min_tokens
    token_min_len,token_max_len = args.token_min_len,args.token_max_len
    namespaces = tuple(str(ns) for ns in args.namespaces)
    save_titles = args.save_titles 
    
    program, logger = init_gensim_logger()
    
    logger.info('running {} with:\n{}'.format(program,pformat({'input_articles_path':input_articles_path, 'output_corpus_path':output_corpus_path ,'output_id2word_path':output_id2word_path, 'keep_words':keep_words, 'no_below':no_below, 'no_above':no_above, 'article_min_tokens':article_min_tokens, 'token_min_len':token_min_len, 'token_max_len':token_max_len, 'namespaces':namespaces, 'save_titles':save_titles})))
    
    # mit Hashing-Trick -> schneller, weniger schön betrachtbar
    # dictionary = HashDictionary(id_range=keep_words, debug=False)
    # dictionary.allow_update = True  # start collecting document frequencies
    # wiki = WikiCorpus(input_articles_path, lemmatize=False, dictionary=dictionary, article_min_tokens=article_min_tokens, token_min_len=token_min_len, token_max_len=token_max_len, filter_namespaces=namespaces)
    # MmCorpus.serialize(output_files_prefix + '-bow.mm', wiki, progress_cnt=10000)
    # dictionary.filter_extremes(no_below=no_below, no_above=no_above, keep_n=keep_words) # im Original stand hier DEFAULT_DICT_SIZE?
    # dictionary.save_as_text(output_files_prefix + '-wordids.txt.bz2')
    # wiki.save(output_files_prefix + '-corpus.pkl.bz2')
    # ohne Hashing-Trick
    wiki = WikiCorpus(input_articles_path, lemmatize=False, article_min_tokens=article_min_tokens, token_min_len=token_min_len, token_max_len=token_max_len, filter_namespaces=namespaces)
    wiki.metadata = save_titles    # schreibe Metadaten (inkl. Titel)?
    wiki.dictionary.filter_extremes(no_below=no_below, no_above=no_above, keep_n=keep_words)
    wiki.dictionary.compactify()
    MmCorpus.serialize(output_corpus_path, wiki, progress_cnt=10000, metadata=save_titles)
    wiki.dictionary.save_as_text(output_id2word_path)
    logger.info("finished running %s", program)
    
    
if __name__ == '__main__':
    main()
    
