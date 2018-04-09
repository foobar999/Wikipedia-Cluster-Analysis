import os, sys
import logging
import argparse
from pprint import pformat
from mw import xml_dump
from gensim.utils import smart_open
from gensim.corpora import Dictionary
from utils.utils import init_gensim_logger

# TODO gegen frozenste von PageIDs prüfen
# TODO gegen redirect,namespace o.Ä. prüfen
    
def inspect_page(page):
    return True
    
def main():
    parser = argparse.ArgumentParser(description='creates an id2author gensim dictionary mapping file which maps internal author ids to author names', epilog='Example: ./{} --history-dump=enwiki-pages-meta-history.xml.bz2 --id2author=enwiki-id2author.cpickle -'.format(sys.argv[0]))
    parser.add_argument('--history-dump', type=argparse.FileType('r'), help='path to input WikiMedia *-pages-meta-history file (.xml/.xml.bz2)', required=True)
    parser.add_argument('--id2author', type=argparse.FileType('w'), help='path to output binary id2author dictionary file (.cpickle/.cpickle.bz2)', required=True)
    
    args = parser.parse_args()
    input_history_dump_path = args.history_dump.name
    output_id2author_path = args.id2author.name
    
    program, logger = init_gensim_logger()
    logger.info('running {} with:\n{}'.format(program, pformat({'input_history_dump_path':input_history_dump_path, 'output_id2author_path':output_id2author_path})))

    dump = xml_dump.Iterator.from_file(smart_open(input_history_dump_path))
    author_iter = ((revision.contributor.user_text for revision in page) for page in dump)
    id2author = Dictionary(author_iter)
    id2author.save(output_id2author_path)
    logging.info('number of processed documents: {}'.format(id2author.num_docs))
    logging.info('number of found authors: {}'.format(len(id2author.token2id)))
        
if __name__ == '__main__':
    main()
