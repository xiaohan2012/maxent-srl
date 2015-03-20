import sys
from collections import namedtuple
from nltk.parse.stanford import StanfordParser

from feature_extractor import FeatureExtractor
from tree_util import (collect_nodes, find_node_by_positions)

Frame = namedtuple('Frame', ['start', 'end', 'name'])
NodePosition = namedtuple('NodePosition', ['start', 'end'])

class Context(object):
    def __init__(self, sentence, parse_tree, frame, node_pos):
        self.sentence =  sentence
        self.parse_tree = parse_tree
        self.frame = frame
        self.node_pos = node_pos
        
parser=StanfordParser(
    path_to_jar = "/cs/fs/home/hxiao/code/stanford-parser-full-2015-01-30/stanford-parser.jar",
    path_to_models_jar = "/cs/fs/home/hxiao/code/stanford-parser-full-2015-01-30/stanford-parser-3.5.1-models.jar",
    model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz"
)

def make_training_data(feature_funcs, annotations):
    """
    Given the FrameNet annotations, return the training instances in terms of the tree nodes

    >>> from annotation import parse_fulltext
    >>> annotations = parse_fulltext("test_data/annotation1.xml")
    >>> from features import DummyNodeFeature
    >>> instances = make_training_data([DummyNodeFeature], annotations)
    >>> len(instances) # 27 nodes times 2 annotations
    54
    >>> [i for i in instances if i[1] == 'Recipient'][0][0]
    {'node_dummy': ([u'to', u'Goodwill'], u'PP')}
    >>> [i for i in instances if i[1] == 'Donor'][0][0]
    {'node_dummy': ([u'Your'], u'PRP$')}
    >>> [i for i in instances if i[1] == 'Means'][0][0]
    {'node_dummy': ([u'Your', u'contribution', u'to', u'Goodwill'], u'NP')}
    >>> [i for i in instances if i[1] == 'Value'][0][0]
    {'node_dummy': ([u'more', u'than', u'you', u'may', u'know'], u'ADVP')}
    """
    extractor = FeatureExtractor(feature_funcs)
    
    training_instances = []
    
    for sent_str, anns in annotations:
        tree = parser.raw_parse(sent_str).next()
        for ann in anns:
            frame_name = ann.frame_name
            start, end = ann.target.start, ann.target.end
            frame = Frame(start, end, frame_name)
            frame_node = find_node_by_positions(tree, start, end)

            # NOT TESTED
            if frame_node is None: 
                sys.stderr.write("Warning: %r does not correspond to node in tree %r" %(frame, tree))
                
            for node, (node_start_pos, node_end_pos) in collect_nodes(tree):
                node_pos = NodePosition(node_start_pos, node_end_pos)
                context = Context(sent_str, tree, frame, node_pos)
                feature_values = extractor.extract(node, context)

                # try to see the it has some semantic role
                found_matching_node = False
                for fe in ann.FE:
                    start, end = fe.start, fe.end
                    other_node = find_node_by_positions(tree, start, end)
                    if node == other_node:
                        training_instances.append((feature_values, fe.name))
                        found_matching_node = True
                        break

                # semantic role => NULL
                if not found_matching_node:
                    training_instances.append((feature_values, 'NULL'))

    return training_instances
