from nltk.stem import PorterStemmer

class Feature(object):
    @classmethod
    def get_value(cls, unit, context):
        raise NotImplementedError

class Position(Feature):
    @classmethod
    def get_value(cls, u, c):
        pass

class PhraseType(Feature):
    @classmethod
    def get_value(cls, u, c):
        pass

class HeadWordStem(Feature):
    stemmer=PorterStemmer()

    @classmethod
    def get_head_word(cls, u):
        return u.words[-1]
        
    @classmethod
    def get_value(cls, u, c):
        return cls.stemmer.stem(cls.get_head_word())

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
