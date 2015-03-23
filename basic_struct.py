from collections import namedtuple
Frame = namedtuple('Frame', ['start', 'end', 'name'])

NodePosition = namedtuple('NodePosition', ['start', 'end'])

class Context(object):
    def __init__(self, sentence, parse_tree, frame, node_pos):
        self.sentence =  sentence
        self.parse_tree = parse_tree
        self.frame = frame
        self.node_pos = node_pos
