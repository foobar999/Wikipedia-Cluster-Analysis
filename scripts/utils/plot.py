import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scripts.utils.utils import init_logger

logger = init_logger()


def scatter_plot(data, ofpath, xlabel, ylabel, rasterized=False, size=1, figsize=((5,2.5))):
    logger.info('plotting of shape {} to {}'.format(data.shape, ofpath))
    plt.figure(figsize=figsize)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.scatter(np.arange(len(data)), data, c='dodgerblue', s=size, rasterized=rasterized)
    plt.savefig(ofpath, bbox_inches='tight', dpi=300)
       
       
# plottet ein Histogramm der Werte values mit den Häufigkeiten occurences
# def histogram_plot(values, occurences, ofpath, xlabel, ylabel, figsize=((5,2.5))):
    # logger.info('plotting hist of {} values, {} occurences to {}'.format(len(values), len(occurences), ofpath))
    # i_min, i_max = np.argmin(values), np.argmax(values)
    # logger.info('min value {}: {} occurences, max value {}: {} occurences'.format(values[i_min], occurences[i_min], values[i_max], occurences[i_max]))
    # logger.debug('values {}'.format(values))
    # logger.debug('occurences {}'.format(occurences))
    # plt.figure(figsize=figsize)
    # plt.bar(values, occurences, edgecolor='black', linewidth=1, color='dodgerblue')
    # plt.xlabel(xlabel)
    # plt.ylabel(ylabel)
    # plt.savefig(ofpath, bbox_inches='tight')
    # plt.close()
    
    
def apply_quantile(data, quantile_order):
    logger.info('applying quantile {}'.format(quantile_order))
    logger.info('shape before quantile {}, min {} max {}'.format(data.shape, data.min(), data.max()))
    logger.debug('data before quantile {}'.format(data))
    values, counts = np.unique(data, return_counts=True)
    logger.debug('values {}, counts {}'.format(values, counts))
    cumul = np.cumsum(counts)
    total_sum = np.sum(counts)
    quantile_y_index = np.where(cumul >= quantile_order*total_sum)[0][0]
    quantile = values[quantile_y_index]
    res = data[data <= quantile]
    logger.info('shape after quantile {}, min {} max {}'.format(res.shape, res.min(), res.max()))
    return res
    
def histogram_plot(data, ofpath, xlabel, ylabel, bins='auto', figsize=(5,2.5)):
    logger.info('plotting hist of {} values to {}'.format(len(data), ofpath))
    logger.info('min value {}, max value {}'.format(np.min(data), np.max(data)))
    logger.debug('data {}'.format(data))
    plt.figure(figsize=figsize)
    plt.hist(data, bins=bins, edgecolor='black', linewidth=1, color='dodgerblue')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.savefig(ofpath, bbox_inches='tight')
    plt.close()
    
# entfernt von values, occurences alle Einträge ab ausschließlich dem ersten values-Eintrag, dessen Präfixsumme größer gleich quantile_order * Gesamtsumme ist
# def apply_quantile(values, occurences, quantile_order):
    # assert len(values) == len(occurences)
    # assert len(values) > 1
    # logger.info('applying quantile {}'.format(quantile_order))
    # logger.info('before quantile application: number of values {}, min {} max {}'.format(len(values), values[0], values[-1]))
    # logger.debug('values {}'.format(values))
    # logger.debug('occurences {}'.format(occurences))
    
    # cumul_occurences = np.cumsum(occurences)
    # sum_occurences = np.sum(occurences)
    # quantile_index = np.where(cumul_occurences >= quantile_order*sum_occurences)[0][0]
    # new_values = values[:quantile_index+1]
    # new_occurences = occurences[:quantile_index+1]
    
    # logger.debug('new_values {}'.format(new_values))
    # logger.debug('new_occurences {}'.format(new_occurences))
    # logger.info('after quantile application: number of values {}, min {} max {}'.format(len(new_values), new_values[0], new_values[-1]))
    # return new_values, new_occurences
    
    
    