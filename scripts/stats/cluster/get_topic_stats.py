import argparse
from collections import defaultdict
from pprint import pformat
from gensim import matutils
from gensim.corpora import MmCorpus
from gensim.utils import SaveLoad
from scipy.sparse import dok_matrix
from scripts.utils.utils import init_logger

logger = init_logger()


def get_topic_terms(ldamodel, topicid, topn=10):
    topic = ldamodel.get_topics()[topicid]
    topic = topic / topic.sum()  # normalize to probability distribution
    bestn = matutils.argsort(topic, topn, reverse=True)
    return [(idx, topic[idx]) for idx in bestn]

    
def main():
    parser = argparse.ArgumentParser(description='prints the topics of a LDA instance, sorted decreasing by thei average probabilities in the collection; prints some stats of the appereances of the most important terms of the most important topics')
    parser.add_argument('--bow', type=argparse.FileType('r'), help='path to input bow file (.mm/.mm.bz2)', required=True)
    parser.add_argument('--model-prefix', type=argparse.FileType('r'), help='prefix of input binary lda model files', required=True)
    
    args = parser.parse_args()
    input_bow_path = args.bow.name
    input_model_prefix = args.model_prefix.name
    
    logger.info('running with:\n{}'.format(pformat({'input_bow_path':input_bow_path, 'input_model_prefix':input_model_prefix})))
    
    logger.info('loading bow corpus from {}'.format(input_bow_path))
    bow = MmCorpus(input_bow_path)
    logger.info('loading topic model from {}'.format(input_model_prefix))
    model = SaveLoad.load(input_model_prefix)
    logger.info('loaded {} docs, {} topics'.format(bow.num_docs, model.num_topics))
    
    logger.info('generating sparse document-topic-matrix')
    document_topic_probs = dok_matrix((bow.num_docs, model.num_topics), dtype='d')
    for docid, topics in enumerate(model[bow]):
        for topicid, prob in topics:
            document_topic_probs[docid,topicid] = prob
    document_topic_probs = document_topic_probs.tocsr()
    
    logger.info('calculating average topic probabilities of the document collection')
    topics_avg = document_topic_probs.sum(axis=0) / bow.num_docs
    topics_max = document_topic_probs.max(axis=0).todense().tolist()[0]
    logger.debug('avg {} shape {}'.format(topics_avg, topics_avg.shape))
    logger.debug('max {} len {}'.format(topics_max, len(topics_max)))
    topics_avg = list(enumerate(topics_avg.tolist()[0]))
    topics_avg.sort(key=lambda t:t[1], reverse=True)
    
    num_printed_terms = 10
    logger.info('topics with highest average probabilities')
    for topicid, topic_avg_prob in topics_avg:
        logger.info('topic ID={0}, avgprob={1:.4f}, maxprob={2:.4f}, terms:\n{3}'.format(topicid, topic_avg_prob, topics_max[topicid], model.print_topic(topicid, topn=num_printed_terms)))
        
    num_top_topics = min(5, len(topics_avg))
    num_top_terms = 20
    top_topics = [topicid for topicid,topic_avg in topics_avg][:num_top_topics]
    logger.info('calculating stats of top-{}-topics {} with top-{}-terms per topic'.format(num_top_topics, top_topics, num_top_terms))
    term_topics = defaultdict(list) # mapping termid->topicids für alle termids, die in top-k von irgendwelchen topics enthalten
    for topicid in top_topics:
        for termid, prob in get_topic_terms(model, topicid, topn=num_top_terms):
            term_topics[termid].append(topicid)
    term_topics = dict(term_topics)
        
    num_different_docs_per_topic = {topicid: 0 for topicid in top_topics}
    sum_bow_values_per_topic = {topicid: 0 for topicid in top_topics}
    for docid, document_term_bow in enumerate(bow):
        doc_topics = set()
        for termid, bow_value in document_term_bow:
            if termid in term_topics:
                for topicid in term_topics[termid]:
                    doc_topics.add(topicid)
                    sum_bow_values_per_topic[topicid] += bow_value
        for topicid in doc_topics:
            num_different_docs_per_topic[topicid] += 1
    
    for topicid in top_topics:
        logger.info('top-{}-terms of topic {} occure {} times in collection'.format(num_top_terms, topicid, int(sum_bow_values_per_topic[topicid])))
        logger.info('top-{}-terms of topic {} occure {} different documents'.format(num_top_terms, topicid, num_different_docs_per_topic[topicid]))
    
    
if __name__ == '__main__':
    main()
    
