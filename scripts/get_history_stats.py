import os, sys
import logging
import argparse
import json
from collections import Counter
from pprint import pformat
from mw import xml_dump
from gensim.utils import smart_open
from utils.utils import init_gensim_logger, number_of_tokens
    
calced_stats = ''' 
number of documents |
number of authors |
number of revisions |
histogram of numbers of revisions of documents |
histogram of numbers of revisions of authors |
histogram of numbers of different authors of documents |
histogram of numbers of different contributed documents of authors
'''
    
    
def main():
    parser = argparse.ArgumentParser(description='calculates and logs: {}'.format(calced_stats), epilog='Example: ./{} --history-dump=enwiki-pages-meta-history.xml.bz2'.format(sys.argv[0]))
    parser.add_argument('--history-dump', type=argparse.FileType('r'), help='path to input WikiMedia *-pages-meta-history file (.xml/.xml.bz2)', required=True)
    
    args = parser.parse_args()
    input_history_dump_path = args.history_dump.name
    
    program, logger = init_gensim_logger()
    logger.info('running {} with:\n{}'.format(program, pformat({'input_history_dump_path':input_history_dump_path})))
            
    numrevs_to_count = Counter()
    numauthors_to_count = Counter()
    author_to_numdocs = Counter()
    author_to_numrevs = Counter()
    with smart_open(input_history_dump_path) as history_dump_file: 
        history_dump = xml_dump.Iterator.from_file(history_dump_file)   
        for document in history_dump:          
            document_revisions = [revision for revision in document]
            numrevs_to_count[len(document_revisions)] += 1
            revisions_authors = [revision.contributor.user_text for revision in document_revisions]
            author_to_numrevs.update(revisions_authors)
            unique_authors = set(revisions_authors)
            author_to_numdocs.update(unique_authors)
            numauthors_to_count[len(unique_authors)] += 1
            
    numdocs = sum(numdocs for numdocs in numrevs_to_count.values())
    numrevs = sum(numdocs*numrevs for (numrevs,numdocs) in numrevs_to_count.items())    
    logger.info('number of documents {}'.format(numdocs))
    logger.info('number of revisions {}'.format(numrevs))    
    
    for numrevs, count in numrevs_to_count.items():
        logger.debug('{} documents have {} revisions'.format(count, numrevs))
        
    for numauthors, count in numauthors_to_count.items():
        logger.debug('{} documents have {} different authors'.format(count, numauthors))
        
    numdocs_of_author_to_count = Counter(author_to_numdocs.values())          
    for numdocs_of_author, count in numdocs_of_author_to_count.items():
        logger.debug('{} authors contributed to {} different documents'.format(count, numdocs_of_author))
        
    numrevs_of_author_to_count = Counter(author_to_numrevs.values())
    for numrevs_of_author, count in numrevs_of_author_to_count.items():
        logger.debug('{} authors created {} revisions'.format(count, numrevs_of_author))
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        
if __name__ == '__main__':
    main()
