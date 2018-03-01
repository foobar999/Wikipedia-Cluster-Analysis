import argparse
import sys
import os
import json
from hashlib import sha1
from mwcli import files


def add_sha1_to_revdoc(input_revdoc_path, output_revdoc_path, compress):
    ifile = files.functions.reader(input_revdoc_path)
    revdocs = (json.loads(line) for line in ifile) # TODO ist das speichermäßig ok?
    writer = files.writer(output_revdoc_path)
    for revdoc in revdocs:
        #if 'text' in revdoc:    # TODO ????
        text_to_hash = revdoc['text'] if 'text' in revdoc else ''
        revdoc['sha1'] = sha1(bytes(text_to_hash, 'utf8')).hexdigest()
        json.dump(revdoc, writer)
        writer.write("\n")
    print('wrote {}'.format(output_revdoc_path))


def add_sha1_to_revdocs(input_revdoc_paths, output_sha1_revdoc_dir, compress):
    output_sha1_revdoc_dir = files.normalize_dir(output_sha1_revdoc_dir)
    for input_revdoc_path in input_revdoc_paths:
        output_revdoc_path = files.output_dir_path(input_revdoc_path, output_sha1_revdoc_dir, compress)
        add_sha1_to_revdoc(input_revdoc_path, output_revdoc_path, compress)
        

def main():
    parser = argparse.ArgumentParser(description='adds to at least one JSON wikimedia revision history dump sha1-entries to given revisions', epilog='Example: ./{} afwiki-20070124-pages-meta-history.json.bz2 afwiki-20070124-revdocs-sha1'.format(sys.argv[0]))
    parser.add_argument("irevdocs", nargs='+', type=argparse.FileType('r'), help='path to input JSON revision dump')
    parser.add_argument('--compress', choices=['bz2', 'json', 'xml', 'gz'], default='bz2')
    parser.add_argument("output", help='path to output directory of revision dumps with sha1-values')
    args = parser.parse_args()
    input_revdoc_paths = [path.name for path in args.irevdocs]
    output_sha1_revdoc_dir = args.output
    compress = args.compress
    print('adding sha1-values to revisions')
    print('from paths {}'.format(input_revdoc_paths))
    print('to directory {}'.format(output_sha1_revdoc_dir))
    print('compressing with {}'.format(compress))
    add_sha1_to_revdocs(input_revdoc_paths, output_sha1_revdoc_dir, compress)
    
if __name__ == '__main__':
    main()