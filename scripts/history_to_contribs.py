
import os, sys
import logging
import argparse
from pprint import pformat
from mw import xml_dump
from gensim.utils import smart_open
from gensim.corpora import Dictionary, MmCorpus
from utils.utils import init_logger, number_of_tokens, is_mainspace_page, read_lines, is_valid_contributor

# TODO IP ignorieren Flag?

logger = init_logger()

    
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

# liefert einen Generator ((Revisionen als Tupel, Seitentitel) für alle Seiten im Mainspace)
def get_filtered_revisions_of_pages(history_dump, min_doc_authors, namespace_prefixes):
    num_pages_total = 0
    num_pages_mainspace = 0
    num_revisions_mainspace = 0
    num_revisions_ms_of_valid_users = 0
    num_pages_ms_enough_different_valid_users = 0
    for page in history_dump:
        num_pages_total += 1
        logger.debug('page {}'.format(page.title))
        if is_mainspace_page(page, namespace_prefixes):
            num_pages_mainspace += 1
            logger.debug('page {} considered mainspace'.format(page.title))
            revisions = tuple(revision for revision in page)
            num_revisions_mainspace += len(revisions)
            logger.debug('page {} having {} revisions'.format(page.title, len(revisions)))
            revisions_of_valid_users = tuple(revision for revision in revisions if is_valid_contributor(revision.contributor))
            num_revisions_ms_of_valid_users += len(revisions_of_valid_users)
            logger.debug('page {} having {} revisions of valid users'.format(page.title, len(revisions_of_valid_users)))
            num_different_authors = len(set(rev.contributor.user_text for rev in revisions_of_valid_users))
            logger.debug('page {} having {} different authors -> keep?: {}'.format(page.title, num_different_authors, num_different_authors >= min_doc_authors))
            if num_different_authors >= min_doc_authors:
                num_pages_ms_enough_different_valid_users += 1
                yield revisions_of_valid_users,page.title
                
    logger.info('{} pages total'.format(num_pages_total))
    logger.info('{} pages considered mainspace'.format(num_pages_mainspace))
    logger.info('{} revisions in mainspace pages'.format(num_revisions_mainspace))
    logger.info('{} revisions of valid users in mainspace '.format(num_revisions_ms_of_valid_users))
    logger.info('{} pages in mainspace containing at least {} different users'.format(num_pages_ms_enough_different_valid_users, min_doc_authors))
    
    
# liefert einen Generator ((Autorname für alle Revisionen) für alle Seiten im Mainspace)
def get_revision_authors_of_pages(history_dump, min_doc_authors, namespace_prefixes):
    for revisions, pagetitle in get_filtered_revisions_of_pages(history_dump, min_doc_authors, namespace_prefixes):
        yield (revision.contributor.user_text for revision in revisions)
    

# liefert einen Generator ((Autor-ID, Revision) für alle Revisionen), wobei das Dictionary den Autornamen enthalten muss
def get_authorid_rev_pairs_by_dictionary(revisions, id2author):
    for revision in revisions:
        username = revision.contributor.user_text
        if username in id2author.token2id:
            yield id2author.token2id[username], revision
    
    
# liefert einen Generator (((Autor-ID, Revisionswert) für alle Revisionen), Seitentitel für alle Seiteini im Mainspace)
def get_revision_values_of_pages(history_dump, id2author, revision_value_fun, min_doc_authors, namespace_prefixes):
    num_contribs_of_dict_authors = 0
    for revisions, pagetitle in get_filtered_revisions_of_pages(history_dump, min_doc_authors, namespace_prefixes):
        authorid_rev_pairs = tuple(authorid_rev for authorid_rev in get_authorid_rev_pairs_by_dictionary(revisions, id2author))
        logger.debug('page {} having {} revisions of authors in dictionary'.format(pagetitle, len(authorid_rev_pairs)))
        num_contribs_of_dict_authors += len(authorid_rev_pairs)
        #if len(authorid_rev_pairs) > 0:
        logger.debug('calculating revision values of non-empty revision list')
        authorid_revisionvalue_pairs = revision_value_fun(iter(authorid_rev_pairs))
        yield authorid_revisionvalue_pairs, pagetitle
    logger.info('loaded {} revisions of authors in dictionary'.format(num_contribs_of_dict_authors))


