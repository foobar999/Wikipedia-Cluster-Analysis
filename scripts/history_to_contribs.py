import os, sys
import logging
import argparse
from pprint import pformat
from mw import xml_dump
from gensim.utils import smart_open
from gensim.corpora import Dictionary, MmCorpus
from utils.utils import init_gensim_logger, number_of_tokens

# TODO gegen frozenste von PageIDs prüfen
# TODO gegen redirect,namespace o.Ä. prüfen
    
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
    
    
    
CONTRIBUTION_VALUE_FUNCTIONS = {
    'one': contrib_value_one,
    'numterms': contrib_value_numterms,
    'diff_numterms': contrib_value_diff_numterms
}
    
def inspect_page(page):
    return True
    
def main():
    parser = argparse.ArgumentParser(description='creates an document->author contributions MatrixMarket file from a given WikiMedia *-pages-meta-history dump and a calculated id2author mapping', epilog='Example: ./{} --history-dump=enwiki-pages-meta-history.xml.bz2 --id2author=enwiki-id2author.cpickle.bz2 --contribs=enwiki-contributions.mm --contribution-value=count'.format(sys.argv[0]))
    parser.add_argument('--history-dump', type=argparse.FileType('r'), help='path to input WikiMedia *-pages-meta-history file (.xml/.xml.bz2)', required=True)
    parser.add_argument('--id2author', type=argparse.FileType('r'), help='path to input binary id2author dictionary (.cpickle/.cpickle.bz2)', required=True)
    parser.add_argument('--contribs', type=argparse.FileType('w'), help='path to output MatrixMarket contributions .mm file', required=True)
    parser.add_argument('--contribution-value', choices=CONTRIBUTION_VALUE_CHOICES, help='calculated per-contribution value; choices: {}'.format(CONTRIBUTION_VALUE_CHOICES), required=True)
    
    args = parser.parse_args()
    input_history_dump_path = args.history_dump.name
    input_id2author_path = args.id2author.name
    output_contribs_path = args.contribs.name
    contribution_value = args.contribution_value
    
    program, logger = init_gensim_logger()
    logger.info('running {} with:\n{}'.format(program, pformat({'input_history_dump_path':input_history_dump_path, 'input_id2author_path':input_id2author_path, 'output_contribs_path':output_contribs_path, 'contribution_value':contribution_value})))

    id2author = Dictionary.load(input_id2author_path)
    
    dump = xml_dump.Iterator.from_file(smart_open(input_history_dump_path))
    revision_value_fun = CONTRIBUTION_VALUE_FUNCTIONS[contribution_value]
    contrib_iter = (revision_value_fun(((id2author.token2id[rev.contributor.user_text], rev) for rev in page)) for page in dump)
    # TODO kann man hier was mit dictionary.doc2idx machen??
    MmCorpus.serialize(output_contribs_path, corpus=contrib_iter, id2word=id2author, progress_cnt=10000)    
    
    #for page in contrib_iter:
    #    for author in page:
    #        logger.info(author)
    #    logger.info(page)
    
    
    """
    print('reading {}'.format(files))
    dump_entries = xml_dump.map(files, process_dump=process_dump, threads=4)
    page_ids_titles = [(page_id,page_title) for page_id,page_title in dump_entries]
    print('found {} page ids & titles'.format(len(page_ids_titles)))
    #entries = list(set(contributors))
    #print('found {} contributors'.format(len(contributors)))
    #contributors.sort()
    #contributors = {contributor_name: id for id,contributor_name in enumerate(contributors)}
    with open('page_ids_titles.json', 'w') as page_ids_titles_file:
        json.dump(page_ids_titles, page_ids_titles_file, indent=0)
    """

"""
def process_dump(dump, path):
    for page in dump:
        yield page.id, page.title
"""
        
if __name__ == '__main__':
    main()
