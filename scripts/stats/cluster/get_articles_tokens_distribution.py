import argparse
import numpy as np
from scripts.cluster.articles_to_bow import get_filtered_articles_data_from_path
from scripts.utils.utils import init_logger, read_lines
from scripts.utils.plot import histogram_plot, apply_quantile

logger = init_logger()


def main():
    parser = argparse.ArgumentParser(description='plots the distribution of document token numbers')
    parser.add_argument("--articles-dump", type=argparse.FileType('r'), help='path to input .xml.bz2 articles dump', required=True)
    parser.add_argument("--namespace-prefixes", type=argparse.FileType('r'), help='file of namespace prefixes to ignore', required=True)
    parser.add_argument("--token-nums-dist", type=argparse.FileType('w'), help='file of plotted distribution of number of tokens', required=True)
    parser.add_argument('--quantile-order', type=float, help='quantile of distribution to consider', required=True)
    
    args = parser.parse_args()
    output_token_nums_dist_path = args.token_nums_dist.name
    input_articles_path = args.articles_dump.name
    quantile_order = args.quantile_order    
    namespace_prefixes = read_lines(args.namespace_prefixes.name) if args.namespace_prefixes else ()
    
    dok_tokens = get_filtered_articles_data_from_path(input_articles_path, 0, 0, (), namespace_prefixes, False)
    logger.info('calculating distribution of document-token-numbers')
    dok_token_nums = np.array(list(len(tokens) for tokens in dok_tokens))
    dok_token_nums = apply_quantile(dok_token_nums, quantile_order)
    
    xlabel = 'Anzahl Tokens je Dokument'
    ylabel = 'Häufigkeit'
    histogram_plot(dok_token_nums, output_token_nums_dist_path, xlabel, ylabel)
    
       
    
    
if __name__ == '__main__':
    main()
    

    
