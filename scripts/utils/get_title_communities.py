import argparse
from pprint import pformat
from scripts.utils.utils import init_logger, load_communities, load_titles, save_data_to_json

logger = init_logger()
             
     
def main():
    parser = argparse.ArgumentParser(description='maps a given communities/clustering file with document labels and a given metadata file with document titles to a doctitle->communitylabel file')
    parser.add_argument('--communities', type=argparse.FileType('r'), help='path to input .json.bz2 communities file', required=True)
    parser.add_argument('--titles', type=argparse.FileType('r'), help='path to input .json.bz2 titles file', required=True)
    parser.add_argument('--titlecomms', type=argparse.FileType('w'), help='path to output doctitle->communitylabel .json file', required=True)
    
    args = parser.parse_args()
    input_communities_path = args.communities.name
    input_titles_path = args.titles.name
    output_titlecomms_path = args.titlecomms.name
    
    logger.info('running with:\n{}'.format(pformat({'input_communities_path':input_communities_path, 'input_titles_path':input_titles_path, 'output_titlecomms_path':output_titlecomms_path})))
    
    # lade Titel, Partitionierung
    titles = load_titles(input_titles_path)
    communities = load_communities(input_communities_path)
        
    # erzeuge Titel->Partitionslabel-Mapping
    if isinstance(communities,dict):
        # bei Graph-Communities ist Partitionierung dict: bestimme Dok-ID aus Graph-Label des Dokumentes (wie z.B. "d123"), bestimme zug. Dok-Titel
        title_communities = {titles[doc_id[1:]]: comm_label for doc_id,comm_label in communities.items()}
    else:
        # bei Clustering ist Partitionierung list: betrachte Index jedes Clusterlabels als Dok-ID, bestimme zug. Dok-Titel 
        title_communities = {titles[str(doc_id)]: comm_label for doc_id,comm_label in enumerate(communities) if comm_label >= 0}
    logger.info('generated {} title_communities'.format(len(title_communities)))
    logger.debug('title_communities \n{}'.format(title_communities))
        
    # speichere Titel->Partitionslabel-Mapping
    logger.info('saving title communities')
    save_data_to_json(title_communities, output_titlecomms_path)
        
        
if __name__ == '__main__':
    main()
