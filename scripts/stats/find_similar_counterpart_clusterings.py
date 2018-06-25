import argparse
from pprint import pformat
from scripts.utils.utils import init_logger, load_compressed_json_data
from scripts.utils.comparison import clustering_labels_to_sets, get_equidistant_indices, get_max_num_titles_in_centrality_data
from scripts.utils.comparison import get_partitions_titles_matrix, display_matrix_as_csv

logger = init_logger()
                 

# Jaccard-Ähnlichkeit beider Mengen
def jaccard(set1, set2):
    intsect = len(set1 & set2)
    return intsect / (len(set1)+len(set2)-intsect)
    

# liefert zum Clustering cluster das Jaccard-ähnlichste Cluster aus cp_clustering
def find_most_similar_counterpart_cluster_id(cluster, cp_clustering):
    most_similar_cluster_id = max(range(len(cp_clustering)), key=lambda id:jaccard(cluster,cp_clustering[id]))
    return most_similar_cluster_id
    
    
# bestimmt num_sample_clusters äquidistante Cluster aus clustering der Mindestgröße min_sample_cluster_size, 
# und bestimmt jeweils das ähnlichste Cluster aus der Gegenseite cp_clustering
# liefert je Sample-Cluster eine Tupel (Sample-ClusterID, ClusterID des ähnlichsten Clusters, Jaccard-Ähnlichkeit, #gemeinsamer Dokumente)
def find_most_similar_counterparts_in_clustering(clustering, cp_clustering, num_sample_clusters, min_sample_cluster_size):
    logger.info('finding counterpart clusters of clustering of size {} in clustering of size {}'.format(len(clustering), len(cp_clustering)))
    
    logger.info('considering only clusters of size {}'.format(min_sample_cluster_size))
    cluster_ids = list(range(len(clustering)))
    cluster_ids = [id for id in cluster_ids if len(clustering[id]) >= min_sample_cluster_size] 
    logger.info('considering {} clusters'.format(len(cluster_ids)))
    
    cluster_ids.sort(key=lambda id:len(clustering[id]), reverse=True)
    sample_indices = get_equidistant_indices(len(cluster_ids), num_sample_clusters)
    logger.info('sample cluster indices: {}'.format(sample_indices))
    sample_cluster_ids = [cluster_ids[i] for i in sample_indices]
    logger.info('sample cluster ids: {}'.format(sample_cluster_ids))
    logger.info('sample cluster sizes: {}'.format([len(clustering[i]) for i in sample_cluster_ids]))
    
    sample_cluster_counterpart_data = []
    for sample_cluster_id in sample_cluster_ids:
        sample_cluster = clustering[sample_cluster_id]
        most_similar_cluster_id = find_most_similar_counterpart_cluster_id(sample_cluster, cp_clustering)
        most_similar_cluster = cp_clustering[most_similar_cluster_id]
        jac = jaccard(sample_cluster, most_similar_cluster)
        common_docs = len(sample_cluster & most_similar_cluster)
        sample_cluster_counterpart_data.append((sample_cluster_id,most_similar_cluster_id,jac,common_docs))
    return sample_cluster_counterpart_data

    
# formatiert die ausgegebenen Centrality-Daten cluster_centrality_data eines Clusters
def format_cluster_centrality_data(cluster_centrality_data):
    return 'size: {}, titles: {}'.format(cluster_centrality_data['size'], cluster_centrality_data['titles'])
 
 
def display_csv_centrality_matrix_of_samples(samples_centrality_data):
    samples_centrality_matrix = get_partitions_titles_matrix(samples_centrality_data)
    display_matrix_as_csv(samples_centrality_matrix)
 
 
