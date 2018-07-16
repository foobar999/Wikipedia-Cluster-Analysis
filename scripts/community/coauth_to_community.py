import argparse
from pprint import pformat
from igraph import Graph
from gensim.utils import smart_open
from scripts.utils.utils import init_logger, save_data_to_json
from scripts.utils.graph import log_igraph, log_communities

logger = init_logger()
             
     
def main():
    parser = argparse.ArgumentParser(description='detects communities in a weighted co-authorship-network')
    parser.add_argument('--coauth-graph', type=argparse.FileType('r'), help='path to output pickled, gzipped graph file', required=True)
    parser.add_argument('--communities', type=argparse.FileType('w'), help='path to output .json communities file', required=True)
    methods = {
        'greedy': 'fast greedy detection',
        'louvain': 'louvain detection'
    }
    parser.add_argument('--method', choices=methods, help='community detection method: ' + str(methods), required=True)
    consider_only_communities = {
        'giant': 'consider only subgraph of largest connected component in community detection',
        'non-singleton': 'consider only components with of least 2 nodes'
    }
    parser.add_argument('--consider-only-communities', choices=consider_only_communities, help='consider only specific components; options: {}'.format(consider_only_communities))
    
    args = parser.parse_args()
    input_coauth_graph_path = args.coauth_graph.name
    output_communities_path = args.communities.name
    consider_only_communities = args.consider_only_communities
    method = args.method
    
    logger.info('running with:\n{}'.format(pformat({'input_coauth_graph_path':input_coauth_graph_path, 'output_communities_path':output_communities_path, 'consider_only_communities':consider_only_communities, 'method':method})))
    
    # lade bipartiten Graph
    coauth_graph = Graph.Read_Picklez(input_coauth_graph_path)
    logger.info('read co-authorship graph')
    log_igraph(coauth_graph)
    
    if consider_only_communities is not None:
        if consider_only_communities == 'giant':
            # betrachte nur Riesenkomponente
            logger.info('using largest connected component of largest size instead actual graph')
            coauth_graph = coauth_graph.components().giant()
        elif consider_only_communities == 'non-singleton':
            # entferne Knoten in 1-Knoten-Community, d.h. Knoten ohne Kanten 
            logger.info('using only non-singleton communities')
            node_degrees = coauth_graph.degree(coauth_graph.vs)
            singleton_nodes = [n for n,deg in enumerate(node_degrees) if deg == 0]
            coauth_graph.delete_vertices(singleton_nodes)
        logger.info('new network:')
        log_igraph(coauth_graph)        
    
    # führe Community-Detection mit Verfahren method durch
    logger.info('running {} community detection'.format(method))
    if method == 'greedy':
        dendogram = coauth_graph.community_fastgreedy(weights='weight')
        communities = dendogram.as_clustering()
    elif method == 'louvain':
        communities = coauth_graph.community_multilevel(weights='weight')
    log_communities(communities, coauth_graph)
    
    # speichere communities als JSON-Dictionary {Graph-Label: Community-Label}
    node_names = coauth_graph.vs['name']
    node_community_labels = communities.membership
    name_labeling = dict(zip(node_names, node_community_labels))
    logger.info('saving community labels')
    save_data_to_json(name_labeling, output_communities_path)
        
        
if __name__ == '__main__':
    main()
