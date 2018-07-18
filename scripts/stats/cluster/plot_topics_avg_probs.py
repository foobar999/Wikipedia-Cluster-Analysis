import argparse
import numpy as np
from pprint import pformat
from scripts.utils.utils import init_logger
from scripts.utils.documents import load_document_topics
from scripts.utils.plot import scatter_plot

logger = init_logger()

    
def main():
    parser = argparse.ArgumentParser(description='plots 1. average probalities per topic 3. cdf of these probabilities')
    parser.add_argument('--document-topics', type=argparse.FileType('r'), help='path to input document-topic-file (.npz)', required=True)
    parser.add_argument('--topic-avg-probs', type=argparse.FileType('w'), help='path to output avg prop plot file', required=True)
    parser.add_argument('--topic-avg-probs-cdf', type=argparse.FileType('w'), help='path to output avg prob cdf plot file', required=True)

    args = parser.parse_args()
    input_document_topics_path = args.document_topics.name
    output_topic_avg_probs_path = args.topic_avg_probs.name
    output_topic_avg_probs_cdf_path = args.topic_avg_probs_cdf.name

    document_topics = load_document_topics(input_document_topics_path)
    
    logger.info('calculating average probability per topic')
    average_topic_props = np.average(document_topics, axis=0)
    logger.info('shape of average res {}'.format(average_topic_props.shape))
    average_topic_props[::-1].sort()
    logger.info('sum over averages {}'.format(average_topic_props.sum()))    
    
    logger.info('plotting average topic probabilites')
    xlabel = 'Topic'
    ylabel = 'Ø Anteil'
    scatter_plot(average_topic_props, output_topic_avg_probs_path, xlabel, ylabel)
    
    average_topic_props_cdf = np.cumsum(average_topic_props)
    logger.info('plotting average topic probabilites cumulative distribution function')
    xlabel = 'Topic'
    ylabel = 'Ø Anteil (CDF)'
    scatter_plot(average_topic_props_cdf, output_topic_avg_probs_cdf_path, xlabel, ylabel)
    

    
    
if __name__ == '__main__':
    main()

