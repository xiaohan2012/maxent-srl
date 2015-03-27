import sys
import networkx as nx
from collections import Counter
from pathlib import Path
import cPickle as pickle
from annotation import align_annotation_with_sentence
from ling_util import convert_bracket_for_token

class DependencyTree(object):
    """
    Data wrapper for dependency tree in format of graph as well as the edge to label mapping

    >>> from dependency_output_parser import parse_output
    >>> o = parse_output(open('test_data/depparse_output1.out'))[0]
    >>> t = to_graph(o.nodes, o.edges)
    >>> t.get_node('Objectives', 1)
    Objectives(NNS)-1
    >>> len(t.tokens())
    25
    >>> t.tokens()
    ['Objectives', 'of', 'AL', 'QAEDA', ':', 'Support', 'God', "'s", 'religion', ',', 'establishment', 'of', 'Islamic', 'rule', ',', 'and', 'restoration', 'of', 'the', 'Islamic', 'Caliphate', ',', 'God', 'willing', '.']
    """
    def __init__(self, g, e2l, all_nodes):
        self.g = g
        self.e2l = e2l
        self.all_nodes = all_nodes
        self.wp2node = {(convert_bracket_for_token(n.token), n.index): n
                        for n in all_nodes}
    def get_node(self, token, index):
        return self.wp2node[(token, index)]

    def tokens(self):
        tokens = [convert_bracket_for_token(n.token) for n in self.all_nodes]
        if tokens[0] == 'ROOT':
            return tokens[1:]
        else:
            return tokens

def to_graph(nodes, edges):
    """
    Convert the dependency tree in format of nodes and eedges to a networkx directed graph
    as well as the edge to label mapping(as networkx graph cannot handle edge label)
    
    >>> from dependency_output_parser import parse_output
    >>> o = parse_output(open('test_data/depparse_output1.out'))[0]
    >>> t = to_graph(o.nodes, o.edges)
    >>> len(t.g.nodes()) # preposition words such as in, of are omitted
    21
    >>> t.g.nodes()
    [QAEDA(NNP)-4, AL(NNP)-3, Islamic(JJ)-13, rule(NN)-14, Caliphate(NN)-21, the(DT)-19, :(:)-5, .(.)-25, restoration(NN)-17, ,(,)-22, Support(NN)-6, God(NNP)-7, ,(,)-15, ,(,)-10, establishment(NN)-11, religion(NN)-9, ROOT-0, God(NNP)-23, Objectives(NNS)-1, Islamic(JJ)-20, willing(JJ)-24]
    >>> len(t.g.edges())
    20
    >>> t.g.edges()
    [(QAEDA(NNP)-4, AL(NNP)-3), (rule(NN)-14, Islamic(JJ)-13), (Caliphate(NN)-21, the(DT)-19), (Caliphate(NN)-21, Islamic(JJ)-20), (restoration(NN)-17, Caliphate(NN)-21), (God(NNP)-7, Support(NN)-6), (establishment(NN)-11, rule(NN)-14), (religion(NN)-9, restoration(NN)-17), (religion(NN)-9, God(NNP)-23), (religion(NN)-9, ,(,)-22), (religion(NN)-9, God(NNP)-7), (religion(NN)-9, ,(,)-15), (religion(NN)-9, ,(,)-10), (religion(NN)-9, establishment(NN)-11), (ROOT-0, Objectives(NNS)-1), (God(NNP)-23, willing(JJ)-24), (Objectives(NNS)-1, QAEDA(NNP)-4), (Objectives(NNS)-1, :(:)-5), (Objectives(NNS)-1, .(.)-25), (Objectives(NNS)-1, religion(NN)-9)]
    >>> t.e2l    
    {(QAEDA(NNP)-4, AL(NNP)-3): 'nn', (Objectives(NNS)-1, QAEDA(NNP)-4): 'prep_of', (religion(NN)-9, ,(,)-15): 'punct', (religion(NN)-9, restoration(NN)-17): 'conj_and', (religion(NN)-9, God(NNP)-7): 'poss', (restoration(NN)-17, Caliphate(NN)-21): 'prep_of', (Objectives(NNS)-1, .(.)-25): 'punct', (establishment(NN)-11, rule(NN)-14): 'prep_of', (God(NNP)-23, willing(JJ)-24): 'amod', (Objectives(NNS)-1, religion(NN)-9): 'dep', (Caliphate(NN)-21, Islamic(JJ)-20): 'amod', (ROOT-0, Objectives(NNS)-1): 'root', (religion(NN)-9, ,(,)-22): 'punct', (religion(NN)-9, God(NNP)-23): 'appos', (religion(NN)-9, establishment(NN)-11): 'conj_and', (rule(NN)-14, Islamic(JJ)-13): 'amod', (religion(NN)-9, ,(,)-10): 'punct', (God(NNP)-7, Support(NN)-6): 'nn', (Objectives(NNS)-1, :(:)-5): 'punct', (Caliphate(NN)-21, the(DT)-19): 'det'}
    """
    g = nx.DiGraph()
    
    e2l = {}
    for f, t, l in edges:
        g.add_edge(f, t)
        e2l[(f,t)] = l
    return DependencyTree(g, e2l, nodes)

