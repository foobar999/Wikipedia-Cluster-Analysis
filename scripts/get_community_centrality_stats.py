import os, sys
import logging
import argparse
import math
from heapq import nlargest
from pprint import pformat
from igraph import Graph, VertexClustering
import numpy as np
from io import StringIO
from utils.utils import init_logger, log_igraph, load_communities, load_titles

logger = init_logger()

        
def degree(comm_subgraph):
    return comm_subgraph.degree(comm_subgraph.vs)
    
def strength(comm_subgraph):
    return comm_subgraph.strength(comm_subgraph.vs, weights='weight')

def norm_betweenness(betweennesses, N):
    if N > 2:
        return [2*B/((N-1)*(N-2)) for B in betweennesses]
    else:
        return betweennesses
    
# shortest-path betweenness -> anzahl kürzester Wege durch Knoten
# http://igraph.org/r/doc/betweenness.html
# komischerweise in python ohne normalisierung
#   in R:        B'=2*B/(n*n-3*n+2)
#   in networkx: B'=B*2/((n-1)(n-2)) -> das gleiche -> scheint so richtig
def betweenness(comm_subgraph):
    N = comm_subgraph.vcount()
    return norm_betweenness(comm_subgraph.betweenness(), N)    
    
# siehe "Scientific collaboration networks. II. Shortest paths, weighted networks, and centrality"
# "In this simple calculation we assumed that the distance between authors is just the inverse of the weight of their collaborative tie"
# Invertierung der Kantengewichte
# berechnung der kürzesten wege dauert deutlich länger, da im ungewichteten graphen mit breitensuche bestimmbar!
def weighted_betweenness(comm_subgraph):
    comm_subgraph.es['weight'] = [1/w for w in comm_subgraph.es['weight']]
    N = comm_subgraph.vcount()
    return norm_betweenness(comm_subgraph.betweenness(weights='weight'), N)
    
# closeness: in "Centrality in networks: I. Conceptual clarification. Social Networks" zuerst vorgeschlagen?
# closeness eines knoten: (N-1)/(gesamtlänge aller kürzester Wege von/zu diesem Knoten)
def closeness(comm_subgraph):
    return comm_subgraph.closeness(normalized=True)
    
# durchschnittslänge der kürzesten wege dieses knotens zu allen anderen
# zuvor inversion de gewichte -> starke beziehung ergibt kleines gewicht
# hohe closeness -> kleine farness -> von diesem knoten sind alle anderen knoten schnell erreichbar
def weighted_closeness(comm_subgraph):
    comm_subgraph.es['weight'] = [1/w for w in comm_subgraph.es['weight']]
    return comm_subgraph.closeness(weights='weight', normalized=True)


    
def log_titles_of_max_nodes(max_weight_node_names, titles):
    logger.debug('max weight nodes (nodeid,weight): {}'.format(max_weight_node_names))
    for node_name, weight in max_weight_node_names:
        document_title = titles[node_name[1:]]
        logger.info('document title {}, weight {}'.format(document_title, weight))
        yield document_title
    
        
def get_top_nodes_of_communities(comm_subgraph, J, weighting_fun):   
    logger.info('computing {}-weights'.format(weighting_fun.__name__))
    node_weights = weighting_fun(comm_subgraph)
    logger.info('found {} node weights'.format(len(node_weights)))
    max_weight_nodes = nlargest(J, enumerate(node_weights), key=lambda nd:nd[1])
    max_weight_node_names = [(comm_subgraph.vs['name'][nodeid],weight) for nodeid,weight in max_weight_nodes]
    logger.debug('max_weight_node_names \n{}'.format(max_weight_node_names))
    return max_weight_node_names
        
        
