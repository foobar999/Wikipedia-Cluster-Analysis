import argparse
from pprint import pformat
import numpy as np
from scipy.spatial.distance import cdist
from scripts.utils.utils import init_logger, load_titles, save_data_to_json
from scripts.utils.documents import load_document_topics, load_cluster_labels

logger = init_logger()


def get_clusters_from_labels(cluster_labels):
    num_clusters = len(np.unique(cluster_labels))
    logger.info('number of clusters {}'.format(num_clusters))
    clusters = [[] for _ in range(num_clusters)]
    for docid,label in enumerate(cluster_labels):
        clusters[label].append(docid)
    logger.debug('clusters \n{}'.format(clusters))
    return clusters
            
            
def get_top_central_cluster_docs(cluster, document_topics, max_docs_per_clus, metric):
    logger.info('cluster of size {}: finding {} nearest docs to centroid with metric {}'.format(len(cluster), max_docs_per_clus, metric))
    cluster_documents = document_topics[cluster]
    logger.debug('submatrix shape {}'.format(cluster_documents.shape))
    cluster_centroid = np.mean(cluster_documents, axis=0)
    cluster_centroid = cluster_centroid.reshape((1,len(cluster_centroid)))
    logger.debug('cluster centroid shape {}'.format(cluster_centroid.shape))
    document_centroid_dists = cdist(cluster_documents, cluster_centroid, metric=metric).flatten()
    logger.debug('nearest index {}'.format(np.argmin(document_centroid_dists)))
    logger.debug('document_centroid_dists shape {}'.format(document_centroid_dists.shape))
    central_doc_indices = np.argsort(document_centroid_dists)[:max_docs_per_clus].tolist() # funktioniert auch, wenn Cluster kleiner als max_docs_per_clus
    logger.debug('central_doc_indices {}'.format(central_doc_indices))
    central_docids = [cluster[i] for i in central_doc_indices]
    centralities = [document_centroid_dists[i] for i in central_doc_indices]
    logger.debug('central doc ids {}'.format(central_docids))
    return central_docids, centralities
     
     
def get_document_titles(docids, document_titles):
    return [document_titles[str(docid)] for docid in docids]
    
     
def main():
    parser = argparse.ArgumentParser(description='creates a file of clusterings: clusters are sorted descending by size, cluster elements are sorted by distance to cluster centroid')    
    parser.add_argument('--document-topics', type=argparse.FileType('r'), help='path to input document-topic-file (.npz)', required=True)
    parser.add_argument('--cluster-labels', type=argparse.FileType('r'), help='path to input .json.bz2 clustering file', required=True)
    parser.add_argument('--titles', type=argparse.FileType('r'), help='path to input .json.bz2 titles file', required=True)  
    parser.add_argument('--centrality-data', type=argparse.FileType('w'), help='path to output .json cluster->centrality_data file', required=True)
    parser.add_argument('--max-docs-per-clus', type=int, help='maxiumum number of highest considered nodes per cluster', required=True)
    parser.add_argument('--metric', help='calced dissimilarity to centroids (muse be allowd by cdist of scipy)', required=True)
    
    args = parser.parse_args()
    input_document_topics_path = args.document_topics.name
    input_cluster_labels_path = args.cluster_labels.name
    input_titles_path = args.titles.name
    output_centrality_data_path = args.centrality_data.name
    max_docs_per_clus = args.max_docs_per_clus
    metric = args.metric
    
    logger.info('running with:\n{}'.format(pformat({'input_document_topics_path':input_document_topics_path, 'input_cluster_labels_path':input_cluster_labels_path, 'input_titles_path':input_titles_path, 'output_centrality_data_path':output_centrality_data_path, 'max_docs_per_clus':max_docs_per_clus, 'metric':metric})))
        
    document_topics = load_document_topics(input_document_topics_path)
    cluster_labels = load_cluster_labels(input_cluster_labels_path)
    document_titles = load_titles(input_titles_path)
        
    clusters = get_clusters_from_labels(cluster_labels)    
    logger.info('computing {}-centralities of {} documents in {} communities'.format(metric, len(cluster_labels), len(clusters)))
    centrality_data = {}
    for clus_id, cluster in enumerate(clusters):
        max_doc_ids, centralities = get_top_central_cluster_docs(cluster, document_topics, max_docs_per_clus, metric)
        logger.debug('max doc ids {}'.format(max_doc_ids))
        logger.debug('max doc centralities {}'.format(centralities))
        max_doc_titles = get_document_titles(max_doc_ids, document_titles)
        logger.debug('max titles: {}'.format(max_doc_titles))
        centrality_data_of_cluster = {
            'size': len(cluster),
            'titles': max_doc_titles, 
            'centralities': centralities
        }
        centrality_data[clus_id] = centrality_data_of_cluster
    
    logger.info('saving cluster centrality data (titles,centralities) of {} clusters'.format(len(centrality_data)))
    save_data_to_json(centrality_data, output_centrality_data_path)
    
    # prüfe, ob knotenlabel->communityid mapping zu communityid->titles,centralities-mapping passt
    # titles_docids = {title: docid for docid,title in document_titles.items()}
    # for clus_id,centrality_data_of_cluster in centrality_data.items():
        # for title in centrality_data_of_cluster['titles']:
            # assert cluster_labels[int(titles_docids[title])] == clus_id
        
if __name__ == '__main__':
    main()
