import argparse
from pprint import pformat
from scripts.utils.utils import init_logger, load_communities, load_titles, save_data_to_json

logger = init_logger()
             
     
def main():
    parser = argparse.ArgumentParser(description='maps a given partitioning (clustering/communities) file with document labels and a given metadata file with document titles to a doctitle->partitionlabel file')
    parser.add_argument('--partitions', type=argparse.FileType('r'), help='path to input .json.bz2 partitioning file (communities: JSON-dict / clustering: JSON-list)', required=True)
    parser.add_argument('--titles', type=argparse.FileType('r'), help='path to input .json.bz2 titles file', required=True)
    parser.add_argument('--title-partitions', type=argparse.FileType('w'), help='path to output doctitle->partitionlabel .json file', required=True)
    
    args = parser.parse_args()
    input_partititions_path = args.partitions.name
    input_titles_path = args.titles.name
    output_title_partitions_path = args.title_partitions.name
    
    logger.info('running with:\n{}'.format(pformat({'input_partititions_path':input_partititions_path, 'input_titles_path':input_titles_path, 'output_title_partitions_path':output_title_partitions_path})))
    
    # lade Titel, Partitionierung
    titles = load_titles(input_titles_path)
    partitions = load_communities(input_partititions_path)
        
    # erzeuge Titel->Partitionslabel-Mapping
    if isinstance(partitions,dict):
        # bei Graph-Communities ist Partitionierung dict: bestimme Dok-ID aus Graph-Label des Dokumentes (wie z.B. "d123"), bestimme zug. Dok-Titel
        title_partitions = {titles[doc_id[1:]]: comm_label for doc_id,comm_label in partitions.items()}
    else:
        # bei Clustering ist Partitionierung list: betrachte Index jedes Clusterlabels als Dok-ID, bestimme zug. Dok-Titel 
        title_partitions = {titles[str(doc_id)]: comm_label for doc_id,comm_label in enumerate(partitions) if comm_label >= 0}
    logger.info('generated {} title_partitions'.format(len(title_partitions)))
    logger.debug('title_partitions \n{}'.format(title_partitions))
        
    # speichere Titel->Partitionslabel-Mapping
    logger.info('saving title communities')
    save_data_to_json(title_partitions, output_title_partitions_path)
        
        
if __name__ == '__main__':
    main()
