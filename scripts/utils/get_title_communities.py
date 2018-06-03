import os, sys
import logging
import argparse
import json
import bz2
from pprint import pformat
from scripts.utils.utils import init_logger

logger = init_logger()
             
     
def main():
    parser = argparse.ArgumentParser(description='maps a given communities file with document labels and a give binary titles file with document titles to a doctitle->communitylabel file')
    parser.add_argument('--communities', type=argparse.FileType('r'), help='path to input .json.bz2 communities file', required=True)
    parser.add_argument('--titles', type=argparse.FileType('r'), help='path to input .json.bz2 titles file', required=True)
    parser.add_argument('--titlecomms', type=argparse.FileType('w'), help='path to output doctitle->communitylabel .json file', required=True)
    
    args = parser.parse_args()
    input_communities_path = args.communities.name
    input_titles_path = args.titles.name
    output_titlecomms_path = args.titlecomms.name
    
    logger.info('running with:\n{}'.format(pformat({'input_communities_path':input_communities_path, 'input_titles_path':input_titles_path, 'output_titlecomms_path':output_titlecomms_path})))
    
    with bz2.open(input_titles_path, 'rt') as input_titles_file:
        titles = json.load(input_titles_file)
    with bz2.open(input_communities_path, 'rt') as input_communities_file:
        communities = json.load(input_communities_file)
        
    logger.info('{} titles'.format(len(titles)))
    logger.debug('titles \n{}'.format(titles))
    logger.info('{} communities'.format(len(communities)))
    logger.debug('communities \n{}'.format(communities))
        
    if isinstance(communities,dict):
        title_communities = {titles[doc_id[1:]]: comm_label for doc_id,comm_label in communities.items()}
    else:
        title_communities = {titles[str(doc_id)]: comm_label for doc_id,comm_label in enumerate(communities) if comm_label >= 0}
    logger.info('generated {} title_communities and removed noise'.format(len(title_communities)))
    logger.debug('title_communities \n{}'.format(title_communities))
        
    logger.info('saving to {}'.format(output_titlecomms_path))
    with open(output_titlecomms_path, 'w') as output_titlecomms_file:
        json.dump(title_communities, output_titlecomms_file, indent=1)
        
        
if __name__ == '__main__':
    main()
