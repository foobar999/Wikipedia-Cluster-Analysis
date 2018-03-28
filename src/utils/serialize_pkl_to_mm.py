import os, sys
import argparse
import logging
from gensim.utils import SaveLoad
from gensim.corpora import MmCorpus

def main():
    parser = argparse.ArgumentParser(description='serializes given binary .pkl or .pkl.bz2 file to text-based .mm model file in MatrixMarket format (requires that collection data used for creation of the .pkl file is still available!)', epilog='Example: ./{} bowmodel.pkl.bz2 bowmodel.mm'.format(sys.argv[0]))
    parser.add_argument('model_pkl', type=argparse.FileType('r'), help='path to input .pkl or .pkl.bz2 model file (bag-of-words, tf-idf)')
    parser.add_argument('model_mm', type=argparse.FileType('w'), help='path to output .mm model file')
    args = parser.parse_args()
    input_model_pkl_path = args.model_pkl.name
    output_model_mm_path = args.model_mm.name
    
    program = os.path.basename(sys.argv[0])
    logger = logging.getLogger(program)
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')    
    logging.root.level = logging.INFO
    logger.info('serializing {} to {}'.format(input_model_pkl_path, output_model_mm_path))
    model = SaveLoad.load(input_model_pkl_path)
    MmCorpus.serialize(output_model_mm_path, model)
    
if __name__ == '__main__':
    main()