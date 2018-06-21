import argparse
import numpy as np
#from sklearn.metrics import normalized_mutual_info_score
# sklearn's mi-scores benutzen ln statt log2 -> nimm eigene log2-Variante
# merkwürdig: es scheint bei nmi bei ln und log2 das gleiche rauszukommen
from scripts.external.supervised import normalized_mutual_info_score 
from scripts.utils.utils import init_logger, load_communities

logger = init_logger()
             

def main():
    parser = argparse.ArgumentParser(description='compares two clusterings/community structures by computing the normalized mutual information score of both documenttitle->clusterlabel mappings (comparison bases of intersection based on equal documenttitles)')
    parser.add_argument('--clusterings', nargs=2, type=argparse.FileType('r'), metavar=('CLUS1','CLUS2'), help='path to two titleclsuterings files (.json/.json.bz2)', required=True)
    
    args = parser.parse_args()
    input_clusterings_paths = (args.clusterings[0].name, args.clusterings[1].name)
    
    clustering1 = load_communities(input_clusterings_paths[0])
    clustering2 = load_communities(input_clusterings_paths[1])
    
    logger.info('intersecting clusterings by document titles')
    intersect_titles = sorted(clustering1.keys() & clustering2.keys())
    logger.debug('intersect titles \n{}'.format(intersect_titles))
    logger.info('number of intersect titles {}'.format(len(intersect_titles)))
    
    intsect_labels1 = [clustering1[title] for title in intersect_titles]
    logger.debug('labels of intersect titles in clustering 1 \n{}'.format(intsect_labels1))
    intsect_labels2 = [clustering2[title] for title in intersect_titles]
    logger.debug('labels of intersect titles in clustering 2 \n{}'.format(intsect_labels2))
    
    intsect_labels1 = np.array(intsect_labels1)
    intsect_labels2 = np.array(intsect_labels2)
    
    score = normalized_mutual_info_score(intsect_labels1, intsect_labels2)
    logger.info('normalized-mutual-info: {}'.format(score))
        
        
        
if __name__ == '__main__':
    main()