#einfache Klasse, die einen Generator wrappt und self.metadata = True setzt, damit gensim die Artikeltitel speichert
class MetadataCorpus(object):
    def __init__(self, generator):
        self.generator = generator
        self.metadata = True
    def __iter__(self):
        yield from self.generator
    
    
def main():
    parser = argparse.ArgumentParser(description='creates an id2author mapping gensim dictionary a document->authorid contributions MatrixMarket file and a binary article title file from a given WikiMedia *-pages-meta-history dump (considering only articles in mainspace!)')
    parser.add_argument('--history-dump', type=argparse.FileType('r'), help='path to input WikiMedia *-pages-meta-history file (.xml/.xml.bz2)', required=True)
    parser.add_argument('--id2author', type=argparse.FileType('w'), help='path to output binary id2author dictionary (.cpickle/.cpickle.bz2)', required=True)
    parser.add_argument('--contribs', type=argparse.FileType('w'), help='path to output MatrixMarket contributions .mm file; also creates a binary article title file CONTRIBS.metadata.cpickle', required=True)
    parser.add_argument('--contribution-value', choices=CONTRIBUTION_VALUE_CHOICES, help='calculated per-contribution value; choices: {}'.format(CONTRIBUTION_VALUE_CHOICES), required=True)
    parser.add_argument('--min-auth-docs', type=int, help='only consider contributions of authors that contributed to at least MIN_AUTH_DOCS different documents', required=True)
    parser.add_argument('--min-doc-auths', type=int, help='only consider documents with MIN_DOC_AUTHS different authors')
    parser.add_argument("--namespace-prefixes", type=argparse.FileType('r'), help='file of namespace prefixes to ignore')    
        
    args = parser.parse_args()
    args = parser.parse_args()
    input_history_dump_path = args.history_dump.name
    output_id2author_path = args.id2author.name
    output_contribs_path = args.contribs.name
    contribution_value = args.contribution_value
    min_author_docs = args.min_auth_docs
    min_doc_authors = args.min_doc_auths
    namespace_prefixes = read_lines(args.namespace_prefixes.name) if args.namespace_prefixes else ()
        
    logger.info('running with:\n{}'.format(pformat({'input_history_dump_path':input_history_dump_path, 'output_id2author_path':output_id2author_path, 'output_contribs_path':output_contribs_path, 'contribution_value':contribution_value, 'min_author_docs':min_author_docs, 'min_doc_authors':min_doc_authors, 'namespace_prefixes':namespace_prefixes})))        
            
    with smart_open(input_history_dump_path) as history_dump_file:    
        logger.info('generating author->id mappings')
        history_dump = xml_dump.Iterator.from_file(history_dump_file)
        # benutze id2word-Dictionary von gensim als id2author-Dictionary
        id2author = Dictionary(get_revision_authors_of_pages(history_dump, min_doc_authors, namespace_prefixes))
        # entferne Autoren, die an weniger als min_author_docs beteiligt
        id2author.filter_extremes(no_below=min_author_docs, no_above=1, keep_n=None, keep_tokens=None)
        id2author.save(output_id2author_path)
        
    with smart_open(input_history_dump_path) as history_dump_file: 
        logger.info('generating MatrixMarket representation per revision: (docid, authorid, value of revision)')
        history_dump = xml_dump.Iterator.from_file(history_dump_file)
        revision_value_fun = CONTRIBUTION_VALUE_FUNCTIONS[contribution_value]
        doc_auth_contribs = MetadataCorpus(get_revision_values_of_pages(history_dump, id2author, revision_value_fun, min_doc_authors, namespace_prefixes))
        MmCorpus.serialize(output_contribs_path, corpus=doc_auth_contribs, id2word=id2author, metadata=True, progress_cnt=10000)    
    
    
        
if __name__ == '__main__':
    main()
    
    
    