# https://github.com/scikit-learn/scikit-learn/blob/master/sklearn/metrics/cluster/supervised.py angepasst an log2

from math import log2
import numpy as np
from scipy import sparse as sp
from sklearn.metrics.cluster.supervised import check_clusterings, contingency_matrix
from sklearn.utils.validation import check_array
    
def entropy(labels):
    """Calculates the entropy for a labeling."""
    if len(labels) == 0:
        return 1.0
    label_idx = np.unique(labels, return_inverse=True)[1]
    pi = np.bincount(label_idx).astype(np.float64)
    pi = pi[pi > 0]
    pi_sum = np.sum(pi)
    # log(a / b) should be calculated as log(a) - log(b) for
    # possible loss of precision
    return -np.sum((pi / pi_sum) * (np.log2(pi) - log2(pi_sum)))
    

def mutual_info_score(labels_true, labels_pred, contingency=None):
    """Mutual Information between two clusterings.
    The Mutual Information is a measure of the similarity between two labels of
    the same data. Where :math:`|U_i|` is the number of the samples
    in cluster :math:`U_i` and :math:`|V_j|` is the number of the
    samples in cluster :math:`V_j`, the Mutual Information
    between clusterings :math:`U` and :math:`V` is given as:
    .. math::
        MI(U,V)=\sum_{i=1}^|U| \sum_{j=1}^|V| \\frac{|U_i\cap V_j|}{N}
        \log2\\frac{N|U_i \cap V_j|}{|U_i||V_j|}
    This metric is independent of the absolute values of the labels:
    a permutation of the class or cluster label values won't change the
    score value in any way.
    This metric is furthermore symmetric: switching ``label_true`` with
    ``label_pred`` will return the same score value. This can be useful to
    measure the agreement of two independent label assignments strategies
    on the same dataset when the real ground truth is not known.
    Read more in the :ref:`User Guide <mutual_info_score>`.
    Parameters
    ----------
    labels_true : int array, shape = [n_samples]
        A clustering of the data into disjoint subsets.
    labels_pred : array, shape = [n_samples]
        A clustering of the data into disjoint subsets.
    contingency : {None, array, sparse matrix},
                  shape = [n_classes_true, n_classes_pred]
        A contingency matrix given by the :func:`contingency_matrix` function.
        If value is ``None``, it will be computed, otherwise the given value is
        used, with ``labels_true`` and ``labels_pred`` ignored.
    Returns
    -------
    mi : float
       Mutual information, a non-negative value
    See also
    --------
    adjusted_mutual_info_score: Adjusted against chance Mutual Information
    normalized_mutual_info_score: Normalized Mutual Information
    """
    if contingency is None:
        labels_true, labels_pred = check_clusterings(labels_true, labels_pred)
        contingency = contingency_matrix(labels_true, labels_pred, sparse=True)
    else:
        contingency = check_array(contingency,
                                  accept_sparse=['csr', 'csc', 'coo'],
                                  dtype=[int, np.int32, np.int64])

    if isinstance(contingency, np.ndarray):
        # For an array
        nzx, nzy = np.nonzero(contingency)
        nz_val = contingency[nzx, nzy]
    elif sp.issparse(contingency):
        # For a sparse matrix
        nzx, nzy, nz_val = sp.find(contingency)
    else:
        raise ValueError("Unsupported type for 'contingency': %s" %
                         type(contingency))

    contingency_sum = contingency.sum()
    pi = np.ravel(contingency.sum(axis=1))
    pj = np.ravel(contingency.sum(axis=0))
    log2_contingency_nm = np.log2(nz_val)
    contingency_nm = nz_val / contingency_sum
    # Don't need to calculate the full outer product, just for non-zeroes
    outer = pi.take(nzx) * pj.take(nzy)
    log2_outer = -np.log2(outer) + log2(pi.sum()) + log2(pj.sum())
    mi = (contingency_nm * (log2_contingency_nm - log2(contingency_sum)) +
          contingency_nm * log2_outer)
    return mi.sum()
    
    
def normalized_mutual_info_score(labels_true, labels_pred):
    """Normalized Mutual Information between two clusterings.
    Normalized Mutual Information (NMI) is an normalization of the Mutual
    Information (MI) score to scale the results between 0 (no mutual
    information) and 1 (perfect correlation). In this function, mutual
    information is normalized by ``sqrt(H(labels_true) * H(labels_pred))``
    This measure is not adjusted for chance. Therefore
    :func:`adjusted_mustual_info_score` might be preferred.
    This metric is independent of the absolute values of the labels:
    a permutation of the class or cluster label values won't change the
    score value in any way.
    This metric is furthermore symmetric: switching ``label_true`` with
    ``label_pred`` will return the same score value. This can be useful to
    measure the agreement of two independent label assignments strategies
    on the same dataset when the real ground truth is not known.
    Read more in the :ref:`User Guide <mutual_info_score>`.
    Parameters
    ----------
    labels_true : int array, shape = [n_samples]
        A clustering of the data into disjoint subsets.
    labels_pred : array, shape = [n_samples]
        A clustering of the data into disjoint subsets.
    Returns
    -------
    nmi : float
       score between 0.0 and 1.0. 1.0 stands for perfectly complete labeling
    See also
    --------
    adjusted_rand_score: Adjusted Rand Index
    adjusted_mutual_info_score: Adjusted Mutual Information (adjusted
        against chance)
    Examples
    --------
    Perfect labelings are both homogeneous and complete, hence have
    score 1.0::
      >>> from sklearn.metrics.cluster import normalized_mutual_info_score
      >>> normalized_mutual_info_score([0, 0, 1, 1], [0, 0, 1, 1])
      1.0
      >>> normalized_mutual_info_score([0, 0, 1, 1], [1, 1, 0, 0])
      1.0
    If classes members are completely split across different clusters,
    the assignment is totally in-complete, hence the NMI is null::
      >>> normalized_mutual_info_score([0, 0, 0, 0], [0, 1, 2, 3])
      0.0
    """
    labels_true, labels_pred = check_clusterings(labels_true, labels_pred)
    classes = np.unique(labels_true)
    clusters = np.unique(labels_pred)
    # Special limit cases: no clustering since the data is not split.
    # This is a perfect match hence return 1.0.
    if (classes.shape[0] == clusters.shape[0] == 1 or
            classes.shape[0] == clusters.shape[0] == 0):
        return 1.0
    contingency = contingency_matrix(labels_true, labels_pred, sparse=True)
    contingency = contingency.astype(np.float64)
    # Calculate the MI for the two clusterings
    mi = mutual_info_score(labels_true, labels_pred,
                           contingency=contingency)
    # Calculate the expected value for the mutual information
    # Calculate entropy for each labeling
    h_true, h_pred = entropy(labels_true), entropy(labels_pred)
    nmi = mi / max(np.sqrt(h_true * h_pred), 1e-10)
    return nmi
   
   
   
   
   
   