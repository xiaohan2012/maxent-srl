import numpy as np
from collections import defaultdict

def encode(data_features, features):
    """
    data_features: list of dict of feature values
    features: the selected features

    Return:
    1. np.array(2d) of the encoded data
    2. feature_value to column index mapping

    >>> data_features = [{'a': 1, 'b': 1}, {'a': 2, 'b': 2}, {'a': 3, 'b': 3}]
    >>> features = {'a': set([1, 2]), 'b': set([1])}
    >>> data, mapping = encode(data_features, features)
    >>> data
    array([[ 1.,  0.,  1.],
           [ 0.,  1.,  0.],
           [ 0.,  0.,  0.]])
    >>> mapping
    defaultdict(<type 'dict'>, {'a': {1: 0, 2: 1}, 'b': {1: 2}})
    """
    acc = 0
    mapping = defaultdict(dict)
    for name, values in features.items():
        for value in values:
            mapping[name][value] = acc
            acc+=1

    data = np.zeros((len(data_features), acc))

    for row, features in zip(data, data_features):
        for key, value in features.items():
            if key in mapping and value in mapping[key]:
                row[mapping[key][value]] = 1
    return data, mapping
    
