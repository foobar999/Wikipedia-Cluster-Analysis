import argparse
from pprint import pformat
from gensim.corpora import MmCorpus
import networkx as nx
from networkx import bipartite
from heapq import nsmallest
from scripts.utils.utils import init_logger, argparse_bool
from scripts.utils.graph import simplify_graph_nwx, get_bipartite_nodes, get_bipartite_node_counts, log_nwx

logger = init_logger()
          
          
# liefert Beiträge aus Korpus als (docid, authorid+offset, value)-Tripel
# zu jedem authorid-wert wird als offset die anzahl der dokumente hinzuaddiert, damit docids und authorids sich nicht überlappen 
def get_edges_from_contribs(contribs):
    authorid_offset = contribs.num_docs
    for docid, contribs_of_doc in enumerate(contribs):
        for authorid, contrib_value in contribs_of_doc:
            yield 'd'+str(docid), 'a'+str(authorid), contrib_value
     
     
def main():
    parser = argparse.ArgumentParser(description='maps a given document-author-contribution file to a weighted bipartite network of document and author nodes')
    parser.add_argument('--contribs', type=argparse.FileType('r'), help='path to input contribution MatrixMarket file (.mm/.mm.bz2)', required=True)
    parser.add_argument('--bipart-graph', type=argparse.FileType('w'), help='path to output graph (.graph/.graph.bz2) file', required=True)
    parser.add_argument('--top-n-contribs', type=int, help='keep at most N highest contribs per author', required=True)
    
    args = parser.parse_args()
    input_contribs_path = args.contribs.name
    output_bipart_graph_path = args.bipart_graph.name
    top_n_contribs = args.top_n_contribs
    
    logger.info('running with:\n{}'.format(pformat({'input_contribs_path':input_contribs_path, 'output_bipart_graph_path':output_bipart_graph_path, 'top_n_contribs':top_n_contribs})))
    
    contribs = MmCorpus(input_contribs_path)
    num_docs = contribs.num_docs
    num_authors = contribs.num_terms
    logger.info('processing contributions of {} documents, {} authors'.format(num_docs, num_authors))
        
    bipart_graph = nx.Graph()
    doc_nodes = tuple('d'+str(n) for n in range(0,num_docs))
    bipart_graph.add_nodes_from(doc_nodes, bipartite=0)
    auth_nodes = tuple('a'+str(n) for n in range(0,num_authors))
    bipart_graph.add_nodes_from(auth_nodes, bipartite=1)    
    bipart_graph.add_weighted_edges_from(get_edges_from_contribs(contribs), weight='weight')
    log_nwx(bipart_graph)
    logger.info('bipartite? {}'.format(bipartite.is_bipartite(bipart_graph))) 
    
    simplify_graph_nwx(bipart_graph)
    logger.info('actual numbers after simplifying: {} docs, {} authors, {} edges'.format(*get_bipartite_node_counts(bipart_graph), len(bipart_graph.edges)))
    max_degree_author = max(bipart_graph.degree(auth_nodes), key=lambda node_deg: node_deg[1])
    logger.info('author {} having max degree of {}'.format(*max_degree_author))   
    
    # aktalisiere variablen 
    doc_nodes, auth_nodes = get_bipartite_nodes(bipart_graph)
    
    logger.info('pruning to top {} edges per author'.format(top_n_contribs))
    for auth_node in auth_nodes:
        logger.debug('author {}'.format(auth_node))
        auth_edges = bipart_graph[auth_node]
        auth_edges = tuple((neighbor,weight['weight']) for neighbor,weight in auth_edges.items())
        logger.debug('incident edges \n{}'.format(pformat(auth_edges)))
        num_remove = len(auth_edges) - top_n_contribs
        author_min_edges = nsmallest(num_remove, auth_edges, key=lambda edge: edge[1])
        logger.debug('removing edges \n{}'.format(pformat(author_min_edges)))
        bipart_graph.remove_edges_from((auth_node,neighbor) for neighbor,weight in author_min_edges)
    
    # keep_max_edges = 10000
    # logger.info('pruning to {} highest edges'.format(keep_max_edges))
    # num_edges_to_remove = len(bipart_graph.edges) - keep_max_edges
    # min_edges = nsmallest(num_edges_to_remove, bipart_graph.edges(data='weight'), key=lambda edge: edge[2])
    # bipart_graph.remove_edges_from(min_edges)
    # log_nwx(bipart_graph)
    
    max_degree_author = max(bipart_graph.degree(auth_nodes), key=lambda node_deg: node_deg[1])
    logger.info('author {} having max degree of {}'.format(*max_degree_author))
    
    # entferne isolierte Knoten
    simplify_graph_nwx(bipart_graph)
    log_nwx(bipart_graph)
    logger.info('new number of documents {}, authors {}'.format(*get_bipartite_node_counts(bipart_graph)))
    
    logger.info('writing graph to {}'.format(output_bipart_graph_path))
    nx.write_gpickle(bipart_graph, output_bipart_graph_path)
   
   
if __name__ == '__main__':
    main()
