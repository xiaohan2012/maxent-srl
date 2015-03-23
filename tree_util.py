from nltk.tree import Tree

def collect_nodes(tree):
    """
    Collect all the nodes as well as thei char position ranges from the tree

    The root is ecluded

    >>> from nltk.tree import Tree
    >>> tree = Tree('ROOT', [Tree('S', [Tree('NP', [Tree('PRP', ['I'])]), Tree('VP', [Tree('VBP', ['love']), Tree('NP', [Tree('PRP', ['you'])])])])])
    >>> node_info = collect_nodes(tree)
    >>> nodes = [n for n,pos in node_info]
    >>> len(nodes)
    7
    >>> tree in nodes
    False
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
    >>> node_info
    [(Tree('PRP', ['I']), (0, 0)), (Tree('NP', [Tree('PRP', ['I'])]), (0, 0)), (Tree('VBP', ['love']), (2, 5)), (Tree('PRP', ['you']), (7, 9)), (Tree('NP', [Tree('PRP', ['you'])]), (7, 9)), (Tree('VP', [Tree('VBP', ['love']), Tree('NP', [Tree('PRP', ['you'])])]), (2, 9)), (Tree('S', [Tree('NP', [Tree('PRP', ['I'])]), Tree('VP', [Tree('VBP', ['love']), Tree('NP', [Tree('PRP', ['you'])])])]), (0, 9))]
    """
    assert isinstance(tree, Tree)
    def aux(subtree, acc, start):
        if isinstance(subtree, Tree):
            start_offset = start
            for i in xrange(len(subtree)):
                if isinstance(subtree[i], Tree):
                    length = len(' '.join(subtree[i].leaves()))
                else: # a string
                    length = len(subtree[i])
                aux(subtree[i], acc, start_offset)
                start_offset += (length+1) # one space
            acc.append((subtree, (start, start_offset-2)))
    nodes = []
    assert len(tree) == 1
    aux(tree[0], nodes, 0)
    return nodes

def find_node_by_positions(tree, start, end):
    """
    Given the start/end(inclusive) index of the text string(' '.join(tree.leaves())), find the corresponding node in the tree

    Time complexity: O(height of the tree)
    
    >>> from nltk.tree import Tree
    >>> tree = Tree('ROOT', [Tree('S', [Tree('NP', [Tree('NP', [Tree('PRP$', ['Your']), Tree('NN', ['contribution'])]), Tree('PP', [Tree('TO', ['to']), Tree('NP', [Tree('NNP', ['Goodwill'])])])]), Tree('VP', [Tree('MD', ['will']), Tree('VP', [Tree('VB', ['mean']), Tree('ADVP', [Tree('ADVP', [Tree('RBR', ['more'])]), Tree('SBAR', [Tree('IN', ['than']), Tree('S', [Tree('NP', [Tree('PRP', ['you'])]), Tree('VP', [Tree('MD', ['may']), Tree('VP', [Tree('VB', ['know'])])])])])])])]), Tree('.', ['.'])])])
    >>> find_node_by_positions(tree, 0, 3)
    Tree('PRP$', ['Your'])
    >>> print find_node_by_positions(tree, 0, 4)
    None
    >>> find_node_by_positions(tree, 40, 61) # more than you may know
    Tree('ADVP', [Tree('ADVP', [Tree('RBR', ['more'])]), Tree('SBAR', [Tree('IN', ['than']), Tree('S', [Tree('NP', [Tree('PRP', ['you'])]), Tree('VP', [Tree('MD', ['may']), Tree('VP', [Tree('VB', ['know'])])])])])])
    
    # more tests
    >>> tree = Tree('ROOT', [Tree('S', [Tree('NP', [Tree('DT', ['This'])]), Tree('VP', [Tree('VBZ', ['is']), Tree('NP', [Tree('NP', [Tree('DT', ['an']), Tree('NN', ['employment']), Tree('NN', ['contract'])]), Tree('PP', [Tree('IN', ['between']), Tree('NP', [Tree('NP', [Tree('NNP', ['AL']), Tree('NNP', ['QAEDA'])]), Tree('CC', ['and']), Tree('NP', [Tree('DT', ['a']), Tree('JJ', ['potential']), Tree('NN', ['recruit'])])])])])]), Tree('.', ['.'])])])
    >>> find_node_by_positions(tree, 22, 29)
    Tree('NN', ['contract'])
    """
    assert start >= 0 and start <= end, "Invalid range %r" %((start, end), )

    # Binary search for the target range
    tree = tree[0]# we don't consider the root
    offset = 0
    tree_word_length = lambda t: len(' '.join(t.leaves()))
    
    while True:
        if offset == start and start + tree_word_length(tree) - 1 == end:
            return tree
        else:
            found_range = False
            subtree_start = offset
            for subtree in tree:
                subtree_end = subtree_start + tree_word_length(subtree) - 1
                if start >= subtree_start and end <= subtree_end:
                    found_range = True
                    offset = subtree_start
                    tree = subtree
                    break
                else:
                    subtree_start = subtree_end + 2
                    tree = subtree
            if not found_range:
                # the target range lies in the intersection between the two subtrees
                return None

    
