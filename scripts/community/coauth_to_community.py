import os, sys
import logging
import argparse
import json
from pprint import pformat
from igraph import Graph
from gensim.utils import smart_open
from scripts.utils.utils import init_logger, log_igraph, log_communities, argparse_bool

logger = init_logger()
             
     
def main():
    parser = argparse.ArgumentParser(description='determines communities in of a weighted co-authorship-network')
    parser.add_argument('--coauth-graph', type=argparse.FileType('r'), help='path to output pickled, gzipped graph file', required=True)
    parser.add_argument('--communities', type=argparse.FileType('w'), help='path to output .json communities file', required=True)
    parser.add_argument('--use-giant-comp', type=argparse_bool, help='if set: use connected components with most nodes instead of actual graph', required=True)
    methods = {
        'greedy': 'fast greedy detection',
        'louvain': 'louvain detection'
    }
    parser.add_argument('--method', choices=methods, help='community detection method: ' + str(methods), required=True)
    
    args = parser.parse_args()
    input_coauth_graph_path = args.coauth_graph.name
    output_communities_path = args.communities.name
    use_giant_comp = args.use_giant_comp
    method = args.method
    
    logger.info('running with:\n{}'.format(pformat({'input_coauth_graph_path':input_coauth_graph_path, 'output_communities_path':output_communities_path, 'use_giant_comp':use_giant_comp, 'method':method})))
    
    
    # lade bipartiten Graph
    coauth_graph = Graph.Read_Picklez(input_coauth_graph_path)
    logger.info('read co-authorship graph')
    log_igraph(coauth_graph)
    
    # ersetze ggf. durch seine größte Zusammenhangskomponente
    if use_giant_comp:
        logger.info('using largest connected component of largest size instead actual graph')
        coauth_graph = coauth_graph.components().giant()
        log_igraph(coauth_graph)        
    
    # community detection 
    logger.info('running {} community detection'.format(method))
    if method == 'greedy':
        dendogram = coauth_graph.community_fastgreedy(weights='weight')
        communities = dendogram.as_clustering()
    elif method == 'louvain':
        communities = coauth_graph.community_multilevel(weights='weight')
    log_communities(communities, coauth_graph)
    
    # speichere communities: speichere keine Indizes, sondern gespeicherte Labels
    node_names = coauth_graph.vs['name']
    node_community_labels = communities.membership
    name_labeling = dict(zip(node_names, node_community_labels))
    logger.debug('saving labels \n{}'.format(pformat(name_labeling)))
    with open(output_communities_path, 'w') as output_communities_file:
        json.dump(name_labeling, output_communities_file, indent=1)
        
        
if __name__ == '__main__':
    main()
