
class FeatureExtractor(object):
    """
    feature_funcs: feature object from `features`. They are the features to extract
    
    >>> from features import (FooFeature, BarFeature)
    >>> ext = FeatureExtractor([FooFeature, BarFeature])
    >>> ext.extract('a', None)
    {'foo': 'foo', 'bar': 'bar'}
    """
    def __init__(self, feature_funcs):
        self.feature_funcs = feature_funcs

    def extract(self, unit, context):
        """
        unit: a parse tree node
        context: the context information about the node
        """
        return {f.name: f.get_value(unit, context)
                for f in self.feature_funcs}
