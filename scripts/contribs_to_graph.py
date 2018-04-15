import os, sys
import logging
import argparse
from pprint import pformat
from itertools import combinations
from gensim.utils import smart_open
from gensim.corpora import  MmCorpus
from igraph import Graph
from utils.utils import init_gensim_logger

program, logger = init_gensim_logger()

# TODO option für paarweise maß einbauen

def get_related_doc_pairs(author_doc_contribs):    
    for authorid,doc_contribs in enumerate(author_doc_contribs):
        logger.debug('contribs of {}: {}'.format(authorid,doc_contribs))
        for d1_contrib,d2_contrib in combinations(doc_contribs,2):
            co_authorship_degree = min(d1_contrib[1],d2_contrib[1])
            yield d1_contrib[0], d2_contrib[0], co_authorship_degree


def main():
    parser = argparse.ArgumentParser(description='creates a pickled networkx graph from a given authorid-docid contributions file by calculating pairwise document distances', epilog='Example: ./{} --contribs=enwiki-auth-doc-contribs.mm.bz2 --graph=enwiki-document-graph.cpickle '.format(sys.argv[0]))
    parser.add_argument('--contribs', type=argparse.FileType('r'), help='path to input authorid-documentid-contrib MatrixMarketfile (.mm/.mm.bz2)', required=True)
    parser.add_argument('--graph', type=argparse.FileType('w'), help='path to output binary pickled graph file (.cpickle/.cpickle.bz2)', required=True)
    
    args = parser.parse_args()
    input_contribs_path = args.contribs.name
    output_graph_path = args.graph.name
    
    logger.info('running {} with:\n{}'.format(program, pformat({'input_contribs_path':input_contribs_path, 'output_graph_path':output_graph_path})))
    
    author_doc_contribs = MmCorpus(input_contribs_path)
    logger.info('adding edges to graph')
    related_docs = [(d1,d2) for d1,d2,co_authorship_degree in get_related_doc_pairs(author_doc_contribs)]
    graph = Graph(n=None, edges=related_docs, directed=False )
    print(graph)
    #for x in related_docs:
    #    print(x)
        
     #if not G.has_edge(d1, d2):
        #    G.add_edge(d1, d2, weight=co_authorship_degree)
        #else:
        #    G[d1][d2]['weight'] += co_authorship_degree
            
    logger.debug('\n' + pformat(json_graph.adjacency_data(G)))
    logger.info('created graph with {} nodes, {} edges'.format(len(G), G.size()))
    nx.write_gpickle(G, output_graph_path)
    
        
if __name__ == '__main__':
    main()
