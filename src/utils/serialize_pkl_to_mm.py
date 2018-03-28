import os, sys
import argparse
import logging
from gensim.utils import SaveLoad
from gensim.corpora import MmCorpus
from gensim.models import TfidfModel

def main():
    parser = argparse.ArgumentParser(description='serializes given binary .pkl or .pkl.bz2 file to text-based .mm model file in MatrixMarket format (optional: also serializes id2words dictionary in give binary file to .txt dictionary file) (requires that collection data used for creation of the .pkl file is still available!)', epilog='Example: ./{} bowmodel.pkl.bz2 bowmodel.mm --id2word bowmodel_dict.txt'.format(sys.argv[0]))
    parser.add_argument('model_pkl', type=argparse.FileType('r'), help='path to input .pkl or .pkl.bz2 model file (bag-of-words, tf-idf)')
    parser.add_argument('model_mm', type=argparse.FileType('w'), help='path to output .mm model file')
    parser.add_argument('--id2word', type=argparse.FileType('w'), help='optional path to output .txt dictionary file')
    args = parser.parse_args()
    input_model_pkl_path = args.model_pkl.name
    output_model_mm_path = args.model_mm.name
    output_id2word_path = args.id2word.name if args.id2word else None
    
    program = os.path.basename(sys.argv[0])
    logger = logging.getLogger(program)
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')    
    logging.root.level = logging.INFO
    logger.info('serializing {} to {}'.format(input_model_pkl_path, output_model_mm_path))
    model = SaveLoad.load(input_model_pkl_path)
    MmCorpus.serialize(output_model_mm_path, model)
    #if output_id2word_path:
    #    logger.info('serializing dictionary of given model to {}'.format(output_id2word_path))
    #    model.dictionary.save_as_text(output_id2word_path)
    
if __name__ == '__main__':
    main()