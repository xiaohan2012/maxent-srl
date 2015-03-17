from collections import (Counter, defaultdict)


def filter_by_frequency(templated_features, cutoff):
    """
    templated_features: list of dict containing templated feature values
    cutoff: some minimal frequency cutoff
    
    >>> templated_features = [{('a',): (1,), ('b',): (2,)}, {('a',): (1,), ('b',): (1,)}]
    >>> filter_by_frequency(templated_features, 2)
    defaultdict(<type 'set'>, {('a',): set([(1,)])})
    """
    table = defaultdict(lambda: Counter())

    for features in templated_features:
        for feature_name, feature_value in features.items():
            table[feature_name][feature_value] += 1
            
      
    selected_features = defaultdict(set)
    
    for feature_name in table:
        for feature_value, freq in table[feature_name].items():
            if freq >= cutoff:
                selected_features[feature_name].add(feature_value)

    return selected_features
