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
    parser = argparse.ArgumentParser(description='extracts contributors from given wikimedia dumps and creates a contributor->id mapping JSON file', epilog='Example: ./{} collections/afwiki-20070124-pages-meta-history.xml.bz2 res.json'.format(sys.argv[0]))
    parser.add_argument("input_dump_files", nargs='+', type=argparse.FileType('r'), help='paths to wikimedia history dumps (.xml or .xml.bz2)')
    parser.add_argument("output_mappings_file", type=argparse.FileType('w'), help='path to resulting contributor->id mappings file')
    args = parser.parse_args()
    input_dump_files = [file.name for file in args.input_dump_files]
    output_mappings_file = args.output_mappings_file.name
    
    contributors = create_mappings(input_dump_files)
    
    with open(output_mappings_file, 'w', newline='') as contributors2ids_file:
        csv_writer = csv.writer(contributors2ids_file, delimiter=' ')
        csv_writer.writerows(enumerate(contributors))
        
        
if __name__ == '__main__':
    main()
