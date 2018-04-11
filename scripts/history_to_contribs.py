import os, sys
import logging
import argparse
from pprint import pformat
from mw import xml_dump
from gensim.utils import smart_open
from gensim.corpora import Dictionary, MmCorpus
from utils.utils import init_gensim_logger, number_of_tokens

# TODO gegen redirect,namespace o.Ä. prüfen
# TODO sowas wie "min-authors"?
# TODO IP ignorieren Flag
    
CONTRIBUTION_VALUE_CHOICES = {
    'one': '1 per contribution',
    'numterms': 'number of terms per contribution',
    'diff_numterms': 'max(0, difference of number of terms to previous contrib'
}


def contrib_value_one(ids_revisions):
    for authorid,rev in ids_revisions:
        yield authorid, 1
        
def contrib_value_numterms(ids_revisions):
    for authorid,rev in ids_revisions:
        yield authorid, number_of_tokens(rev.text)
        
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
    
    
# liefert zu einem Generator von Paaren (AutorID,Revision) einen Generator von (AutorID,Beitragswert(Revision))
CONTRIBUTION_VALUE_FUNCTIONS = {
    'one': contrib_value_one,
    'numterms': contrib_value_numterms,
    'diff_numterms': contrib_value_diff_numterms
}
    
    
def create_author2id_dictionary(history_dump):
    dump_authors = ((revision.contributor.user_text for revision in page) for page in history_dump)
    return Dictionary(dump_authors)
    
    
def create_doc_auth_contributions(history_dump, id2author, revision_value_fun):
    dump_doc_auth_contribs = (revision_value_fun(((id2author.token2id[rev.contributor.user_text], rev) for rev in page)) for page in history_dump)
    return dump_doc_auth_contribs 
    
    
def main():
    parser = argparse.ArgumentParser(description='creates an id2author mapping gensim dictionary a document->authorid contributions MatrixMarket file from a given WikiMedia *-pages-meta-history dump', epilog='Example: ./{} --history-dump=enwiki-pages-meta-history.xml.bz2 --id2author=enwiki-id2author.cpickle.bz2 --contribs=enwiki-contributions.mm --contribution-value=count'.format(sys.argv[0]))
    parser.add_argument('--history-dump', type=argparse.FileType('r'), help='path to input WikiMedia *-pages-meta-history file (.xml/.xml.bz2)', required=True)
    parser.add_argument('--id2author', type=argparse.FileType('w'), help='path to output binary id2author dictionary (.cpickle/.cpickle.bz2)', required=True)
    parser.add_argument('--contribs', type=argparse.FileType('w'), help='path to output MatrixMarket contributions .mm file', required=True)
    parser.add_argument('--contribution-value', choices=CONTRIBUTION_VALUE_CHOICES, help='calculated per-contribution value; choices: {}'.format(CONTRIBUTION_VALUE_CHOICES), required=True)
    
    args = parser.parse_args()
    input_history_dump_path = args.history_dump.name
    output_id2author_path = args.id2author.name
    output_contribs_path = args.contribs.name
    contribution_value = args.contribution_value
    
    program, logger = init_gensim_logger()
    logger.info('running {} with:\n{}'.format(program, pformat({'input_history_dump_path':input_history_dump_path, 'output_id2author_path':output_id2author_path, 'output_contribs_path':output_contribs_path, 'contribution_value':contribution_value})))
    
    with smart_open(input_history_dump_path) as history_dump_file:    
        logger.info('generating author->id mappings')
        history_dump_iter = xml_dump.Iterator.from_file(history_dump_file)
        id2author = create_author2id_dictionary(history_dump_iter)
        id2author.save(output_id2author_path)
        
    with smart_open(input_history_dump_path) as history_dump_file: 
        logger.info('generating MatrixMarket representation per revision: (docid, authorid, value of revision)')
        history_dump_iter = xml_dump.Iterator.from_file(history_dump_file)
        revision_value_fun = CONTRIBUTION_VALUE_FUNCTIONS[contribution_value]
        doc_auth_contribs = create_doc_auth_contributions(history_dump_iter, id2author, revision_value_fun)
        MmCorpus.serialize(output_contribs_path, corpus=doc_auth_contribs, id2word=id2author, progress_cnt=10000)    
    
    
        
if __name__ == '__main__':
    main()
