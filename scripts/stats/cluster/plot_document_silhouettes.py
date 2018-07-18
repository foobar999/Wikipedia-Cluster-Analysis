import argparse
import numpy as np
from scripts.utils.utils import init_logger
from scripts.utils.plot import line_plot

logger = init_logger()


def main():
    parser = argparse.ArgumentParser(description='plots a given csv silhouette data file (2 columns)')
    parser.add_argument('--csv-data', type=argparse.FileType('r'), help='path to input csv data', required=True)
    parser.add_argument('--img-file', type=argparse.FileType('w'), help='path to output im file', required=True)

    args = parser.parse_args()
    input_csv_data_path = args.csv_data.name
    output_img_path = args.img_file.name

    logger.info('loading csv data from {}'.format(input_csv_data_path))
    csv_data = np.genfromtxt(input_csv_data_path, delimiter=' ', names=('x','y'), dtype=None)
    logger.info('loaded data of shape {}'.format(csv_data.shape))
    logger.debug('loaded data \n{}'.format(csv_data))
    
    logger.info('plotting csv data')  
    xlabel = '#Cluster'
    ylabel = 'Silhouettenkoeffizient'
    figsize = (7,3.5)
    line_plot(csv_data['x'], csv_data['y'], xlabel, ylabel, output_img_path, plot_grid=True, figsize=figsize)
    

if __name__ == '__main__':
    main()

