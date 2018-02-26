import csv
import argparse
import sys
from mw import xml_dump


def process_dump(dump, path):
    for page in dump:
        for revision in page:
            yield revision.contributor.user_text
            
            
def create_mappings(input_dump_files):
    print('extracting contributors from {}'.format(input_dump_files))   # TODO für direkte Ausgabe sorgen
    contributors = xml_dump.map(input_dump_files, process_dump=process_dump, threads=4)
    contributors = [revision_contributor_name for revision_contributor_name in contributors]
    print('found {} contributions'.format(len(contributors)))
    contributors = list(set(contributors))  # entferne Dubletten
    print('found {} contributors'.format(len(contributors)))
    contributors.sort()
    return contributors

    
# TODO print durch logging ersetzen? (führt zu Problemen bei Windows mit multiprocessing)
def main():  
    parser = argparse.ArgumentParser(description='extracts contributors from at least one wikimedia dump and creates an id->contributor mapping CSV file', epilog='Example: ./{} afwiki-20070124-pages-meta-history.xml.bz2 id2contributor.csv'.format(sys.argv[0]))
    parser.add_argument("idump", nargs='+', type=argparse.FileType('r'), help='path to wikimedia history dump (.xml or .xml.bz2)')
    parser.add_argument("oid2con", type=argparse.FileType('w'), help='path to resulting id->contributor mappings CSV file')
    args = parser.parse_args()
    input_dump_files = [file.name for file in args.idump]
    output_mappings_file = args.oid2con.name
    
    contributors = create_mappings(input_dump_files)
    
    with open(output_mappings_file, 'w', newline='', encoding='utf-8') as id2contributor_file:
        csv_writer = csv.writer(id2contributor_file, delimiter=' ')
        csv_writer.writerows(enumerate(contributors))   # schreibe Einträge der Form [(0,CONTRIBUTOR_1),(1,CONTRIBUTOR_2),...]
        
        
if __name__ == '__main__':
    main()