# bestimmt Sample-Cluster aus clustering und bestimmt jeweils das ähnlichste Cluster aus cp_clustering, loggt jeweils die Centrality-Daten 
def analyze_clustering_similarities(clustering, cp_clustering, centrality_data, cp_centrality_data, num_sample_clusters):
    min_sample_cluster_size = get_max_num_titles_in_centrality_data(centrality_data.values())
    sample_cluster_counterpart_data = find_most_similar_counterparts_in_clustering(clustering, cp_clustering, num_sample_clusters, min_sample_cluster_size)
    
    for sample_cluster_id, most_similar_cluster_id, jac, common_docs in sample_cluster_counterpart_data:
        cluster_centrality_data = centrality_data[sample_cluster_id]
        logger.info('of cluster: id {}, {}'.format(sample_cluster_id, format_cluster_centrality_data(cluster_centrality_data)))
        cp_cluster_centrality_data = cp_centrality_data[most_similar_cluster_id]
        logger.info('most similar counterpart cluster: id {}, {}'.format(most_similar_cluster_id, format_cluster_centrality_data(cp_cluster_centrality_data)))
        logger.info('jaccard {}, number of common documents {}'.format(jac, common_docs))
    
    # logge Tabelle der Centrality-Daten der Sample-Cluster
    samples_centrality_data = [centrality_data[scid] for scid,_,_,_ in sample_cluster_counterpart_data]
    logger.info('centrality data of samples')
    display_csv_centrality_matrix_of_samples(samples_centrality_data)
    
    # logger Tabelle der Centrality-Daten der jeweils ähnlichsten Cluster der Sample-Cluster
    cp_similar_centrality_data = [cp_centrality_data[mscid] for _,mscid,_,_ in sample_cluster_counterpart_data]
    logger.info('centrality data of most similar clusters of samples')
    display_csv_centrality_matrix_of_samples(cp_similar_centrality_data)
    
    
def main():
    parser = argparse.ArgumentParser(description='for two clusterings C1 and C2: 1. samples some equidistant clusters of C1. 2. finds the most Jaccard-similar cluster of C2 for each sample cluster of C1. 3. repeats 1. and 2. with swapped roles of C1 and C2')
    parser.add_argument('--title-clusterings', nargs=2, type=argparse.FileType('r'), metavar=('TC1','TC2'), help='path to two input .json.bz2 titleclusterings files', required=True)
    parser.add_argument('--centrality-data', nargs=2, type=argparse.FileType('r'), metavar=('CD1','CD2'), help='path to two input .json.bz2 clustering->centrality_data files', required=True)
    parser.add_argument('--num-sample-clusters', type=int, help='number of sampled equidistant clusters', required=True)
    
    args = parser.parse_args()
    input_title_clusterings_paths = (args.title_clusterings[0].name, args.title_clusterings[1].name)
    input_centrality_data_paths = (args.centrality_data[0].name, args.centrality_data[1].name)
    num_sample_clusters = args.num_sample_clusters
    
    logger.info('running with:\n{}'.format(pformat({'input_title_clusterings_paths':input_title_clusterings_paths, 'input_centrality_data_paths':input_centrality_data_paths})))
    
    logger.info('loading labels of both clusterings')
    title_clustering1 = load_compressed_json_data(input_title_clusterings_paths[0])
    title_clustering2 = load_compressed_json_data(input_title_clusterings_paths[1])
    
    logger.info('loading centrality data of both clusterings')
    centrality_data1 = load_compressed_json_data(input_centrality_data_paths[0])
    centrality_data1 = {int(cluster_id): data for cluster_id, data in centrality_data1.items()} # konvertiere str-Keys zu int-Keys 
    centrality_data2 = load_compressed_json_data(input_centrality_data_paths[1])
    centrality_data2 = {int(cluster_id): data for cluster_id, data in centrality_data2.items()}
    
    clustering1 = clustering_labels_to_sets(title_clustering1)
    clustering2 = clustering_labels_to_sets(title_clustering2)
    
    logger.info('')
    logger.info('analyzing clustering1 -> clustering2 similarities')
    analyze_clustering_similarities(clustering1, clustering2, centrality_data1, centrality_data2, num_sample_clusters)
    logger.info('')
    logger.info('analyzing clustering2 -> clustering1 similarities')
    analyze_clustering_similarities(clustering2, clustering1, centrality_data2, centrality_data1, num_sample_clusters)
    
        
        
if __name__ == '__main__':
    main()
