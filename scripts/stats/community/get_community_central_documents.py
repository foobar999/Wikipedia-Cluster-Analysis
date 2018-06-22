import json
import argparse
from heapq import nlargest
from pprint import pformat
from igraph import Graph, VertexClustering
from scripts.utils.utils import init_logger, load_communities, load_titles
from scripts.utils.graph import log_igraph

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

    
# liefert die Dokumenttitel der Knoten mit den Namenslabeln node_names
def get_document_titles_of_node_names(node_names, titles):
    return [titles[node_name[1:]] for node_name in node_names] # entferne 'd', das bei allen Dokumenten enthalten
        
# liefert die (maximal) J Knoten aus der Community comm_subgraph mit den höchsten Centrality-Werten, inkl. der jeweiligen Werte
def get_top_nodes_of_communities(comm_subgraph, J, centrality_function):  
    comm_size = comm_subgraph.vcount()
    logger.debug('computing {} centralities of community of size {}'.format(centrality_function.__name__, comm_size))
    node_centralities = centrality_function(comm_subgraph) # insb. weighted_closeness, weighted_betweenness dauern ne weilw
    node_centralities = enumerate(node_centralities)
    max_nodes_centralities = nlargest(min(comm_size,J), node_centralities, key=lambda nd:nd[1])
    max_node_names_centralities = [(comm_subgraph.vs['name'][nodeid],cen) for nodeid,cen in max_nodes_centralities]
    logger.debug('max_weight_node_names {}'.format(max_node_names_centralities))
    return max_node_names_centralities
    
     
def main():
    parser = argparse.ArgumentParser(description='calculated the J most central documents of each community and writes their titles to a JSON file (exactly min(#nodes of community,J) titles are save per community)')
    parser.add_argument('--coauth-graph', type=argparse.FileType('r'), help='path to output pickled, gzipped graph file', required=True)
    parser.add_argument('--communities', type=argparse.FileType('r'), help='path to input .json.bz2 communities file', required=True)
    parser.add_argument('--titles', type=argparse.FileType('r'), help='path to input .json.bz2 titles file', required=True)
    parser.add_argument('--central-titles', type=argparse.FileType('w'), help='path to output .json community->j-central-titles file', required=True)
    centrality_measures = {
        'degree': degree,
        'strength': strength,
        'betweenness': betweenness,
        'closeness': closeness,
        'weighted_betweenness': weighted_betweenness,
        'weighted_closeness': weighted_closeness
    }
    parser.add_argument('--centrality-measure', choices=centrality_measures, help='used centrality measure to calculated centrality', required=True)
    parser.add_argument('--J', type=int, help='maxiumum number of highest considered nodes per community', required=True)
    
    args = parser.parse_args()
    input_coauth_graph_path = args.coauth_graph.name
    input_communities_path = args.communities.name
    input_titles_path = args.titles.name
    output_central_titles_path = args.central_titles.name
    centrality_measure = args.centrality_measure
    J = args.J
    
    logger.info('running with:\n{}'.format(pformat({'input_coauth_graph_path':input_coauth_graph_path, 'input_communities_path':input_communities_path, 'input_titles_path':input_titles_path, 'output_central_titles_path':output_central_titles_path, 'centrality_measure':centrality_measure, 'J':J})))
    
    logger.info('loading graph from {}'.format(input_coauth_graph_path))
    coauth_graph = Graph.Read_Picklez(input_coauth_graph_path)
    log_igraph(coauth_graph)
    
    communities = load_communities(input_communities_path)
    titles = load_titles(input_titles_path)
    
    # entferne Knoten, die nicht in gespeicherter Communitystruktur auftauchen (z.B. weil nicht in Riesencommunity sind)
    logger.info('removing nodes of graph without community labels')
    node_names = coauth_graph.vs['name']
    node_names_of_communities = communities.keys()
    node_names_not_in_communities = set(node_names) - set(node_names_of_communities)
    coauth_graph.delete_vertices(node_names_not_in_communities)
    logger.info('graph stats after removing')
    log_igraph(coauth_graph)
    
    logger.info('creating vertex clustering of community labels')
    node_labels = [communities[name] for name in coauth_graph.vs['name']] 
    community_structure = VertexClustering(coauth_graph, membership=node_labels)
    logger.debug('created vertex clustering {}'.format(community_structure))
        
    logger.info('computing {}-centralities of {} communities'.format(centrality_measure, len(community_structure)))
    centrality_function = centrality_measures[centrality_measure]
    max_document_titles_of_communities = {}
    for comm_id in range(len(community_structure)):
        comm_subgraph = community_structure.subgraph(comm_id)
        max_node_names_centralities = get_top_nodes_of_communities(comm_subgraph, J, centrality_function)
        logger.debug('max_node_names_weights {}'.format(max_node_names_centralities))        
        max_node_names, centralities = zip(*max_node_names_centralities)
        max_doc_titles = get_document_titles_of_node_names(max_node_names, titles)
        logger.debug('max titles: {}'.format(max_doc_titles))
        max_document_titles_of_communities[comm_id] = {'titles': max_doc_titles, 'centralities': centralities}
        
    logger.info('saving community centrality data (titles,centralities) of {} communities to {}'.format(len(max_document_titles_of_communities), output_central_titles_path))
    with open(output_central_titles_path, 'w') as output_central_titles_file:
        json.dump(max_document_titles_of_communities, output_central_titles_file, indent=1)
    
    # prüfe, ob knotenlabel->communityid mapping zu communityid->titles,centralities-mapping passt
    # titles_nodenames = {title: nodename for nodename,title in titles.items()}
    # for comm_id,titles_centralities in max_document_titles_of_communities.items():
        # for title in titles_centralities['titles']:
            # assert communities['d'+titles_nodenames[title]] == comm_id
    
        
if __name__ == '__main__':
    main()
