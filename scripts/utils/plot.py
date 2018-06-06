import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scripts.utils.utils import init_logger

logger = init_logger()


def scatter_plot(data, ofpath, xlabel, ylabel, rasterized=False, size=1, figsize=((5,2.5))):
    logger.info('plotting of shape {} to {}'.format(data.shape, ofpath))
    #plt.rc('font',family='Calibri')     
    plt.figure(figsize=figsize)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.scatter(np.arange(len(data)), data, c='dodgerblue', s=size, rasterized=rasterized)
    plt.savefig(ofpath, bbox_inches='tight', dpi=300)
       
