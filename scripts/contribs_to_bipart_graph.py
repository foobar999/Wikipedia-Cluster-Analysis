import os, sys
import logging
import argparse
from pprint import pformat
from gensim.corpora import MmCorpus
import networkx as nx
from networkx import bipartite
from utils.utils import init_logger, argparse_bool, simplify_graph_nwx, get_bipartite_node_counts, log_nwx

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
    
    args = parser.parse_args()
    input_contribs_path = args.contribs.name
    output_bipart_graph_path = args.bipart_graph.name
    
    logger.info('running with:\n{}'.format(pformat({'input_contribs_path':input_contribs_path, 'output_bipart_graph_path':output_bipart_graph_path})))
    
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
    
    # entferne isolierte Knoten
    simplify_graph_nwx(bipart_graph)
    log_nwx(bipart_graph)
    
    logger.info('writing graph to {}'.format(output_bipart_graph_path))
    nx.write_gpickle(bipart_graph, output_bipart_graph_path)
   
   
if __name__ == '__main__':
    main()
