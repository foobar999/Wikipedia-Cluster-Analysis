import os, sys
import argparse
import logging
from gensim.utils import SaveLoad

def main():
    parser = argparse.ArgumentParser(description='serializes the dictionary of a given binary .pkl or .pkl.bz2 bag-of-words file to a text-based id2word .txt file', epilog='Example: ./{} mycorpus-bow.pkl.bz2 mycorpus-dict.txt'.format(sys.argv[0]))
    parser.add_argument('model_pkl', type=argparse.FileType('r'), help='path to input .pkl or .pkl.bz2 bag-of-words model file ')
    parser.add_argument('id2word', type=argparse.FileType('w'), help='path to output .txt id2word file')
    args = parser.parse_args()
    input_model_pkl_path = args.model_pkl.name
    output_id2word_path = args.id2word.name
    
    program = os.path.basename(sys.argv[0])
    logger = logging.getLogger(program)
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')    
    logging.root.level = logging.INFO
    logger.info('serializing id2word-mapping of {} to {}'.format(input_model_pkl_path, output_id2word_path))
    model = SaveLoad.load(input_model_pkl_path)
    model.dictionary.save_as_text(output_id2word_path)
    
if __name__ == '__main__':
    main()