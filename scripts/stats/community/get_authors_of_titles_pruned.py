import argparse
import networkx as nx
from collections import defaultdict
from gensim.corpora import Dictionary
from scripts.utils.utils import init_logger, load_titles, save_data_to_json
from scripts.utils.graph import log_nwx, get_bipartite_nodes

logger = init_logger()
               
     
def main():
    parser = argparse.ArgumentParser(description='creates a mapping document title -> list of authors who contributed to this document (in the pruned affiliation network)')
    parser.add_argument('--bipart-graph', type=argparse.FileType('r'), help='path to input pickled networkx bipart graph file (.graph/.graph.bz2)', required=True)
    parser.add_argument('--id2author', type=argparse.FileType('r'), help='path to input .txt.bz2 authorid->authorname mapping file', required=True)
    parser.add_argument('--titles', type=argparse.FileType('r'), help='path to input .json.bz2 documentid->document title mapping file', required=True)
    parser.add_argument('--title2authornames', type=argparse.FileType('w'), help='path to output .json doctitle->authnames mapping file', required=True)
    
    args = parser.parse_args()
    input_bipart_graph_path = args.bipart_graph.name
    input_id2author_path = args.id2author.name
    input_titles_path = args.titles.name
    output_title2authornames_path = args.title2authornames.name
    
    logger.info('reading bipartite graph from {}'.format(input_bipart_graph_path))
    bipart_graph = nx.read_gpickle(input_bipart_graph_path)
    log_nwx(bipart_graph)
    
    logger.info('loading id2author from {}'.format(input_id2author_path))
    id2author = Dictionary.load_from_text(input_id2author_path)
    logger.info('loaded id2author of size {}'.format(len(id2author)))
    
    titles = load_titles(input_titles_path)
    
    logger.info('generating doctitle->authornames mapping')
    title2authorname = defaultdict(list)
    doc_nodes,_ = get_bipartite_nodes(bipart_graph)
    for doc_node in doc_nodes:
        doc_id = doc_node[1:]
        doc_name = titles[doc_id]
        for author_node in bipart_graph[doc_node]:
            author_id = int(author_node[1:])
            author_name = id2author[author_id]
            title2authorname[doc_name].append(author_name)
    num_doctitles = len(title2authorname)
    num_authornames = sum(len(authornames) for authornames in title2authorname.values())
    logger.info('generated doctitle->authornames mapping: {} keys, {} entries'.format(num_doctitles, num_authornames))
    
    logger.info('sorting doctitle->authornames mapping')
    title2authorname = dict(sorted(title2authorname.items()))
    for authornames in title2authorname.values():
        authornames.sort()
    
    logger.info('saving doctitle->authornames mapping')
    save_data_to_json(title2authorname, output_title2authornames_path)
    
        
if __name__ == '__main__':
    main()
