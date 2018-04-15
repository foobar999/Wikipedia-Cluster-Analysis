import os, sys
import logging
import argparse
from pprint import pformat
from mw import xml_dump
from gensim.utils import smart_open
from gensim.corpora import Dictionary, MmCorpus
from six import itervalues, iteritems
from utils.utils import init_gensim_logger, number_of_tokens, debug_mode_set, is_page_in_mainspace

# TODO IP ignorieren Flag?
    
def contrib_value_one(ids_revisions):
    for authorid,rev in ids_revisions:
        yield authorid, 1        
        
# resultierende MM-Matrix wird kleiner, da ggf. 0en zurückgegeben, die ja nicht mitgespeichert werden
# -> Löschen zählt nicht als Beitrag
# -> Wörter tauschen zählt nicht als Beitrag
# -> Leerzeichen hinzufügen zählt nicht
def contrib_value_diff_numterms(ids_revisions):
    authorid,rev = next(ids_revisions)
    prev_num_toks = number_of_tokens(rev.text)
    yield authorid, prev_num_toks
    for authorid,rev in ids_revisions:
        num_toks = number_of_tokens(rev.text)
        yield authorid, max(0,num_toks-prev_num_toks)
        prev_num_toks = num_toks
    
CONTRIBUTION_VALUE_CHOICES = {
    'one': '1 per contribution',
    'diff_numterms': 'max(0, difference of number of terms to previous contrib'
}
    
# liefert zu einem Generator von Paaren (AutorID,Revision) einen Generator von (AutorID,Beitragswert(Revision))
CONTRIBUTION_VALUE_FUNCTIONS = {
    'one': contrib_value_one,
    'diff_numterms': contrib_value_diff_numterms
}

def get_mainspace_pages(history_dump):
    return (page for page in history_dump if is_page_in_mainspace(page))
    
    
# liefert einen Generator: ((Username je Revision) je Artikel)
def create_author2id_dictionary(history_dump):
    dump_authors = ((revision.contributor.user_text for revision in page) for page in get_mainspace_pages(history_dump))
    return Dictionary(dump_authors)
        
    
# einfache Klasse, die einen Generator wrappt und self.metadata = True setzt, damit gensim die Artikeltitel speichert
class MetadataCorpus(object):
    def __init__(self, generator):
        self.generator = generator
        self.metadata = True
    def __iter__(self):
        yield from self.generator

# beachte: ein Dokument geht auch in die Gesamtzahl der Dokumente ein, wenn alle Revisionen weggefilter wurden!7

# liefert einen MetadataCorpus-gewrappten Generator: ((UserID, Beitrag je Revision), Titel je Artikel)
def create_doc_auth_contributions(history_dump, id2author, revision_value_fun):
    def get_revisions_of_page(page):
        for rev in page:
            username = rev.contributor.user_text
            if username in id2author.token2id:
                yield (id2author.token2id[username], rev)
    
    #for page in history_dump:
    #    filtered_revisions = tuple(auth_rev for auth_rev in get_revisions_of_page(page))
    #    if len(filtered_revisions) > 0:
    #        yield revision_value_fun(iter(filtered_revisions))
    
    return MetadataCorpus((revision_value_fun(get_revisions_of_page(page)),page.title) for page in get_mainspace_pages(history_dump)) 
    
    
def main():
    parser = argparse.ArgumentParser(description='creates an id2author mapping gensim dictionary a document->authorid contributions MatrixMarket file and a binary article title file from a given WikiMedia *-pages-meta-history dump (considering only articles in mainspace!)', epilog='Example: ./{} --history-dump=enwiki-pages-meta-history.xml.bz2 --id2author=enwiki-id2author.cpickle.bz2 --contribs=enwiki-contributions.mm --contribution-value=count --min-auth-docs=2'.format(sys.argv[0]))
    parser.add_argument('--history-dump', type=argparse.FileType('r'), help='path to input WikiMedia *-pages-meta-history file (.xml/.xml.bz2)', required=True)
    parser.add_argument('--id2author', type=argparse.FileType('w'), help='path to output binary id2author dictionary (.cpickle/.cpickle.bz2)', required=True)
    parser.add_argument('--contribs', type=argparse.FileType('w'), help='path to output MatrixMarket contributions .mm file; also creates a binary article title file CONTRIBS.metadata.cpickle', required=True)
    parser.add_argument('--contribution-value', choices=CONTRIBUTION_VALUE_CHOICES, help='calculated per-contribution value; choices: {}'.format(CONTRIBUTION_VALUE_CHOICES), required=True)
    parser.add_argument('--min-auth-docs', type=int, help='only consider contributions of authors that contributed to at least MIN_AUTH_DOCS different documents', required=True)
    
    args = parser.parse_args()
    input_history_dump_path = args.history_dump.name
    output_id2author_path = args.id2author.name
    output_contribs_path = args.contribs.name
    contribution_value = args.contribution_value
    min_author_docs = args.min_auth_docs
    
    program, logger = init_gensim_logger()
    logger.info('running {} with:\n{}'.format(program, pformat({'input_history_dump_path':input_history_dump_path, 'output_id2author_path':output_id2author_path, 'output_contribs_path':output_contribs_path, 'contribution_value':contribution_value, 'min_author_docs':min_author_docs})))
        
    with smart_open(input_history_dump_path) as history_dump_file:    
        logger.info('generating author->id mappings')
        history_dump_iter = xml_dump.Iterator.from_file(history_dump_file)
        # benutze id2word-Dictionary von gensim als id2author-Dictionary
        id2author = create_author2id_dictionary(history_dump_iter)
        # entferne Autoren, die an weniger als min_author_docs beteiligt
        id2author.filter_extremes(no_below=min_author_docs, no_above=1, keep_n=None, keep_tokens=None)
        id2author.save(output_id2author_path)
        
    with smart_open(input_history_dump_path) as history_dump_file: 
        logger.info('generating MatrixMarket representation per revision: (docid, authorid, value of revision)')
        history_dump_iter = xml_dump.Iterator.from_file(history_dump_file)
        revision_value_fun = CONTRIBUTION_VALUE_FUNCTIONS[contribution_value]
        doc_auth_contribs = create_doc_auth_contributions(history_dump_iter, id2author, revision_value_fun) 
        MmCorpus.serialize(output_contribs_path, corpus=doc_auth_contribs, id2word=id2author, metadata=True, progress_cnt=10000)    
    
    
        
if __name__ == '__main__':
    main()

    
    
# in Anlehnung an filter_extremes() und filter_tokens() https://github.com/RaRe-Technologies/gensim/blob/master/gensim/corpora/dictionary.py
# def filter_author2id_without_compactify(author2id, no_below):
    # good_ids = (v for v in itervalues(author2id.token2id) if no_below <= author2id.dfs.get(v, 0))
    # good_ids = sorted(good_ids, key=author2id.dfs.get, reverse=True)
    # good_ids = set(good_ids)
    # author2id.token2id = {token: tokenid for token, tokenid in iteritems(author2id.token2id) if tokenid in good_ids}
    # author2id.dfs = {tokenid: freq for tokenid, freq in iteritems(author2id.dfs) if tokenid in good_ids}
    
    
    