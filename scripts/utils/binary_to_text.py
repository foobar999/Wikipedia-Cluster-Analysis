import argparse
import pickle
from gensim.utils import smart_open
from scripts.utils.utils import init_logger, save_data_to_json

logger = init_logger()


def main():
    parser = argparse.ArgumentParser(description='creates from a binary gensim document metadata file a JSON docid->doctitle mapping file')
    parser.add_argument('--metadata', type=argparse.FileType('r'), help='path to input document metadata file (.metadata.cpickle)', required=True)
    parser.add_argument('--titles', type=argparse.FileType('w'), help='path to output docid->doctitle mapping file (.json)', required=True)

    args = parser.parse_args()
    input_metadata_path = args.metadata.name
    output_titles_path = args.titles.name
    
    logger.info('loading metadata from {}'.format(input_metadata_path))
    with smart_open(input_metadata_path, "rb") as input_metadata_file:
        metadata = pickle.load(input_metadata_file)
    titles = metadata
    logger.info('saving metadata titles')
    save_data_to_json(titles, output_titles_path)
    
    
if __name__ == '__main__':
    main()
    
    
    
    