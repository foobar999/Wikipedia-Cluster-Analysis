import argparse
import numpy as np
from scripts.cluster.articles_to_bow import get_filtered_articles_data_from_path
from scripts.utils.utils import init_logger, read_lines
from scripts.utils.plot import histogram_plot, get_quantile

logger = init_logger()


def main():
    parser = argparse.ArgumentParser(description='plots the distribution of minimum document token numbers')
    parser.add_argument("--articles-dump", type=argparse.FileType('r'), help='path to input .xml.bz2 articles dump', required=True)
    parser.add_argument("--namespace-prefixes", type=argparse.FileType('r'), help='file of namespace prefixes to ignore', required=True)
    parser.add_argument("--token-nums-dist", type=argparse.FileType('w'), help='file of plotted distribution of minmum number of tokens', required=True)
    parser.add_argument('--quantile-order', type=float, help='quantile of distribution to consider', required=True)
    
    args = parser.parse_args()
    input_articles_path = args.articles_dump.name
    output_token_nums_dist_path = args.token_nums_dist.name
    quantile_order = args.quantile_order    
    namespace_prefixes = read_lines(args.namespace_prefixes.name) if args.namespace_prefixes else ()
    
    dok_tokens = get_filtered_articles_data_from_path(input_articles_path, 0, 0, (), namespace_prefixes, False)
    logger.info('calculating distribution of document-token-numbers')
    dok_token_nums = np.array(list(len(tokens) for tokens in dok_tokens))
    
    # zur Einschränkung des dargestellten Wertebereiches: ersetze alle Werte, die größer als das quantile_order-Quantil sind, durch das quantile_order-Quantil
    quantile = get_quantile(dok_token_nums, quantile_order)
    dok_token_nums[dok_token_nums > quantile] = quantile 
    
    xlabel = 'Mindestanzahl Tokens'
    ylabel = 'Anzahl Artikel'
    histogram_plot(dok_token_nums, output_token_nums_dist_path, xlabel, ylabel, figsize=(10,2), cumulative=-1)
    
       
    
    
if __name__ == '__main__':
    main()
    

    
