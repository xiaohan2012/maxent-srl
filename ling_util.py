"""
Linguistic utility functions
"""

rules = {
    'ADJP': ('right',  set(('%', 'QP', 'JJ', 'VBN', 'VBG', 'ADJP', '$', 'JJR', 'JJS', 'DT', 'FW', '****', 'RBR', 'RBS', 'RB',))),
    'ADVP': ('left', set(('RBR', 'RB', 'RBS', 'FW', 'ADVP', 'CD', '****', 'JJR', 'JJS', 'JJ',))),
    'CONJP': ('left', set(('CC', 'RB', 'IN',))),
    'FRAG': ('left', set(('**',))),
    'INTJ': ('right',  set(('**',))),
    'LST': ('left', set(('LS', ))),
    'NAC': ('right',  set(('NN', 'NNS', 'NNP', 'NNPS', 'NP', 'NAC', 'EX', '$', 'CD', 'QP', 'PRP', 'VBG', 'JJ', 'JJS', 'JJR', 'ADJP', 'FW',))),
    'NP': ('right',  set(('EX', '$', 'CD', 'QP', 'PRP', 'VBG', 'JJ', 'JJS', 'JJR', 'ADJP', 'DT', 'FW', 'RB', 'SYM', 'PRP$',))),
    'NP$': ('right', set(('NN', 'NNS', 'NNP', 'NNPS', 'NP', 'NAC', 'EX', '$', 'CD', 'QP', 'PRP', 'VBG', 'JJ', 'JJS', 'JJR', 'ADJP', 'FW', 'SYM',))),
    'PNP': ('right',  set(('**',))),
    'PP': ('left', set(('IN', 'TO', 'FW',))),
    'PRN': ('left', set(('**',))),
    'PRT': ('left', set(('RP',))),
    'QP': ('right',  set(('CD', 'NCD', '%', 'QP', 'JJ', 'JJR', 'JJS', 'DT',))),
    'RRC': ('left', set(('VP', 'NP', 'ADVP', 'ADJP', 'PP',))),
    'S': ('right',  set(('VP', 'SBAR', 'ADJP', 'UCP', 'NP',))),
    'SBAR': ('right',  set(('S', 'SQ', 'SINV', 'SBAR', 'FRAG', 'X',))),
    'SBARQ': ('right',  set(('SQ', 'S', 'SINV', 'SBARQ', 'FRAG', 'X',))),
    'SINV': ('right',  set(('S', 'VP', 'VBZ', 'VBD', 'VBP', 'VB', 'SINV', 'ADJP', 'NP',))),
    'SQ': ('right',  set(('VP', 'VBZ', 'VBD', 'VBP', 'VB', 'MD', 'SQ',))),
    'UCP': ('left', set(('**',))),
    'VP': ('left', set(('VBD', 'VBN', 'MD', 'VBZ', 'TO', 'VB', 'VP', 'VBG', 'VBP', 'ADJP', 'NP',))),
    'WHADJP': ('right',  set(('JJ', 'ADJP',))),
    'WHADVP': ('left', set(('WRB',))),
    'WHNP': ('right',  set(('WDT', 'WP', 'WP$', 'WHADJP', 'WHPP', 'WHNP',))),
    'WHPP': ('left', set(('IN', 'TO', 'FW',))),
    'X': ('left', set(('**',))),
}

def get_head_word(node, sensitive = True):
    """
    if `sensitive` is set to True, then node without any head word will not be reported as Exception
    Reference:
    - http://people.csail.mit.edu/mcollins/papers/heads       (method one)
    
    >>> from nltk.tree import Tree
    >>> tree = Tree('ROOT', [Tree('S', [Tree('NP', [Tree('NP', [Tree('PRP$', ['Your']), Tree('NN', ['contribution'])]), Tree('PP', [Tree('TO', ['to']), Tree('NP', [Tree('NNP', ['Goodwill'])])])]), Tree('VP', [Tree('MD', ['will']), Tree('VP', [Tree('VB', ['mean']), Tree('ADVP', [Tree('ADVP', [Tree('RBR', ['more'])]), Tree('SBAR', [Tree('IN', ['than']), Tree('S', [Tree('NP', [Tree('PRP', ['you'])]), Tree('VP', [Tree('MD', ['may']), Tree('VP', [Tree('VB', ['know'])])])])])])])]), Tree('.', ['.'])])])
    >>> node = tree[0][0][1][1][0]
    >>> get_head_word(node)
    'Goodwill'
    >>> get_head_word(tree[0][0][0])
    'contribution'
    >>> get_head_word(tree[0][1][1])
    'mean'
    >>> get_head_word(tree[0])
    'will'
    >>> get_head_word(tree[0][1][1][1][1])
    'may'
    >>> get_head_word(tree) # doctest: +IGNORE_EXCEPTION_DETAIL    
    Traceback (most recent call last):
    KeyError: "No rule for label...
    >>> print get_head_word(tree, sensitive = False)
    None
    """
    if len(node) == 1 and isinstance(node[0], basestring):
        return node[0]
    else:
        if node.label().startswith('N'):    # NN is different
            # NNP does not exist?
            if node[-1].label().startswith('N'):
                return get_head_word(node[-1])
        label = node.label()
        if label in rules:
            rule = rules[label]
            direction = rule[0]
            label_values = rule[1]
            if direction == 'left': #from left to right
                iters = node
            else:
                iters = node[::-1]
            
            for child in iters:
                if child.label() in label_values:
                    return get_head_word(child)
        else:
            if sensitive:
                raise KeyError("No rule for label '%s'" %(label))
            else:
                return None
        raise ValueError("No head word for %r" %(node))
