import argparse
import numpy as np
from scripts.utils.utils import init_logger
from scripts.utils.documents import load_cluster_labels
from scripts.utils.plot import scatter_plot

logger = init_logger()
    

def main():
    parser = argparse.ArgumentParser(description='plots descending LOF-values of documents')
    parser.add_argument('--outlier-scores', type=argparse.FileType('r'), help='path to input JSON outlier scores file', required=True)
    parser.add_argument('--lof-plot', type=argparse.FileType('w'), help='path to output LOF-values plot file', required=True)

    args = parser.parse_args()
    input_outlier_scores_path = args.outlier_scores.name
    output_lof_plot_path = args.lof_plot.name
   
    outlier_scores = np.array(load_cluster_labels(input_outlier_scores_path))
    outlier_scores[::-1].sort()
    scatter_plot(outlier_scores, output_lof_plot_path, 'Dokument', 'Local Outlier Factor')
    

if __name__ == '__main__':
    main()

