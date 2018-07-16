import argparse
import networkx as nx
from igraph import Graph
from pprint import pformat
from scripts.utils.utils import init_logger
from scripts.utils.graph import log_nwx, log_igraph

logger = init_logger()
               
     
def main():
    parser = argparse.ArgumentParser(description='converts a weighted pickle networkx Graph to a pickled igraph graph')
    parser.add_argument('--nwx', type=argparse.FileType('r'), help='path to input pickled networkx graph file (.graph/.graph.bz2)', required=True)
    parser.add_argument('--igraph', type=argparse.FileType('w'), help='path to output pickled gzipped igraph file (.graph.gz)', required=True)
    
    args = parser.parse_args()
    input_nwx_path = args.nwx.name
    output_igraph_path = args.igraph.name
    
    logger.info('running with:\n{}'.format(pformat({'input_nwx_path':input_nwx_path, 'output_igraph_path':output_igraph_path})))
    
    logger.info('reading networkx graph from {}'.format(input_nwx_path))
    nwx_graph = nx.read_gpickle(input_nwx_path)
    log_nwx(nwx_graph)
    
    logger.info('converting read networkx graph to igraph graph')
    weighted_edges = nwx_graph.edges(data='weight')
    node_name_ids = {node: id for id,node in enumerate(nwx_graph.nodes())}
    edge_weights = (((n1,n2),w) for n1,n2,w in weighted_edges)
    edges, weights = zip(*edge_weights)
    edges = [(node_name_ids[n1],node_name_ids[n2]) for n1,n2 in edges]
    igraph_graph = Graph(n=len(node_name_ids), edges=list(edges), directed=False, vertex_attrs={'name': list(nwx_graph.nodes())}, edge_attrs={'weight': list(weights)})
    
    log_igraph(igraph_graph)
    
    logger.info('writing graph to {}'.format(output_igraph_path))
    igraph_graph.write_picklez(fname=output_igraph_path)
    
        
if __name__ == '__main__':
    main()
