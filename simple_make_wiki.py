# leichte Adaption von https://github.com/RaRe-Technologies/gensim/blob/master/gensim/scripts/make_wikicorpus.py

import os
import sys
import argparse
import logging
from gensim.corpora import Dictionary, HashDictionary, MmCorpus, WikiCorpus
from gensim.models import TfidfModel

DEFAULT_DICT_SIZE = 100000
DEFAULT_NO_BELOW = 5
DEFAULT_NO_ABOVE = 0.5
DEFAULT_ART_MIN_TOKENS = 50
DEFAULT_TOKEN_MIN_LEN = 2
DEFAULT_TOKEN_MAX_LEN = 20
DEFAULT_NAMESPACES = 0

def main():
    parser = argparse.ArgumentParser(description='creates gensim data files from a given XML.BZ2 MediaWiki dump', epilog='Example: ./{} enwiki-pages-articles.xml.bz2 topicdata/enwiki --keep-words 1000 --no-below=10 --no-above=0.5 --article-min-tokens 50 --token-min-len 2 --token-max-len 20 --namespaces 0 '.format(sys.argv[0]))
    parser.add_argument("idump", type=argparse.FileType('r'), help='path to input XML.BZ2 articles dump')
    parser.add_argument("oprefix", help='prefix for generated gensim files')
    parser.add_argument("--keep-words", type=int, default=DEFAULT_DICT_SIZE, help='number of most frequent word types to keep (default {})'.format(DEFAULT_DICT_SIZE))
    parser.add_argument("--no-below", type=int, default=DEFAULT_NO_BELOW, help='Keep only tokes which appear in at least NO_BELOW documents (default {})'.format(DEFAULT_NO_BELOW))
    parser.add_argument("--no-above", type=float, default=DEFAULT_NO_ABOVE, help='Keep only tokes which appear in at most NO_ABOVE*CORPUSSIZE documents (default {})'.format(DEFAULT_NO_ABOVE))
    parser.add_argument("--article-min-tokens", type=int, default=DEFAULT_ART_MIN_TOKENS, help='Analyze only articles of >= ARTICLE_MIN_TOKENS tokens default {}). Should be >=1'.format(DEFAULT_ART_MIN_TOKENS))
    parser.add_argument("--token-min-len", type=int, default=DEFAULT_TOKEN_MIN_LEN, help='Consider only tokens of at least TOKEN_MIN_LEN chars (default {})'.format(DEFAULT_TOKEN_MIN_LEN))
    parser.add_argument("--token-max-len", type=int, default=DEFAULT_TOKEN_MAX_LEN, help='Consider only tokens of at most TOKEN_MAX_LEN chars (default {})'.format(DEFAULT_TOKEN_MAX_LEN))
    parser.add_argument("--namespaces", nargs='+', type=int, default=(DEFAULT_NAMESPACES), help='Consider only given MediaWiki namespaces (default {})'.format(DEFAULT_NAMESPACES))
    
    
    args = parser.parse_args()
    input_articles_path = args.idump.name
    output_files_prefix = args.oprefix 
    keep_words = args.keep_words
    no_below,no_above = args.no_below,args.no_above
    article_min_tokens = args.article_min_tokens
    token_min_len,token_max_len = args.token_min_len,args.token_max_len
    namespaces = tuple(str(ns) for ns in args.namespaces)
    
    if not os.path.isdir(os.path.dirname(output_files_prefix)):
        parser.print_help(sys.stderr)
        raise SystemExit('Error: Directory "{}" not exits. Create the directory and try again.'.format(os.path.dirname(output_files_prefix)))
    
    program = os.path.basename(sys.argv[0])
    logger = logging.getLogger(program)
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')    
    logging.root.level = logging.INFO
    
    logger.info('running {} with input_articles {}, output_prefix {}, keep_words {}, no_below {}, no_above {}, article_min_tokens {}, token_min_len {}, token_max_len {}, namespaces {}'.format(sys.argv[0],input_articles_path,output_files_prefix,keep_words,no_below,no_above,article_min_tokens,token_min_len,token_max_len,namespaces))
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
    print(wiki.__dict__)
    wiki.dictionary.filter_extremes(no_below=no_below, no_above=no_above, keep_n=keep_words)
    MmCorpus.serialize(output_files_prefix + '-bow.mm', wiki, progress_cnt=10000)
    wiki.dictionary.save_as_text(output_files_prefix + '-wordids.txt.bz2')
    dictionary = Dictionary.load_from_text(output_files_prefix + '-wordids.txt.bz2')
    del wiki
    
    mm = MmCorpus(output_files_prefix + '-bow.mm')
    tfidf = TfidfModel(mm, id2word=dictionary, normalize=True)
    tfidf.save(output_files_prefix + '.tfidf_model')

    MmCorpus.serialize(output_files_prefix + '-tfidf.mm', tfidf[mm], progress_cnt=10000)
    logger.info("finished running %s", program)
    
    
if __name__ == '__main__':
    main()
    
