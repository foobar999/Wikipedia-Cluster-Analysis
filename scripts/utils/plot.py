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
       
# liefert den kleinsten Wert aus data, bei dem die Häufigkeiten aller Werte kleiner gleich diesem Wert den Anteil quantile_order aller Häufigkeiten ausmachen
def get_quantile(data, quantile_order):
    logger.info('determining {}-quantile of data of shape{}'.format(quantile_order, data.shape))
    values, counts = np.unique(data, return_counts=True)
    logger.info('found {} different values: min {}, max {}'.format(len(values), values[0], values[-1]))
    logger.debug('values {}, counts {}'.format(values, counts))
    cumul = np.cumsum(counts)
    total_sum = np.sum(counts)
    quantile_y_index = np.where(cumul >= quantile_order*total_sum)[0][0]
    quantile = values[quantile_y_index]
    logger.info('{}-quantile value: {}'.format(quantile_order, quantile))
    return quantile
    
# plottet ein Histogram der Daten data
def histogram_plot(data, ofpath, xlabel, ylabel, range=None, cumulative=False, bins='auto', figsize=(5,2.5)):
    logger.info('plotting hist of {} values to {}'.format(len(data), ofpath))
    logger.info('min value {}, max value {}'.format(np.min(data), np.max(data)))
    logger.debug('data {}'.format(data))
    plt.figure(figsize=figsize)
    plt.hist(data, bins=bins, edgecolor='black', linewidth=1, color='dodgerblue', cumulative=cumulative, range=range)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.savefig(ofpath, bbox_inches='tight')
    

    
    
    
    
    