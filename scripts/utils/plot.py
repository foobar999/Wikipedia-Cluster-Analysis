import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scripts.utils.utils import init_logger

logger = init_logger()


def scatter_plot(data, ofpath, xlabel, ylabel):
    logger.info('plotting of shape {} to {}'.format(data.shape, ofpath))
    #plt.rc('font',family='Calibri')     
    plt.figure(figsize=(5,2.5))
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.scatter(np.arange(len(data)), data, c='dodgerblue', s=1, rasterized=True)
    plt.savefig(ofpath, bbox_inches='tight', dpi=300)
       
