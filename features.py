from nltk.stem import PorterStemmer

from ling_util import get_head_word


class FeatureExtractionFail(Exception):
    pass

class Feature(object):
    @classmethod
    def get_value(cls, unit, context):
        raise NotImplementedError

class Position(Feature):
    """
    >>> from nltk.tree import Tree
    >>> from basic_struct import (Frame, NodePosition, Context)
    >>> tree = Tree('ROOT', [Tree('S', [Tree('NP', [Tree('NP', [Tree('PRP$', ['Your']), Tree('NN', ['contribution'])]), Tree('PP', [Tree('TO', ['to']), Tree('NP', [Tree('NNP', ['Goodwill'])])])]), Tree('VP', [Tree('MD', ['will']), Tree('VP', [Tree('VB', ['mean']), Tree('ADVP', [Tree('ADVP', [Tree('RBR', ['more'])]), Tree('SBAR', [Tree('IN', ['than']), Tree('S', [Tree('NP', [Tree('PRP', ['you'])]), Tree('VP', [Tree('MD', ['may']), Tree('VP', [Tree('VB', ['know'])])])])])])])]), Tree('.', ['.'])])])
    >>> sent = u'Your contribution to Goodwill will mean more than you may know .'
    >>> Position.get_value(tree[0][0][0][0], Context(sent, tree, Frame(start=5, end=16, name='Giving'), NodePosition(0, 3)))
    'strict-before'
    >>> Position.get_value(tree[0][1][0], Context(sent, tree, Frame(start=5, end=16, name='Giving'), NodePosition(18, 19)))
    'strict-after'
    >>> Position.get_value(tree[0][0][0][1], Context(sent, tree, Frame(start=5, end=16, name='Giving'), NodePosition(5, 16)))
    'in'
    >>> Position.get_value(tree[0][0], Context(sent, tree, Frame(start=21, end=33, name='FakeStuff'), NodePosition(0, 28)))
    'overlap-before'
    >>> Position.get_value(tree[0][1], Context(sent, tree, Frame(start=21, end=33, name='FakeStuff'), NodePosition(28, 37)))
    'overlap-after'
    """
    name = "pos_to_frame"
    
    @classmethod
    def get_value(cls, u, c):
        if c.node_pos.end < c.frame.start:
            return 'strict-before'
        elif c.node_pos.start > c.frame.end:
            return 'strict-after'
        elif c.node_pos.start >= c.frame.start and c.node_pos.end <= c.frame.end:
            return 'in'
        elif c.node_pos.end > c.frame.start and c.node_pos.start < c.frame.start:
            return 'overlap-before'
        elif c.node_pos.start < c.frame.end and c.node_pos.end > c.frame.end:
            return 'overlap-after'
        else:
            raise ValueError('Invalid position in case of  %r and %r' %(c.node_pos, c.frame))

class PathToFrame(Feature):
    """
    >>> from nltk.tree import Tree
    >>> from basic_struct import (Frame, NodePosition, Context)
    >>> tree = Tree('ROOT', [Tree('S', [Tree('NP', [Tree('NP', [Tree('PRP$', ['Your']), Tree('NN', ['contribution'])]), Tree('PP', [Tree('TO', ['to']), Tree('NP', [Tree('NNP', ['Goodwill'])])])]), Tree('VP', [Tree('MD', ['will']), Tree('VP', [Tree('VB', ['mean']), Tree('ADVP', [Tree('ADVP', [Tree('RBR', ['more'])]), Tree('SBAR', [Tree('IN', ['than']), Tree('S', [Tree('NP', [Tree('PRP', ['you'])]), Tree('VP', [Tree('MD', ['may']), Tree('VP', [Tree('VB', ['know'])])])])])])])]), Tree('.', ['.'])])])
    >>> sent = u'Your contribution to Goodwill will mean more than you may know .'
    >>> PathToFrame.get_value(tree[0][0][0][0], Context(sent, tree, Frame(start=5, end=16, name='Giving'), NodePosition(0, 3))) # your
    ('PRP$', 'u', 'NP', 'd', 'NN')
    >>> PathToFrame.get_value(tree[0][1][0], Context(sent, tree, Frame(start=5, end=16, name='Giving'), NodePosition(18, 19))) # to
    ('TO', 'u', 'PP', 'u', 'NP', 'd', 'NP', 'd', 'NN')
    >>> PathToFrame.get_value(tree[0][0][0][1], Context(sent, tree, Frame(start=5, end=16, name='Giving'), NodePosition(35, 38))) #mean
    ('VB', 'u', 'VP', 'u', 'VP', 'u', 'S', 'd', 'NP', 'd', 'NP', 'd', 'NN')
    >>> PathToFrame.get_value(tree[0][0][0][0], Context(sent, tree, Frame(start=0, end=3, name=''), NodePosition(0, 3))) # frame is node
    ('PRP$',)
    >>> PathToFrame.get_value(tree[0][0][0][0], Context(sent, tree, Frame(start=0, end=28, name=''), NodePosition(0, 3))) # frame is the parent
    ('PRP$', 'u', 'NP', 'u', 'NP')
    >>> PathToFrame.get_value(tree[0][0], Context(sent, tree, Frame(start=0, end=3, name=''), NodePosition(0, 28))) # node is the parent
    ('NP', 'd', 'NP', 'd', 'PRP$')
    """
    name = 'path_to_frame'

    @classmethod
    def get_word_index_range(cls, sent, char_start, char_end):
        """Given the char start/end index, return the corresponding word start/end index"""
        cur = 0
        start, end = None, None
        for i, w in enumerate(sent.split()):
            if cur == char_start:
                start = i
            if (cur+len(w)-1) == char_end:
                end = i+1
                break
            cur += (len(w)+1)

        if start == None or end == None:
            raise FeatureExtractionFail('Cannot extract the path at %r for "%s"' %((char_start, char_end), sent))
        return start, end
    
    @classmethod
    def get_value(cls, u, c):
        # print u, c.node_pos.start, c.node_pos.end
        # print c.frame
        #from root to source node
        start, end = cls.get_word_index_range(c.sentence, c.node_pos.start, c.node_pos.end)
        path1 = c.parse_tree.treeposition_spanning_leaves(start, end)

        #from root to frame node
        start, end = cls.get_word_index_range(c.sentence, c.frame.start, c.frame.end)
        path2 = c.parse_tree.treeposition_spanning_leaves(start, end)
        
        if path1 == path2:
            return (u.label(),)
        else:
            #find their lowest common ancestor
            i = 0
            lca = c.parse_tree
            max_steps = min(len(path1),len(path2))
            while i < max_steps and path1[i] == path2[i]:
                lca = lca[path1[i]]
                i += 1

            steps = [lca.label()]
            # source node to LCA
            node = lca
            for ind in path1[i:-1]: #ignore the leaf node, so -1
                steps.insert(0, 'u')
                node = node[ind]
                steps.insert(0, node.label())

            # LCA to frame node
            node = lca
            for ind in path2[i:-1]: #ignore the leaf node, so -1
                steps.append('d')
                node = node[ind]
                steps.append(node.label())

            return tuple(steps)

