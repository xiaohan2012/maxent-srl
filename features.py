from nltk.stem import PorterStemmer
from ling_util import get_head_word

class Feature(object):
    @classmethod
    def get_value(cls, unit, context):
        raise NotImplementedError

class Position(Feature):
    @classmethod
    def get_value(cls, u, c):
        pass

class PhraseType(Feature):
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
        return cls.stemmer.stem(head_word)

class Voice(Feature):
    @classmethod
    def get_value(cls, u, c):
        pass

class Frame(Feature):
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
