import argparse
from heapq import nsmallest
from pprint import pformat
from math import log10
import networkx as nx
from networkx import bipartite
from scripts.utils.utils import init_logger
from scripts.utils.graph import log_nwx, get_bipartite_nodes, simplify_graph_nwx

logger = init_logger()
            

# Jaccard-Ähnlichkeit der Knoten v1,v2 im Graph graph
def jaccard(graph, v1, v2):
    neighbors1, neighbors2 = set(graph[v1]), set(graph[v2])
    counter = len(neighbors1 & neighbors2)
    if counter == 0:
        return 0
    denominator = len(neighbors1) + len(neighbors2) - counter
    return counter / denominator
    
# Skalarprodukt der Dokument-Autor-Beiträge von v1,v2
def dot_product(graph, v1, v2):
    nbrs1, nbrs2 = graph[v1], graph[v2]
    common_nbrs = set(nbrs1) & set(nbrs2)
    return sum(nbrs1[n]['weight']*nbrs2[n]['weight'] for n in common_nbrs)    
     
     
def main():
    parser = argparse.ArgumentParser(description='maps a given bipartite graph to a co-authorship graph of documents')
    parser.add_argument('--bipart-graph', type=argparse.FileType('r'), help='path to input pickled networkx bipart graph file (.graph/.graph.bz2)', required=True)
    parser.add_argument('--coauth-graph', type=argparse.FileType('w'), help='path to output pickled networkx coauth graph file (.graph/.graph.bz2)', required=True)
    modes = {
        'mul': 'weight of edges between d1 and d2 is the number of authors contributing to both',
        'jac': 'weight of edges between d1 and d2 is the jaccard similarity of shared authors',
        'coll': 'weight of edges between d1 and d2 is newmans collaboration weight',
        'dot': 'dot product of weighted author vectors of d1 and d2',
        'logdot': 'dot product of weighted author vectors of d1 and d2, each weighted log10-ed',
    }
    parser.add_argument('--mode', choices=modes, help='co-authorship generation mode: ' + str(modes), required=True)
    
    args = parser.parse_args()
    input_bipart_path = args.bipart_graph.name
    output_coauth_graph_path = args.coauth_graph.name
    mode = args.mode
    
    logger.info('running with:\n{}'.format(pformat({'input_bipart_path':input_bipart_path, 'output_coauth_graph_path':output_coauth_graph_path, 'mode':mode})))
    
    # lade bipartiten Graph
    logger.info('reading bipartite graph from {}'.format(input_bipart_path))
    bipart_graph = nx.read_gpickle(input_bipart_path)
    log_nwx(bipart_graph)
    doc_nodes, auth_nodes = get_bipartite_nodes(bipart_graph)
    logger.info('{} document nodes, {} author nodes'.format(len(doc_nodes), len(auth_nodes)))
    
    # erzeuge Dokumentnetzwerk durch One-Mode-Projektion
    logger.info('running one-mode {} projection'.format(mode))
    if mode == 'mul':
        coauth_graph = bipartite.weighted_projected_graph(bipart_graph, doc_nodes, ratio=False)
    elif mode == 'jac':
        coauth_graph = bipartite.generic_weighted_projected_graph(bipart_graph, doc_nodes, weight_function=jaccard)
        #coauth_graph = bipartite.overlap_weighted_projected_graph(bipart_graph, doc_nodes, jaccard=True)
    elif mode == 'coll':
        coauth_graph = bipartite.collaboration_weighted_projected_graph(bipart_graph, doc_nodes)     
    elif mode in ('dot', 'logdot'):
        # logarithmiere alle Gewichte bei 'logdot'
        if mode == 'logdot': 
            for v1,v2,data in bipart_graph.edges(data=True):
                data['weight'] = log10(data['weight']+1)
        coauth_graph = bipartite.generic_weighted_projected_graph(bipart_graph, doc_nodes, weight_function=dot_product)
    log_nwx(coauth_graph)    
        
    # behalte nur die Kanten mit den K größten Gewichten im gesamten Dokumentnetzwerk
    # hab ich bei der Arbeit durch Verwendung eines sehr großen K ignoriert
    #logger.info('pruning to {} highest edges'.format(keep_max_edges))
    #num_edges_to_remove = len(coauth_graph.edges) - keep_max_edges
    #min_edges = nsmallest(num_edges_to_remove, coauth_graph.edges(data='weight'), key=lambda edge: edge[2])
    #coauth_graph.remove_edges_from(min_edges)
    #log_nwx(coauth_graph)
    
    # speichere Dokumentnetzwerk
    logger.info('writing graph to {}'.format(output_coauth_graph_path))
    nx.write_gpickle(coauth_graph, output_coauth_graph_path)
    
        
if __name__ == '__main__':
    main()

    
    
    