class PhraseType(Feature):
    """
    >>> from nltk.tree import Tree
    >>> tree = Tree('ROOT', [Tree('S', [Tree('NP', [Tree('NP', [Tree('PRP$', ['Your']), Tree('NN', ['contribution'])]), Tree('PP', [Tree('TO', ['to']), Tree('NP', [Tree('NNP', ['Goodwill'])])])]), Tree('VP', [Tree('MD', ['will']), Tree('VP', [Tree('VB', ['mean']), Tree('ADVP', [Tree('ADVP', [Tree('RBR', ['more'])]), Tree('SBAR', [Tree('IN', ['than']), Tree('S', [Tree('NP', [Tree('PRP', ['you'])]), Tree('VP', [Tree('MD', ['may']), Tree('VP', [Tree('VB', ['know'])])])])])])])]), Tree('.', ['.'])])])
    >>> PhraseType.get_value(tree[0][0], None)
    'NP'
    """
    name = "phrase_type"
    
    @classmethod
    def get_value(cls, u, c):
        return u.label()

class HeadWordStem(Feature):
    """
    >>> from nltk.tree import Tree
    >>> tree = Tree('ROOT', [Tree('S', [Tree('NP', [Tree('NP', [Tree('PRP$', ['Your']), Tree('NN', ['contribution'])]), Tree('PP', [Tree('TO', ['to']), Tree('NP', [Tree('NNP', ['Goodwill'])])])]), Tree('VP', [Tree('MD', ['will']), Tree('VP', [Tree('VB', ['mean']), Tree('ADVP', [Tree('ADVP', [Tree('RBR', ['more'])]), Tree('SBAR', [Tree('IN', ['than']), Tree('S', [Tree('NP', [Tree('PRP', ['you'])]), Tree('VP', [Tree('MD', ['may']), Tree('VP', [Tree('VB', ['know'])])])])])])])]), Tree('.', ['.'])])])
    >>> HeadWordStem.get_value(tree[0], None)
    u'will'
    """
    name = "head_stem"
    stemmer=PorterStemmer()
        
    @classmethod
    def get_value(cls, u, c):
        head_word = get_head_word(u)
        if head_word == None:
            print u
        return cls.stemmer.stem(head_word)

class Voice(Feature):
    @classmethod
    def get_value(cls, u, c):
        pass

class Frame(Feature):
    name = "frame"
    @classmethod
    def get_value(cls, u, c):
        return c.frame.name


# For debugging purpose
class DummyNodeFeature(object):
    name = "node_dummy"
    
    @classmethod
    def get_value(cls, u, c):
        return (u.leaves(), u.label())


class FooFeature(object):
    name = "foo"
    
    @classmethod
    def get_value(cls, u, c):
        return "foo"

class BarFeature(object):
    name = "bar"
    
    @classmethod
    def get_value(cls, u, c):
        return "bar"


ALL_FEATURES = (Position, 
                PathToFrame, # tricky one
                PhraseType, HeadWordStem, Frame)
