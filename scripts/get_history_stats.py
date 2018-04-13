import os, sys
import logging
import argparse
import csv
from collections import Counter
from pprint import pformat
from mw import xml_dump
from gensim.utils import smart_open
from utils.utils import init_gensim_logger
    
def write_rows(csv_filename, rows):
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=' ')
        csv_writer.writerows(rows)  
        
def read_rows(csv_filename):   
    with open(csv_filename, 'r', newline='', encoding='utf-8') as csv_file:
        csvreader = csv.reader(csv_file, delimiter=' ')
        return [row for row in csvreader]
    
    
calced_stats = ''' 
number of documents |
number of authors |
number of revisions 
'''
written_stats = '''
histogram of numbers of revisions of documents -> STAT-FILES-PREFIX-num-revs-per-doc.csv |
histogram of numbers of revisions of authors -> STAT-FILES-PREFIX-num-revs-per-auth.csv | 
histogram of numbers of different authors of documents -> STAT-FILES-PREFIX-PREFIX-num-auth-per-doc.csv |
histogram of numbers of different contributed documents of authors -> STAT-FILES-PREFIX-num-docs-per-auth.csv
'''
    
    
def main():
    parser = argparse.ArgumentParser(description='calculates and logs {}, writes {}'.format(calced_stats,written_stats), epilog='Example: ./{} --history-dump=enwiki-pages-meta-history.xml.bz2'.format(sys.argv[0]))
    parser.add_argument('--history-dump', type=argparse.FileType('r'), help='path to input WikiMedia *-pages-meta-history file (.xml/.xml.bz2)', required=True)
    parser.add_argument('--stat-files-prefix', help='prefix of generated CSV stat files', required=True)
    
    args = parser.parse_args()
    input_history_dump_path = args.history_dump.name
    output_stat_prefix = args.stat_files_prefix
    
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
    numauthors = len(author_to_numdocs)
    logger.info('number of documents {}'.format(numdocs))
    logger.info('number of revisions {}'.format(numrevs))    
    logger.info('number of authors {}'.format(numauthors))
    
    for numrevs, count in numrevs_to_count.most_common(5):
        logger.debug('{} documents have {} revisions'.format(count, numrevs))
        
    for numauthors, count in numauthors_to_count.most_common(5):
        logger.debug('{} documents have {} different authors'.format(count, numauthors))
        
    numdocs_of_author_to_count = Counter(author_to_numdocs.values())          
    for numdocs_of_author, count in numdocs_of_author_to_count.most_common(5):
        logger.debug('{} authors contributed to {} different documents'.format(count, numdocs_of_author))
        
    numrevs_of_author_to_count = Counter(author_to_numrevs.values())
    for numrevs_of_author, count in numrevs_of_author_to_count.most_common(5):
        logger.debug('{} authors created {} revisions'.format(count, numrevs_of_author))
    
    write_rows(output_stat_prefix + '-num-revs-per-doc.csv', sorted(numrevs_to_count.items()))
    write_rows(output_stat_prefix + '-num-revs-per-auth.csv', sorted(numrevs_of_author_to_count.items()))
    write_rows(output_stat_prefix + '-num-auth-per-doc.csv', sorted(numauthors_to_count.items()))
    write_rows(output_stat_prefix + '-num-docs-per-auth.csv', sorted(numdocs_of_author_to_count.items()))
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        
if __name__ == '__main__':
    main()
