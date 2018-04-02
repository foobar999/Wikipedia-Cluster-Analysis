import os, sys
import argparse
from gensim.utils import SaveLoad
import pickle, json


def main():
    parser = argparse.ArgumentParser(description='creates from a given pickled dict .cpickle file a text-based JSON representation file (useful for debugging purposes)', epilog='Example: ./{} corpus.metadata.cpickle corpus.metadata.json'.format(sys.argv[0]))
    parser.add_argument('pickle', type=argparse.FileType('r'), help='path to input pickled object binary .cpickle file')
    parser.add_argument('text', type=argparse.FileType('w'), help='path to output JSON object representation file')

    args = parser.parse_args()
    input_pickle_path = args.pickle.name
    output_text_path = args.text.name
    
    with open(input_pickle_path, "rb") as ifile:
        obj = pickle.load(ifile)
    with open(output_text_path, "w") as ofile:
        json.dump(obj, ofile, indent=4)
    
    
if __name__ == '__main__':
    main()
    