def get_path(t, src, dest):
    """
    Get the path from src to dest in dependency parse tree
    
    >>> from dependency_output_parser import (parse_output, Node)
    >>> o = parse_output(open('test_data/depparse_output1.out'))[0]
    >>> t = to_graph(o.nodes, o.edges)
    >>> objective = Node('Objectives', 1, 'NNS')
    >>> the = Node('the', 19, 'DT')
    >>> get_path(t, objective, the)
    ('dep', 'conj_and', 'prep_of', 'det')
    >>> print get_path(t, the, objective)
    None
    >>> print get_path(t, the, Node('random_node', 10001, 'WQR'))
    None
    """
    nodes = t.g.nodes()
    if src not in nodes or dest not in nodes:
        return None

    try:
        path = nx.shortest_path(t.g, src, dest)
    except nx.NetworkXNoPath:
        return None

    labels = []
    for i in xrange(len(path)-1):    
        labels.append(t.e2l[(path[i], path[i+1])])
    return tuple(labels)

def get_word_indices_by_char_index_range(words, start, end):
    """
    >>> words = ['I', 'love', 'you']
    >>> get_word_indices_by_char_index_range(words, 0, 0)
    [1]
    >>> get_word_indices_by_char_index_range(words, 2, 5)
    [2]
    >>> get_word_indices_by_char_index_range(words, 7, 9)
    [3]
    >>> get_word_indices_by_char_index_range(words, 2, 9)
    [2, 3]
    >>> get_word_indices_by_char_index_range(words, 5, 9) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: Invalid range (5, 9)
    >>> get_word_indices_by_char_index_range(words, 3, 7) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: Invalid range (3, 7)
    """
    inds = []
    cur = 0
    start_match = False
    for i, w in enumerate(words):
        if cur == start and cur + len(w) - 1 <= end:
            inds.append(i+1) # first one is root, so starts with 1
            start_match = True
        elif start_match and cur + len(w) - 1 <= end:
            inds.append(i+1)

        if len(inds) > 0 and cur + len(w) - 1 == end:
            return inds
        elif cur + len(w) - 1 > end:
            raise ValueError('Invalid range %r' %((start, end),))
        cur += len(w)+1
    if not start_match:
        raise ValueError('Invalid range %r' %((start, end),))
    
def get_tree_nodes_from_char_range(t, start, end):
    """get the nodes according to the specified character start and end positions in the sentence
    
    >>> from dependency_output_parser import parse_output
    >>> o = parse_output(open('test_data/depparse_output1.out'))[0]
    >>> t = to_graph(o.nodes, o.edges)
    >>> get_tree_nodes_from_char_range(t, 0, 9)
    (Objectives(NNS)-1,)
    >>> get_tree_nodes_from_char_range(t, 11, 23)
    (of(IN)-2, AL(NNP)-3, QAEDA(NNP)-4, :(:)-5)
    >>> get_tree_nodes_from_char_range(t, 12, 13) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: Invalid range (12, 13)
    """
    frame_str = ' '.join(t.tokens())[start: end+1]
    inds = get_word_indices_by_char_index_range(t.tokens(), start, end)
    return tuple([t.get_node(s, ind) for s, ind in zip(frame_str.split(), inds)])


