"""
Modifikation von gensim.corpora.Wikicorpus 
https://github.com/RaRe-Technologies/gensim/blob/master/gensim/corpora/wikicorpus.py
"""

import bz2, multiprocessing, logging
from xml.etree.cElementTree import iterparse
from gensim import utils
from gensim.corpora import WikiCorpus
from gensim.corpora.wikicorpus import tokenize, extract_pages, init_to_ignore_interrupt, _process_article, get_namespace
from gensim.corpora.wikicorpus import ARTICLE_MIN_WORDS, TOKEN_MIN_LEN, TOKEN_MAX_LEN, IGNORED_NAMESPACES

logger = logging.getLogger(__name__)

# nimmt namespace='0' an, falls kein <ns>-Tag gefunden
def extract_pages_without_namespaces(f, filter_namespaces=False):

    elems = (elem for _, elem in iterparse(f, events=("end",)))

    elem = next(elems)
    namespace = get_namespace(elem.tag)
    ns_mapping = {"ns": namespace}
    page_tag = "{%(ns)s}page" % ns_mapping
    text_path = "./{%(ns)s}revision/{%(ns)s}text" % ns_mapping
    title_path = "./{%(ns)s}title" % ns_mapping
    ns_path = "./{%(ns)s}ns" % ns_mapping
    pageid_path = "./{%(ns)s}id" % ns_mapping

    for elem in elems:
        if elem.tag == page_tag:
            title = elem.find(title_path).text
            text = elem.find(text_path).text

            if filter_namespaces:
                #ns = elem.find(ns_path).text
                res = elem.find(ns_path)
                ns = res.text if res else '0'                
                if ns not in filter_namespaces:
                    text = None

            pageid = elem.find(pageid_path).text
            yield title, text or "", pageid  # empty page will yield None

            elem.clear()

            
class NoNamespaceWikiCorpus(WikiCorpus):
    """
    wie gensim.corpora.WikiCorpus, erlaubt aber ein fehlendes <ns>-Tag und nimmt automatisch den Namespace 0 an
    """
    
    def __init__(self, fname, processes=None, lemmatize=utils.has_pattern(), dictionary=None, filter_namespaces=('0',), tokenizer_func=tokenize, article_min_tokens=ARTICLE_MIN_WORDS, token_min_len=TOKEN_MIN_LEN, token_max_len=TOKEN_MAX_LEN, lower=True):
        super().__init__(fname, processes, lemmatize, dictionary, filter_namespaces, tokenizer_func, article_min_tokens, token_min_len, token_max_len, lower)
        
    def get_texts(self):
        articles, articles_all = 0, 0
        positions, positions_all = 0, 0
        tokenization_params = (self.tokenizer_func, self.token_min_len, self.token_max_len, self.lower)
        texts = \
            ((text, self.lemmatize, title, pageid, tokenization_params)
             for title, text, pageid
             #in extract_pages(bz2.BZ2File(self.fname), self.filter_namespaces))
             in extract_pages_without_namespaces(bz2.BZ2File(self.fname), self.filter_namespaces))
        pool = multiprocessing.Pool(self.processes, init_to_ignore_interrupt)

        try:
            for group in utils.chunkize(texts, chunksize=10 * self.processes, maxsize=1):
                for tokens, title, pageid in pool.imap(_process_article, group):
                    articles_all += 1
                    positions_all += len(tokens)
                    if len(tokens) < self.article_min_tokens or \
                            any(title.startswith(ignore + ':') for ignore in IGNORED_NAMESPACES):
                        continue
                    articles += 1
                    positions += len(tokens)
                    if self.metadata:
                        yield (tokens, (pageid, title))
                    else:
                        yield tokens

        except KeyboardInterrupt:
            logger.warn(
                "user terminated iteration over Wikipedia corpus after %i documents with %i positions "
                "(total %i articles, %i positions before pruning articles shorter than %i words)",
                articles, positions, articles_all, positions_all, ARTICLE_MIN_WORDS
            )
        else:
            logger.info(
                "finished iterating over Wikipedia corpus of %i documents with %i positions "
                "(total %i articles, %i positions before pruning articles shorter than %i words)",
                articles, positions, articles_all, positions_all, ARTICLE_MIN_WORDS
            )
            self.length = articles  # cache corpus length
        finally:
            pool.terminate()
            
            
            
            