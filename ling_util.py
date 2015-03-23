"""
Linguistic utility functions
"""
from nltk.tree import Tree
\
rules = {
    'ADJP': ('right',  set(('%', 'QP', 'JJ', 'VBN', 'VBG', 'ADJP', '$', 'JJR', 'JJS', 'DT', 'FW', '****', 'RBR', 'RBS', 'RB',))),
    'ADVP': ('left', set(('RBR', 'RB', 'RBS', 'FW', 'ADVP', 'CD', '****', 'JJR', 'JJS', 'JJ',))),
    'CONJP': ('left', set(('CC', 'RB', 'IN',))),
    'FRAG': ('left', '**'),
    'INTJ': ('right', '**'),
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

def get_head_word(node):
    """
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
    >>> tree = Tree('NP', [Tree('NP', [Tree('DT', ['an']), Tree('NN', ['employment']), Tree('NN', ['contract'])]), Tree('PP', [Tree('IN', ['between']), Tree('NP', [Tree('NP', [Tree('NNP', ['AL']), Tree('NNP', ['QAEDA'])]), Tree('CC', ['and']), Tree('NP', [Tree('DT', ['a']), Tree('JJ', ['potential']), Tree('NN', ['recruit'])])])])]) # no specific rule case
    >>> get_head_word(tree)
    'between'

    # test for ** cases
    >>> tree = Tree('ROOT', [Tree('FRAG', [Tree('PP', [Tree('IN', ['In']), Tree('NP', [Tree('NP', [Tree('DT', ['the']), Tree('NN', ['name'])]), Tree('PP', [Tree('IN', ['of']), Tree('NP', [Tree('NP', [Tree('NNP', ['Allah'])]), Tree(',', [',']), Tree('NP', [Tree('JJS', ['Most']), Tree('NNS', ['Gracious'])]), Tree(',', [','])])])])]), Tree('NP', [Tree('NP', [Tree('JJS', ['Most'])]), Tree('NP', [Tree('NP', [Tree('NNP', ['Merciful']), Tree('.', ['.'])]), Tree('PRN', [Tree('-LRB-', ['-LRB-']), Tree('NP', [Tree('NP', [Tree('NNP', ['T.C'])]), Tree(':', [':']), Tree('NP', [Tree('NP', [Tree('NN', ['verse'])]), Tree('PP', [Tree('IN', ['from']), Tree('NP', [Tree('DT', ['the']), Tree('NNP', ['Koran'])])])])]), Tree('-RRB-', ['-RRB-'])])])])])])
    >>> get_head_word(tree[0])
    'In'
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
            if label_values == "**":
                return get_head_word(iters[0])
            else:
                for child in iters:
                    if child.label() in label_values:
                        return get_head_word(child)

            #not found, use the one by `direction`
            if direction == 'left':
                return get_head_word(node[0])
            else:
                return get_head_word(node[-1])



mapping = dict(zip('-LRB- -RRB- -RSB- -RSB- -LCB- -RCB-'.split(), '( ) [ ] { }'.split()))

def convert_brackets(tree):
    """convert the bracket notation back to the original

    >>> t = Tree('FRAG', [Tree('PP', [Tree('IN', ['In']), Tree('NP', [Tree('NP', [Tree('DT', ['the']), Tree('NN', ['name'])]), Tree('PP', [Tree('IN', ['of']), Tree('NP', [Tree('NP', [Tree('NNP', ['Allah'])]), Tree(',', [',']), Tree('NP', [Tree('JJS', ['Most']), Tree('NNS', ['Gracious'])]), Tree(',', [','])])])])]), Tree('NP', [Tree('NP', [Tree('JJS', ['Most'])]), Tree('NP', [Tree('NP', [Tree('NNP', ['Merciful']), Tree('.', ['.'])]), Tree('PRN', [Tree('-LRB-', ['-LRB-']), Tree('NP', [Tree('NP', [Tree('NNP', ['T.C'])]), Tree(':', [':']), Tree('NP', [Tree('NP', [Tree('NN', ['verse'])]), Tree('PP', [Tree('IN', ['from']), Tree('NP', [Tree('DT', ['the']), Tree('NNP', ['Koran'])])])])]), Tree('-RRB-', ['-RRB-'])])])])])
    >>> convert_brackets(t)
    Tree('FRAG', [Tree('PP', [Tree('IN', ['In']), Tree('NP', [Tree('NP', [Tree('DT', ['the']), Tree('NN', ['name'])]), Tree('PP', [Tree('IN', ['of']), Tree('NP', [Tree('NP', [Tree('NNP', ['Allah'])]), Tree(',', [',']), Tree('NP', [Tree('JJS', ['Most']), Tree('NNS', ['Gracious'])]), Tree(',', [','])])])])]), Tree('NP', [Tree('NP', [Tree('JJS', ['Most'])]), Tree('NP', [Tree('NP', [Tree('NNP', ['Merciful']), Tree('.', ['.'])]), Tree('PRN', [Tree('-LRB-', ['(']), Tree('NP', [Tree('NP', [Tree('NNP', ['T.C'])]), Tree(':', [':']), Tree('NP', [Tree('NP', [Tree('NN', ['verse'])]), Tree('PP', [Tree('IN', ['from']), Tree('NP', [Tree('DT', ['the']), Tree('NNP', ['Koran'])])])])]), Tree('-RRB-', [')'])])])])])
    """
    def aux(t):
        if isinstance(t, basestring):
            if t in mapping:
                return mapping[t]
            else:
                return t
        else:
            return Tree(t.label(), [convert_brackets(subtree) for subtree in t])
            
    return aux(tree)
