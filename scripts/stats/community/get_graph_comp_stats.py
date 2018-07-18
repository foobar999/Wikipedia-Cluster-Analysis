import argparse
from pprint import pformat
import numpy as np
from igraph import Graph
from scripts.utils.utils import init_logger
from scripts.utils.graph import log_igraph
from scripts.utils.plot import get_quantile, bar_plot

logger = init_logger()


def main():
    parser = argparse.ArgumentParser(description='plots the connected components size distribution of a given graph')
    parser.add_argument('--graph', type=argparse.FileType('r'), help='path to input pickled .cpickle.gz graph file ', required=True)
    parser.add_argument('--img', type=argparse.FileType('w'), help='path of output img file', required=True)
    parser.add_argument('--quantile-order', type=float, help='quantile of histrograms to consider', required=True)
    
    args = parser.parse_args()
    input_graph_path = args.graph.name
    output_img_path = args.img.name
    quantile_order = args.quantile_order
    
    logger.info('running with:\n{}'.format(pformat({'input_graph_path':input_graph_path, 'output_img_path':output_img_path, 'quantile_order':quantile_order})))
    
    graph = Graph.Read_Picklez(input_graph_path)        
    logger.info('loaded graph')
    log_igraph(graph)
        
    logger.info('calculating connected components')
    components = graph.components()
    logger.debug(components)
    components_sizes = np.array([len(comp) for comp in components])
    logger.info('max component size {}'.format(components_sizes.max()))
        
    logger.info('component size distribution of {}-quantile'.format(quantile_order))
    sizes, sizes_counts = np.unique(components_sizes, return_counts=True)
    logger.info('frequencies:\n{}'.format(np.vstack((sizes, sizes_counts)).T))
    
    quantile = get_quantile(components_sizes, quantile_order)
    components_sizes = components_sizes[components_sizes <= quantile]
    sizes, sizes_counts = np.unique(components_sizes, return_counts=True)
    xlabel = 'Knotenanzahl Zusammenhangskomponente'
    ylabel = 'Häufigkeit'
    bar_plot(sizes, sizes_counts, output_img_path, xlabel, ylabel)
    
        
if __name__ == '__main__':
    main()
