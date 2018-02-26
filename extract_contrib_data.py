# -*- coding: utf-8 -*-
import csv
import argparse
import sys
import codecs
from mw import xml_dump
from src import csv_io

def process_dump(dump, path):
    for page in dump:
        for revision in page:
            yield page.id, revision.contributor.user_text, revision            
        
# erzeugt einen Contribution-Eintrag (Artikel-ID, Contributor-ID, Anzahl Zeichen, Anzahl Wörter)
# TODO Format-Zeugs von MediaWiki entfernen
# TODO die Revisionen beinhalten keine Diffs -> Diffs berechnen
def create_row(page_id, contributor_id, revision):
    return (page_id, contributor_id, len(revision.text), len(revision.text.split()))

    
def extract_contrib_data(contributor2id, input_dump_files):
    print('extracting contribution data from {}'.format(input_dump_files))
    contribution_data = xml_dump.map(input_dump_files, process_dump=process_dump, threads=4)
    contributions = [create_row(page_id,contributor2id[contributor],revision) for page_id,contributor,revision in contribution_data]
    print('found {} contributions'.format(len(contributions)))
    return contributions
    
    
def main():  
    parser = argparse.ArgumentParser(description='creates a CSV file with one entry (contributor_id,doc_id,num_contrib_words,num_contrib_bytes) per contribution; needs an id->contributor mapping file (result of "id2contributor.py") and at least one wikipedia dump', epilog='Example: ./{} id2contrib.csv afwiki-20070124-pages-meta-history.xml.bz2 contrib_data.csv'.format(sys.argv[0]))
    parser.add_argument("iid2con", type=argparse.FileType('r'), help='path to input id2contrib CSV file')
    parser.add_argument("idump", nargs='+', type=argparse.FileType('r'), help='path to input wikimedia history dump (.xml or .xml.bz2)')
    parser.add_argument("ocontribs", type=argparse.FileType('w'), help='path to output contribution data csv file')
    args = parser.parse_args()
    input_id2contributor_file = args.iid2con.name
    input_dump_files = [file.name for file in args.idump]
    output_contribution_file = args.ocontribs.name
    print('extracting data')
    print('from dumps {}'.format(input_dump_files))
    print('with id2contributor mappings from {}'.format(input_id2contributor_file))
    print('to output file {}'.format(output_contribution_file))
    contributor2id = {row[1]:row[0] for row in csv_io.read_rows(input_id2contributor_file)}
    print('read {} id->contributor mappings'.format(len(contributor2id)))
    contributions = extract_contrib_data(contributor2id, input_dump_files)
    csv_io.write_rows(output_contribution_file, contributions)
        
        
if __name__ == '__main__':
    main()