def get_annotation_nodes(aligned_annotations, t):
    """
    return the tree nodes from frames and arguments
    
    >>> from annotation import (parse_fulltext, align_annotation_with_sentence)
    >>> from dependency_output_parser import parse_output
    >>> sent_str, annotations = parse_fulltext('test_data/annotation3.xml')[0]
    >>> o = parse_output(open('test_data/depparse_output1.out'))[0]
    >>> t = to_graph(o.nodes, o.edges)
    >>> new_sent = ' '.join(t.tokens())
    >>> aligned_annotations = align_annotation_with_sentence(sent_str, new_sent, annotations)
    >>> nodes_pairs = get_annotation_nodes(aligned_annotations, t)
    >>> len(nodes_pairs)
    5
    >>> nodes_pairs
    [[(Objectives(NNS)-1,), [(of(IN)-2, AL(NNP)-3, QAEDA(NNP)-4, :(:)-5)]], [(Support(NN)-6,), [(God(NNP)-7, 's(POS)-8, religion(NN)-9), (God(NNP)-7,)]], [(establishment(NN)-11,), [(of(IN)-12, Islamic(JJ)-13, rule(NN)-14)]], [(rule(NN)-14,), [(Islamic(JJ)-13,)]], [(willing(JJ)-24,), [(God(NNP)-23,)]]]
    """
    result = []
    for ann in aligned_annotations:
        frame_data = []
        start, end = ann.target
        frame_data.append(get_tree_nodes_from_char_range(t, start, end))
        args = []
        for arg in ann.FE:
            start, end = arg.start, arg.end
            args.append(get_tree_nodes_from_char_range(t, start, end))
        frame_data.append(args)
        result.append(frame_data)
    return result

def count_path_from_nodes_pairs(t, nodes_pairs):
    """
    Given the tree and (frame_nodes, annotation nodes), count the paths from frame_nodes to annotation nodes
    >>> from pickle import load
    >>> t = load(open('test_data/tree.pkl', 'r'))
    >>> nodes_pairs = load(open('test_data/nodes_pairs.pkl', 'r'))
    >>> count_path_from_nodes_pairs(t, nodes_pairs[:1])
    Counter({('prep_of', 'nn'): 1, ('prep_of',): 1, ('punct',): 1})
    >>> count_path_from_nodes_pairs(t, nodes_pairs[:2])
    Counter({('prep_of', 'nn'): 1, ('prep_of',): 1, ('punct',): 1})
    >>> count_path_from_nodes_pairs(t, nodes_pairs[:3])
    Counter({('prep_of',): 2, ('prep_of', 'nn'): 1, ('prep_of', 'amod'): 1, ('punct',): 1})
    >>> count_path_from_nodes_pairs(t, nodes_pairs[:5])
    Counter({('prep_of',): 2, ('amod',): 1, ('prep_of', 'nn'): 1, ('prep_of', 'amod'): 1, ('punct',): 1})
    """
    c = Counter()
    for frame_nodes, ann_nodes in nodes_pairs:
        for fn in frame_nodes:
            flattend_nodes = []
            for nodes in ann_nodes: # flatten 2d list
                if len(nodes) == 1: #iterate tuple(size 1) is non-sense
                    flattend_nodes.append(nodes[0])
                else:
                    flattend_nodes += [n for n in nodes]

            for an in flattend_nodes:
                path = get_path(t, fn, an)
                if path:
                    c[path] += 1

    return c

def path_freq(data_dir):
    """
    Collect the path frequency from the data under directory `data_dir`

    >>> path_freq('test_data/parse_and_annotations/')
    Counter({(u'dobj',): 1, (u'prep_of',): 1})
    """
    from annotation import (parse_fulltext, align_annotation_with_sentence)
    from dependency_output_parser import parse_output
    
    path_freq = Counter()
    # load the sentences

    sents = {}
    for sent_path in Path(data_dir).glob('*.txt'):
        sent_str = sent_path.open(encoding='utf8').read().strip()
        sents[sent_path.stem] = sent_str

    # load and parse the annotations 
    depparses = {}
    for parse_path in Path(data_dir).glob('*.txt.out'):
        sent_id = parse_path.stem.split('.')[0]
        o = parse_output(parse_path.open(encoding='utf8'))
        if len(o) > 1:
            sys.stderr.write('Dropping sentence %s as it contains more than one sentences\n' %(parse_path))
            del sents[sent_id]
            continue
        tree = to_graph(o[0].nodes, o[0].edges)
        depparses[sent_id] = tree

    assert set(sents.keys()) == set(depparses.keys())
    
    # collect the path frequency
    for ann_path in Path(data_dir).glob('*.ann'):
        ann = pickle.load(ann_path.open('r'))
        if ann.sent_id not in sents:
            sys.stderr.write('Dropping annotation %s as it contains more than one sentences\n' %(ann.id))
            continue
        sent = sents[ann.sent_id]
        t = depparses[ann.sent_id]
        
        new_sent = ' '.join(t.tokens())
        aligned_annotations = align_annotation_with_sentence(sent, new_sent, [ann])
        nodes_pairs = get_annotation_nodes(aligned_annotations, t)
        path_freq += count_path_from_nodes_pairs(t, nodes_pairs)

    return path_freq

if __name__ == "__main__":
    freq = path_freq('data/frame_identification')
    import pdb
    pdb.set_trace()

