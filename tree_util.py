from nltk.tree import Tree

def collect_nodes(tree):
    """
    collect all the nodes from the tree

    >>> from nltk.tree import Tree
    >>> tree = Tree('ROOT', [Tree('S', [Tree('NP', [Tree('PRP', ['I'])]), Tree('VP', [Tree('VBP', ['love']), Tree('NP', [Tree('PRP', ['you'])])])])])
    >>> nodes = collect_nodes(tree)
    >>> len(nodes)
    8
    >>> tree in nodes
    True
    >>> tree[0] in nodes
    True
    >>> tree[0][1]
    Tree('VP', [Tree('VBP', ['love']), Tree('NP', [Tree('PRP', ['you'])])])
    >>> tree[0][1] in nodes
    True
    >>> tree[0][0]
    Tree('NP', [Tree('PRP', ['I'])])
    >>> tree[0][0] in nodes
    True
    >>> 'I' in nodes
    False
    """
    assert isinstance(tree, Tree)
    def aux(subtree, acc):
        if isinstance(subtree, Tree):
            acc.append(subtree)
            for i in xrange(len(subtree)):
                aux(subtree[i], acc)

    nodes = []
    aux(tree, nodes)
    return nodes


def find_node_by_positions(tree, start, end):
    """
    Given the start/end(inclusive) index of the text string, find the corresponding node in the tree

    Time complexity: O(height of the tree)
    
    >>> from nltk.tree import Tree
    >>> tree = Tree('ROOT', [Tree('S', [Tree('NP', [Tree('NP', [Tree('PRP$', ['Your']), Tree('NN', ['contribution'])]), Tree('PP', [Tree('TO', ['to']), Tree('NP', [Tree('NNP', ['Goodwill'])])])]), Tree('VP', [Tree('MD', ['will']), Tree('VP', [Tree('VB', ['mean']), Tree('ADVP', [Tree('ADVP', [Tree('RBR', ['more'])]), Tree('SBAR', [Tree('IN', ['than']), Tree('S', [Tree('NP', [Tree('PRP', ['you'])]), Tree('VP', [Tree('MD', ['may']), Tree('VP', [Tree('VB', ['know'])])])])])])])]), Tree('.', ['.'])])])
    >>> find_node_by_positions(tree, 0, 3)
    Tree('PRP$', ['Your'])
    >>> print find_node_by_positions(tree, 0, 4)
    None
    >>> find_node_by_positions(tree, 40, 61) # more than you may know
    Tree('ADVP', [Tree('ADVP', [Tree('RBR', ['more'])]), Tree('SBAR', [Tree('IN', ['than']), Tree('S', [Tree('NP', [Tree('PRP', ['you'])]), Tree('VP', [Tree('MD', ['may']), Tree('VP', [Tree('VB', ['know'])])])])])])
    """
    assert start >= 0 and start <= end, "Invalid range"
    end = end+1 # because of Python slicing rules(exclusive)

    # Binary search for the target range
    tree = tree[0]# we don't consider the root
    offset = 0
    tree_word_length = lambda t: len(' '.join(t.leaves()))
    
    while True:
        if offset == start and start + tree_word_length(tree) == end:
            return tree
        else:
            left_tree, right_tree = tree[0], tree[1]
            left_range_start, left_range_end = offset, offset + tree_word_length(left_tree)
            right_range_start, right_range_end = left_range_end + 1, left_range_end + 1 + tree_word_length(right_tree)

            if start >= left_range_start and end <= left_range_end:
                tree = left_tree
            elif start >= right_range_start and end <= right_range_end:
                tree = right_tree
                offset = right_range_start
            else:
                # the target range lies in the intersection between the two subtrees
                return None