def find_max_nodes_per_community(community_structure, considered_communities, titles, J, weighting_fun):   
    logger.info('top-{}-nodes of each community by {}'.format(J, weighting_fun.__name__))
    matrix = np.empty(shape=(J+1,len(considered_communities)), dtype=object)
    for i, (comm_id,comm_size) in enumerate(considered_communities):
        matrix[0,i] = '$n={}$'.format(comm_size)
        comm_subgraph = community_structure.subgraph(comm_id)
        logger.info('extracted subgraph for community {}: {} nodes, {} edges'.format(comm_id, comm_subgraph.vcount(), comm_subgraph.ecount())) 
        max_weight_node_names = get_top_nodes_of_communities(comm_subgraph, J, weighting_fun)  
        document_titles = list(log_titles_of_max_nodes(max_weight_node_names, titles))
        matrix[1:,i] = document_titles
    strf = StringIO()
    np.savetxt(strf, matrix, delimiter=";", fmt="%s")
    logger.info('CSV \n{}'.format(strf.getvalue()))
    
     
def main():
    parser = argparse.ArgumentParser(description='calculated various centrality-related stats (only the giant component of the graph considered!')
    parser.add_argument('--coauth-graph', type=argparse.FileType('r'), help='path to output pickled, gzipped graph file', required=True)
    parser.add_argument('--communities', type=argparse.FileType('r'), help='path to input .json.bz2 communities file', required=True)
    parser.add_argument('--titles', type=argparse.FileType('r'), help='path to input .json.bz2 titles file', required=True)
    parser.add_argument('--K', type=int, help='number of considered, equaldistand communites 0,floor(1*(N-1)/K),...,N-1', required=True)
    parser.add_argument('--J', type=int, help='maxiumum number of highest considered nodes per community', required=True)
    
    args = parser.parse_args()
    input_coauth_graph_path = args.coauth_graph.name
    input_communities_path = args.communities.name
    input_titles_path = args.titles.name
    K = args.K
    J = args.J
    
    logger.info('running with:\n{}'.format(pformat({'input_coauth_graph_path':input_coauth_graph_path, 'input_communities_path':input_communities_path, 'input_titles_path':input_titles_path, 'K':K, 'J':J})))
    
    logger.info('loading graph from {}'.format(input_coauth_graph_path))
    coauth_graph = Graph.Read_Picklez(input_coauth_graph_path)
    logger.info('using largest connected component of largest size instead actual graph')
    coauth_graph = coauth_graph.components().giant()
    log_igraph(coauth_graph)
    
    communities = load_communities(input_communities_path)
    titles = load_titles(input_titles_path)
    
    logger.info('creating vertex clustering of community labels')
    node_labels = [communities[name] for name in coauth_graph.vs['name']]
    community_structure = VertexClustering(coauth_graph, membership=node_labels)
    logger.debug('created vertex clustering {}'.format(community_structure))
        
    community_sizes = list(enumerate(community_structure.sizes()))
    community_sizes.sort(key=lambda t:t[1], reverse=True)
    logger.debug('community sizes, sorted descending\n{}'.format(community_sizes))
        
    logger.info('filtering to communities of at least {} nodes'.format(J))
    community_sizes = [(commid,size) for commid,size in community_sizes if size >= J]
    logger.info('filtered to {} communities'.format(len(community_sizes)))
        
    N = len(community_sizes)
    logger.info('calculating considered communities number of communites N={}, considering K={} equidistant communities'.format(N, K))
    community_indices = [math.floor(k*(N-1)/(K-1)) for k in range(0,K)]
    logger.info('considering indices {}'.format(community_indices))
    considered_communities = [community_sizes[i] for i in community_indices]
    logger.info('considering communities (id,size): {}'.format(considered_communities))
      
    find_max_nodes_per_community(community_structure, considered_communities, titles, J, degree)
    find_max_nodes_per_community(community_structure, considered_communities, titles, J, strength)
    find_max_nodes_per_community(community_structure, considered_communities, titles, J, betweenness)
    find_max_nodes_per_community(community_structure, considered_communities, titles, J, weighted_betweenness)
    find_max_nodes_per_community(community_structure, considered_communities, titles, J, closeness)
    find_max_nodes_per_community(community_structure, considered_communities, titles, J, weighted_closeness)
    
        
if __name__ == '__main__':
    main()
