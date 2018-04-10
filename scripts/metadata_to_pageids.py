import os, sys
import logging
import argparse
from pprint import pformat
from gensim.utils import pickle, unpickle
from utils.utils import init_gensim_logger

# TODO pageid als zahl ok? ist jedenfalls effizienter
# TODO testen, ob pageids ok, oder ob titles nötig
# TODO bei sehr viel dokumenten? doch lieber ne Textdatei?
    
def main():
    parser = argparse.ArgumentParser(description='convertes a given .metadata.cpickle file (such as generated by gensim MmCorpus.serialize(..., metadata=True) to a pickled frozenset of contained pageids', epilog='Example: ./{} --metadata=enwiki-metadata.cpickle.bz2 --pageids=enwiki-pageids.cpickle.bz2'.format(sys.argv[0]))
    parser.add_argument('--metadata', type=argparse.FileType('r'), help='path to input binary metadata file (.cpickle/.cpickle.bz2)', required=True)
    parser.add_argument('--pageids', type=argparse.FileType('w'), help='path to output binary frozenset of pageids file (.cpickle/.cpickle.bz2)', required=True)
    
    args = parser.parse_args()
    input_metadata_path = args.metadata.name
    output_pageids_path = args.pageids.name
    
    program, logger = init_gensim_logger()
    logger.info('running {} with:\n{}'.format(program, pformat({'input_metadata_path':input_metadata_path, 'output_pageids_path':output_pageids_path})))

    metadata = unpickle(input_metadata_path)
    logger.debug('unpickled {}'.format(metadata))
    pageids = frozenset(int(md[0]) for md in metadata.values())
    logger.debug('created set {}'.format(pageids))
    pickle(pageids, output_pageids_path)
    
        
if __name__ == '__main__':
    main()
