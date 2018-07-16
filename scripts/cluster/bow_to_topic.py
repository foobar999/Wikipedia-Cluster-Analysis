import argparse
from pprint import pformat
import numpy as np
from gensim.corpora import MmCorpus, Dictionary
from gensim.models.wrappers.ldamallet import LdaMallet
from scripts.utils.utils import init_logger

logger = init_logger()


def main():
    parser = argparse.ArgumentParser(description='trains a topic model from a given bag-of-words corpus file and an id2word dictionary')
    parser.add_argument('--bow', type=argparse.FileType('r'), help='path to input text-based MatrixMarket bow corpus file (.mm/.mm.bz2)', required=True)
    parser.add_argument('--id2word', type=argparse.FileType('r'), help='path to input text-based id2word dictionary file (.txt/.txt.bz2)', required=True)
    parser.add_argument('--mallet', type=argparse.FileType('r'), help='path to java mallet executable', required=True)
    parser.add_argument('--model-prefix', type=argparse.FileType('w'), help='prefix of output binary lda model files', required=True)
    parser.add_argument('--num-topics', type=int, help='number of latent topics', required=True)
    parser.add_argument('--num-iterations', type=int, help='set training epochs', required=True)
    parser.add_argument('--alpha', type=float, help='symmetric lda prior value', required=True)
    #parser.add_argument('--beta', type=valid_gensim_prior, help='distribution-over-vocabulary prior: must be float, "symmetric" or "auto"', required=True)

    args = parser.parse_args()
    input_bow_path = args.bow.name
    input_id2word_path = args.id2word.name
    input_mallet_path = args.mallet.name
    output_model_prefix = args.model_prefix.name
    num_topics = args.num_topics
    num_iterations = args.num_iterations
    alpha = args.alpha
    
    logger.info('running topic model with \n{}'.format(pformat({'input_bow_path':input_bow_path, 'input_id2word_path':input_id2word_path, 'input_mallet_path':input_mallet_path, 'output_model_prefix':output_model_prefix, 'num_topics':num_topics, 'num_iterations':num_iterations, 'alpha':alpha})))

    # lade BOW-Instanz & Vokabular, erzeuge & speichere LDA-Instanz
    bow = MmCorpus(input_bow_path)
    id2word = Dictionary.load_from_text(input_id2word_path)
    lda_model = LdaMallet(input_mallet_path, alpha=alpha, corpus=bow, num_topics=num_topics, id2word=id2word, workers=8, prefix=output_model_prefix, optimize_interval=50, iterations=num_iterations)
    logger.info('saving model with output prefix {}'.format(output_model_prefix))
    lda_model.save(output_model_prefix) # speichert NUR Modelldateien, keine eigentlichen Daten

    # gib chrakteristischte Terme der Topics aus
    max_printed_terms = 10
    for topicid in range(num_topics):
        logger.info('topic nr. {}: {}'.format(topicid, lda_model.print_topic(topicid, topn=max_printed_terms)))

    # berechne Mittelwert, Standardabweichung für Theta-Werte (d.h. Anteile der Topics an den Dokumenten)
    theta_sums = [None] * bow.num_docs
    for doc,doc_topics in enumerate(lda_model[bow]):
        theta_sums[doc] = sum(theta for term,theta in doc_topics)
    theta_sums = np.array(theta_sums)
    logger.info('mean theta sum {}'.format(np.mean(theta_sums)))
    logger.info('stddev theta sum {}'.format(np.std(theta_sums)))

    # berechne Mittelwert, Standardabweichung für Phi-Werte (d.h. Anteile der Terme an den Topics)
    phi = lda_model.get_topics()
    logger.info('phi shape {}'.format(phi.shape))
    phi_sums = phi.sum(1)
    logger.info('phi sums shape {}'.format(phi_sums.shape))
    logger.info('mean phi sum {}'.format(np.mean(phi_sums)))
    logger.info('stddev phi sum {}'.format(np.std(phi_sums)))


if __name__ == '__main__':
    main()

    
    
    