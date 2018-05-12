from math import log2
import numpy as np
from scipy import sparse as sp
from sklearn.metrics.cluster.supervised import contingency_matrix, check_array, check_clusterings
from expected_mutual_info_fast import expected_mutual_information

# Anpassung der Funktionen aus https://github.com/scikit-learn/scikit-learn/blob/master/sklearn/metrics/cluster/supervised.py
# für logarithmus dualis

def entropy(labels):
    if len(labels) == 0:
        return 1.0
    label_idx = np.unique(labels, return_inverse=True)[1]
    pi = np.bincount(label_idx).astype(np.float64)
    pi = pi[pi > 0]
    pi_sum = np.sum(pi)
    return -np.sum((pi / pi_sum) * (np.log2(pi) - log2(pi_sum)))

def mutual_info_score(labels_true, labels_pred, contingency=None):
    if contingency is None:
        labels_true, labels_pred = check_clusterings(labels_true, labels_pred)
        contingency = contingency_matrix(labels_true, labels_pred, sparse=True)
    else:
        contingency = check_array(contingency, accept_sparse=['csr', 'csc', 'coo'], dtype=[int, np.int32, np.int64])
    if isinstance(contingency, np.ndarray):
        nzx, nzy = np.nonzero(contingency)
        nz_val = contingency[nzx, nzy]
    elif sp.issparse(contingency):
        nzx, nzy, nz_val = sp.find(contingency)
    else:
        raise ValueError("Unsupported type for 'contingency': %s" % type(contingency))
    contingency_sum = contingency.sum()
    pi = np.ravel(contingency.sum(axis=1))
    pj = np.ravel(contingency.sum(axis=0))
    log_contingency_nm = np.log2(nz_val)
    contingency_nm = nz_val / contingency_sum
    outer = pi.take(nzx) * pj.take(nzy)
    log_outer = -np.log2(outer) + log2(pi.sum()) + log2(pj.sum())
    mi = (contingency_nm * (log_contingency_nm - log2(contingency_sum)) + contingency_nm * log_outer)
    return mi.sum()
    
def normalized_mutual_info_score(labels_true, labels_pred):
    labels_true, labels_pred = check_clusterings(labels_true, labels_pred)
    classes = np.unique(labels_true)
    clusters = np.unique(labels_pred)
    if (classes.shape[0] == clusters.shape[0] == 1 or classes.shape[0] == clusters.shape[0] == 0):
        return 1.0
    contingency = contingency_matrix(labels_true, labels_pred, sparse=True)
    contingency = contingency.astype(np.float64)
    mi = mutual_info_score(labels_true, labels_pred, contingency=contingency)
    h_true, h_pred = entropy(labels_true), entropy(labels_pred)
    nmi = mi / max(np.sqrt(h_true * h_pred), 1e-10)
    return nmi 
    
def adjusted_mutual_info_score(labels_true, labels_pred):
    labels_true, labels_pred = check_clusterings(labels_true, labels_pred)
    n_samples = labels_true.shape[0]
    classes = np.unique(labels_true)
    clusters = np.unique(labels_pred)
    if (classes.shape[0] == clusters.shape[0] == 1 or classes.shape[0] == clusters.shape[0] == 0):
        return 1.0
    contingency = contingency_matrix(labels_true, labels_pred, sparse=True)
    contingency = contingency.astype(np.float64)
    # Calculate the MI for the two clusterings
    mi = mutual_info_score(labels_true, labels_pred, contingency=contingency)
    # Calculate the expected value for the mutual information
    emi = expected_mutual_information(contingency, n_samples)
    # Calculate entropy for each labeling
    h_true, h_pred = entropy(labels_true), entropy(labels_pred)
    ami = (mi - emi) / (max(h_true, h_pred) - emi)
    return ami
    
    
    
    
    
    
    
    
    
    
    