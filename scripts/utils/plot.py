import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from scripts.utils.utils import init_logger

logger = init_logger()


# plottet einzelne die Daten data als einzelne Datenpunkte
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
    
# plottet ein Histogramm der Daten data
def histogram_plot(data, ofpath, xlabel, ylabel, range=None, cumulative=False, bins='auto', figsize=(5,2.5)):
    logger.info('plotting hist of {} values to {}'.format(len(data), ofpath))
    logger.info('min value {}, max value {}'.format(np.min(data), np.max(data)))
    logger.debug('data {}'.format(data))
    plt.figure(figsize=figsize)
    plt.hist(data, bins=bins, edgecolor='black', linewidth=1, color='dodgerblue', cumulative=cumulative, range=range, align='left')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.savefig(ofpath, bbox_inches='tight')
    
# plottet ein Säulenhistogramm der x-y-Daten 
def bar_plot(x, y, ofpath, xlabel, ylabel, align='center', figsize=(5,2.5)):
    assert len(x) == len(y)
    logger.info('plotting bars of {} values to {}'.format(len(x), ofpath))
    logger.info('min x value {}, max x value {}'.format(np.min(x), np.max(x)))
    logger.info('min y value {}, max y value {}'.format(np.min(y), np.max(y)))
    logger.debug('x data {}'.format(x))
    logger.debug('y data {}'.format(y))
    ax = plt.figure(figsize=figsize).gca()
    ax.xaxis.set_major_locator(MaxNLocator(integer=True)) # erzwinge Integer-xticks
    plt.bar(x, y, align=align, edgecolor='black', linewidth=1, color='dodgerblue')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.savefig(ofpath, bbox_inches='tight')


# plottet die x-y-Daten als einzelne 2D-Datenpunkte; bei Angabe von labels werden alle Datenpunkte desselben Labels gleich gefärbt
# verschiedene Labels erhalten ein möglichst gestreutes Spektrum verschiedener Farben
def scatter_2d_plot(x, y, ofpath, labels=None, rasterized=False, size=1, figsize=None):
    assert len(x) == len(y)
    logger.info('plotting {} 2d data points to {}'.format(len(x), ofpath))
    
    if labels is None:
        logger.info('plotting unlabeled data')
        color = 'dodgerblue'    
        color_map = None
    else:
        assert len(labels) == len(x)
        logger.info('plotting labeled data')
        color = labels
        color_map = 'prism'
        
    plt.scatter(x, y, c=color, cmap=color_map, s=size, rasterized=rasterized)
    plt.savefig(ofpath, bbox_inches='tight', dpi=200)
    
    
# plottet die x-y-Daten verbunden durch eine Linie
def line_plot(x, y, xlabel, ylabel, ofpath, plot_grid=True, figsize=(5,2.5)):
    assert len(x) == len(y)
    logger.info('plotting {} 2d data points as a connected line to {}'.format(len(x), ofpath))
    plt.figure(figsize=figsize)
    plt.grid(plot_grid)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.plot(x, y, c='dodgerblue') 
    plt.xticks(x) # zeige an der x-Achse nur die geplotteten Daten als xticks
    plt.savefig(ofpath, bbox_inches='tight')
    
    
    
    
    
    