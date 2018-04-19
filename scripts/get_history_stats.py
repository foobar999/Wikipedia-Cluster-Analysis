import os, sys
import logging
import argparse
import csv, json
from collections import Counter
from pprint import pformat
from mw import xml_dump
from gensim.utils import smart_open
from utils.utils import init_logger, write_rows, read_lines
      
logger = init_logger()

    
calced_stats = ''' 
number of documents |
number of authors |
number of revisions 
'''
written_stats = '''
histogram of numbers of revisions of documents -> STAT-FILES-PREFIX-num-revs-per-doc.csv |
histogram of numbers of revisions of authors -> STAT-FILES-PREFIX-num-revs-per-auth.csv | 
histogram of numbers of different authors of documents -> STAT-FILES-PREFIX-num-auth-per-doc.csv |
histogram of numbers of different contributed documents of authors -> STAT-FILES-PREFIX-num-docs-per-auth.csv |
numbers of documents in namespaces (of given file or by number) -> STAT-FILES-PREFIX-num-docs-per-namespace.json
'''
   
   
def get_namespace(page, namespace_prefixes):
    if page.namespace:
        return str(page.namespace)
    for prefix in namespace_prefixes:
        if page.title.startswith(prefix):
            return prefix
    return '0'
   
    
def main():
    parser = argparse.ArgumentParser(description='calculates and logs {}, writes {}'.format(calced_stats,written_stats), epilog='Example: ./{} --history-dump=enwiki-pages-meta-history.xml.bz2'.format(sys.argv[0]))
    parser.add_argument('--history-dump', type=argparse.FileType('r'), help='path to input WikiMedia *-pages-meta-history file (.xml/.xml.bz2)', required=True)
    parser.add_argument('--stat-files-prefix', help='prefix of generated CSV stat files', required=True)
    parser.add_argument("--namespace-prefixes", type=argparse.FileType('r'), help='file of namespace prefixes to ignore')
    
    args = parser.parse_args()
    input_history_dump_path = args.history_dump.name
    output_stat_prefix = args.stat_files_prefix
    namespace_prefixes = read_lines(args.namespace_prefixes.name) if args.namespace_prefixes else ()
    
    logger.info('running with:\n{}'.format(pformat({'input_history_dump_path':input_history_dump_path, 'namespace_prefixes':namespace_prefixes})))
                        
    numrevs_to_count = Counter()
    numauthors_to_count = Counter()
    author_to_numdocs = Counter()
    author_to_numrevs = Counter()
    namespace_to_count = Counter()
    with smart_open(input_history_dump_path) as history_dump_file: 
        history_dump = xml_dump.Iterator.from_file(history_dump_file)   
        for document in history_dump:   
            namespace = get_namespace(document, namespace_prefixes)
            namespace_to_count[namespace] += 1
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
    logger.info('number of namespaces {}'.format(len(namespace_to_count)))
    
    for namespace, count in namespace_to_count.most_common(5):
        logger.debug('{} documents considered namespace {}'.format(count, namespace))
    
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
    with open(output_stat_prefix + '-num-docs-per-namespace.json', 'w') as namespace_to_count_file:
        namespace_to_count = dict(sorted(namespace_to_count.items()))
        json.dump(namespace_to_count, namespace_to_count_file, indent=1)
    logger.info('wrote files')
    
    
        
if __name__ == '__main__':
    main()
