import os, sys
import logging
import argparse
from pprint import pformat
from gensim.corpora import MmCorpus
import networkx as nx
from networkx import bipartite
from utils.utils import init_logger, argparse_bool, simplify_graph_nwx, get_bipartite_node_counts, log_graph_nwx

logger = init_logger()

# liefert Beiträge aus Korpus als (docid, authorid+offset, value)-Tripel
# zu jedem authorid-wert wird als offset die anzahl der dokumente hinzuaddiert, damit docids und authorids sich nicht überlappen 
# def get_edges_from_contribs(contribs):
    # authorid_offset = contribs.num_docs
    # for docid, contribs_of_doc in enumerate(contribs):
        # for authorid, contrib_value in contribs_of_doc:
            # yield docid, authorid+authorid_offset, contrib_value

##erzeugt aus Kanten [(v1,v2,w1),...] eine Kantenliste [(v1,v2),...] und eine Gewichtsliste [w1,...]
# def edges_to_lists(weighted_edges):
    # edges = []
    # weights = []
    # for v1, v2, weight in weighted_edges:
        # edges.append((v1,v2))
        # weights.append(weight)
    # return edges, weights
            
            
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
    log_graph_nwx(bipart_graph)
    logger.info('bipartite? {}'.format(bipartite.is_bipartite(bipart_graph))) 
    
    # entferne isolierte Knoten
    simplify_graph_nwx(bipart_graph)
    log_graph_nwx(bipart_graph)
    
    logger.info('writing graph to {}'.format(output_bipart_graph_path))
    nx.write_gpickle(bipart_graph, output_bipart_graph_path)
    
    ## Label der Knoten: Dokumentknoten bekommen Label 'di' mit Dokumentindex i, Autoren analog 'ai'
    # node_names = ['d'+str(n) for n in range(0,num_docs)] + ['a'+str(n) for n in range(0,num_authors)]
    ## bipartiter Graph enthält Dokumente und Autoren als Knoten: Unterscheidung durch 'type'-Information
    # node_types = [0] * num_docs + [1] * num_authors
    # logger.debug('node names {}'.format(node_names))
    # logger.debug('node types {}'.format(node_types))
    
    ## erzeugt gewichteten / ungewichteten Graphen, erstmal ohne Kanten
    # bipart_graph = Graph(n=num_docs+num_authors, directed=None, vertex_attrs={'name': node_names, 'type': node_types}, edge_attrs={'weight': []})
    
    ## füge Kanten ein
    # edges, weights = edges_to_lists(get_edges_from_contribs(contribs))
    # logger.debug('adding edges {} with weights {}'.format(edges, weights))
    # bipart_graph.add_edges(edges)
    # bipart_graph.es['weight'] = weights
    # log_graph(bipart_graph)
    
    # simplify_graph(bipart_graph)
    # log_graph(bipart_graph)
    # logger.info('{} document nodes, {} author nodes'.format(*get_bipartite_node_counts(bipart_graph)))
    
    # logger.info('writing graph to {}'.format(output_bipart_graph_path))
    # bipart_graph.write_picklez(fname=output_bipart_graph_path)
    
    
    
        
if __name__ == '__main__':
    main()
