def apply_templates(data_features, templates):
    """
    >>> templates = [\
    ('h', 'f'), \
    ('p', 't', 'f'),\
    ('t', 'f')\
    ]
    >>> data_features = [{'h': 0, 'f': 0, 'p': 1, 't': 2}, {'h': 1, 'f': 0, 'p': 2, 't': 1}, {'h': 0, 'f': 1, 'p': 0, 't': 1}]
    >>> apply_templates(data_features, templates) # doctest: +NORMALIZE_WHITESPACE
    [{('p', 't', 'f'): (1, 2, 0), ('t', 'f'): (2, 0), ('h', 'f'): (0, 0)}, {('p', 't', 'f'): (2, 1, 0), ('t', 'f'): (1, 0), ('h', 'f'): (1, 0)}, {('p', 't', 'f'): (0, 1, 1), ('t', 'f'): (1, 1), ('h', 'f'): (0, 1)}]
    """
    all_rows = []
    for features in data_features:
        row = {}
        for template in templates:
            row[template] = tuple([features[key] for key in template])
        all_rows.append(row)

    return all_rows        
