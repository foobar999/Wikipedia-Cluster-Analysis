import os, sys
import logging
import argparse
from pprint import pformat
from collections import defaultdict
from gensim.corpora import MmCorpus
from gensim.matutils import MmWriter
from utils.utils import init_logger

logger = init_logger()


def accumulate(raw_doc_contribs):
    accumulator = defaultdict(lambda: 0)
    for author_id, value in raw_doc_contribs:
        accumulator[author_id] += value
    return ((author_id,accumulator[author_id]) for author_id in accumulator)

    
def main():
    parser = argparse.ArgumentParser(description='accumulates values of same (document,author)-Pairs', epilog='Example: ./{} --raw-contribs=enwiki-raw-contribs.mm --acc-contribs=enwiki-acc-contribs.mm'.format(sys.argv[0]))
    parser.add_argument('--raw-contribs', type=argparse.FileType('r'), help='path to input MatrixMarket raw contributions file (.mm/.mm.bz2)', required=True)
    parser.add_argument('--acc-contribs', type=argparse.FileType('w'), help='path to output MatrixMarket accumulated contributions .mm file', required=True)
    
    args = parser.parse_args()
    input_raw_contribs_dump_path = args.raw_contribs.name
    output_acc_contribs_dump_path = args.acc_contribs.name
    
    logger.info('running with:\n{}'.format(pformat({'input_raw_contribs_dump_path':input_raw_contribs_dump_path, 'output_acc_contribs_dump_path':output_acc_contribs_dump_path})))

    raw_contribs = MmCorpus(input_raw_contribs_dump_path)
    acc_contribs = (accumulate(raw_doc_contribs) for raw_doc_contribs in raw_contribs)
    #MmCorpus.serialize(output_acc_contribs_dump_path, corpus=acc_contribs, progress_cnt=10000)  
    MmWriter.write_corpus(output_acc_contribs_dump_path, corpus=acc_contribs, index=False, progress_cnt=10000, metadata=False)   
    
        
if __name__ == '__main__':
    main()
