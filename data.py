import sys

from nltk.parse.stanford import StanfordParser

from features import FeatureExtractionFail
from basic_struct import Context, Frame, NodePosition
from feature_extractor import FeatureExtractor
from tree_util import (collect_nodes, find_node_by_positions)
from ling_util import convert_brackets
from annotation import align_annotation_with_tree
        
parser=StanfordParser(
    path_to_jar = "/cs/fs/home/hxiao/code/stanford-parser-full-2015-01-30/stanford-parser.jar",
    path_to_models_jar = "/cs/fs/home/hxiao/code/stanford-parser-full-2015-01-30/stanford-parser-3.5.1-models.jar",
    model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz"
)

def make_training_data(feature_funcs, annotations):
    """
    Given the FrameNet annotations, return the training instances in terms of the tree nodes

    >>> from annotation import parse_fulltext
    >>> annotations = parse_fulltext("test_data/annotation.xml")
    >>> from features import DummyNodeFeature
    >>> instances = make_training_data([DummyNodeFeature], annotations)
    >>> len(instances) # 27 nodes times 2 annotations
    52
    >>> [i for i in instances if i[1] == 'Recipient'][0][0]
    {'node_dummy': ([u'to', u'Goodwill'], u'PP')}
    >>> [i for i in instances if i[1] == 'Donor'][0][0]
    {'node_dummy': ([u'Your'], u'PRP$')}
    >>> [i for i in instances if i[1] == 'Means'][0][0]
    {'node_dummy': ([u'Your', u'contribution', u'to', u'Goodwill'], u'NP')}
    >>> [i for i in instances if i[1] == 'Value'][0][0]
    {'node_dummy': ([u'more', u'than', u'you', u'may', u'know'], u'ADVP')}

    >>> from features import PathToFrame
    >>> annotations = parse_fulltext("test_data/annotation3.xml")
    >>> instances = make_training_data([PathToFrame], annotations)
    """
    extractor = FeatureExtractor(feature_funcs)
    
    training_instances = []
    
    for sent_str, anns in annotations:
        tree = parser.raw_parse(sent_str).next()
        tree = convert_brackets(tree)
        # print tree
        # some preprocessing, align the positions and 
        # also use the sentence string given the parse tree
        anns = align_annotation_with_tree(sent_str, tree, anns)
        sent_str = ' '.join(tree.leaves())
        for ann in anns:
            frame_name = ann.frame_name
            start, end = ann.target.start, ann.target.end
            frame = Frame(start, end, frame_name)
            frame_node = find_node_by_positions(tree, start, end)

            # TODO: bug here
            if frame_node is None: 
                sys.stderr.write("Warning: %r does not correspond to any tree node in sentence \"%s\"\nSkip it\n " %(frame, sent_str))
                continue
                
            for node, (node_start_pos, node_end_pos) in collect_nodes(tree):
                node_pos = NodePosition(node_start_pos, node_end_pos)
                context = Context(sent_str, tree, frame, node_pos)

                feature_values = extractor.extract(node, context)
                
                # try to see the it has some semantic role
                found_matching_node = False
                for fe in ann.FE:
                    other_node = find_node_by_positions(tree, fe.start, fe.end)
                    if node == other_node:
                        training_instances.append((feature_values, fe.name))
                        found_matching_node = True
                        break

                # semantic role => NULL
                if not found_matching_node:
                    training_instances.append((feature_values, 'NULL'))

    return training_instances

def main():
    from pathlib import Path
    try:
        import cPickle as pickle
    except ImportError:
        import pickle
    
    from annotation import parse_fulltext
    from features import ALL_FEATURES
    
    from feature_template import apply_templates
    from feature_selection import filter_by_frequency
    from feature_encoding import encode

    # Feature templates considered if heading by 1:
    # ----------------------------
    # Position + Voice
    # Path length + Clause layer
    # 1 Predicate + Path
    # Path + Position + Voice
    # Path + Position + Voice + Predicate
    # 1 Head word stem + Predicate
    # 1 Head word stem + Predicate + Path
    # 1 Head word stem + Phrase
    # Clause layer + Position + Predicate
    templates = [tuple([f.name]) for f in ALL_FEATURES] + \
                [('path_to_frame', 'frame'), ('head_stem', 'frame'), ('head_stem', 'frame', 'path_to_frame'), ('head_stem', 'phrase_type')]
    
    size = 1
    instances = []
    for i, p in enumerate(Path("/cs/fs2/home/hxiao/Downloads/fndata-1.5/fulltext/").glob("*.xml")):
        if i == size:
            break
        sys.stderr.write("Processing file: '%s'\n" %p.absolute())
        annotations = parse_fulltext(str(p.absolute()))
        instances += make_training_data(ALL_FEATURES, annotations)

    sys.stderr.write("Feature selection...\n")
    x, y = zip(*instances)
    x = apply_templates(x, templates)
    features = filter_by_frequency(x, 2)
    sys.stderr.write("Feature encoding...\n")
    x, feature_map = encode(x, features)
    
    sys.stderr.write("Dumping data...\n")    
    pickle.dump((x, y, ALL_FEATURES, templates, feature_map), open('dump/test_data.pkl', 'w'))
    import pdb
    pdb.set_trace()
    print len(instances)

if __name__ == "__main__":
    main()
