import os, sys
import argparse
from gensim.utils import SaveLoad
import pickle


def main():
    parser = argparse.ArgumentParser(description='creates from a given pickled gensim dictionary .cpickle file a text-based representation file (useful for debugging purposes)', epilog='Example: ./{} corpus.id2word.cpickle corpus.id2word.txt'.format(sys.argv[0]))
    parser.add_argument('pickle', type=argparse.FileType('r'), help='path to input pickled object binary .cpickle file')
    parser.add_argument('text', type=argparse.FileType('w'), help='path to output text-based object representation file')

    args = parser.parse_args()
    input_pickle_path = args.pickle.name
    output_text_path = args.text.name
    
    obj = SaveLoad.load(input_pickle_path)
    obj.save_as_text(output_text_path)
    
    
    
if __name__ == '__main__':
    main()
    
