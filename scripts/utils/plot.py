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
           
# liefert alle Daten von data, die sich im quantile_order-Quantil befinden 
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
    
# plottet ein Histogram der Daten data
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
    
    