import json
from mw import xml_dump

files = ["collections/sample_dump.xml"]
#files = ["collections/afwiki-20070124-pages-meta-history.xml.bz2"]
#files = ["collections/afwiki-20070124-pages-meta-history.xml.bz2"]


def process_dump(dump, path):
    for page in dump:
        for revision in page:
            yield revision.contributor.user_text
    
# TODO print durch logging ersetzen? (führt zu Problemen bei Windows mit multiprocessing)
def main():          
    #logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    #logging.info('extracting contributors from {}'.format(files))
    print('extracting contributors from {}'.format(files))
    contributors = xml_dump.map(files, process_dump=process_dump, threads=4)
    contributors = [revision_contributor_name for revision_contributor_name in contributors]
    print('found {} contributions'.format(len(contributors)))
    contributors = list(set(contributors))
    print('found {} contributors'.format(len(contributors)))
    contributors.sort()
    contributors = {contributor_name: id for id,contributor_name in enumerate(contributors)}
    with open('output/contributors.json', 'w') as contributors2ids_file:
        json.dump(contributors, contributors2ids_file)
        
if __name__ == '__main__':
    main()
