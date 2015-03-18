from lxml import etree
from collections import namedtuple
Annotation = namedtuple('Annotation', ['frame_name', 'target', 'FE'])
Target = namedtuple('Target', ['start', 'end'])
FrameElement = namedtuple('FrameElement', ['start', 'end', 'name'])

parser = etree.XMLParser(ns_clean=True)
    
def parse_fulltext(path):
    """
    Return the annotations of sentences that contain at least one manual annotation
    
    It's something like:
    [(sentence_words, [annotation1, anntatation2]), (....), (....)]
    
    >>> result = parse_fulltext("test_data/annotation1.xml")
    >>> len(result)
    1
    >>> len(result[0])
    2
    >>> result[0][0]
    u'Your contribution to Goodwill will mean more than you may know .'
    >>> result[0][1][0]
    Annotation(frame_name='Giving', target=Target(start=5, end=16), FE=[FrameElement(start=0, end=3, name='Donor'), FrameElement(start=18, end=28, name='Recipient')])
    >>> result[0][1][1]
    Annotation(frame_name='Purpose', target=Target(start=35, end=38), FE=[FrameElement(start=0, end=28, name='Means'), FrameElement(start=40, end=61, name='Value')])
    """
    tree = etree.parse(path, parser)

    result = []
    for sent in tree.xpath('sentence'):
        sent_str = sent.xpath('text')[0].text.decode('utf8')
        annotations = []
        for a in sent.xpath('annotationSet[@status="MANUAL"]'):
            target_node = a.xpath('layer[@name="Target"]/label')[0]
            target = Target(start = int(target_node.attrib['start']),
                            end = int(target_node.attrib['end']))
            
            FE = []
            for label in a.xpath('layer[@name="FE"]/label'):
                FE.append(FrameElement(start = int(label.attrib['start']), 
                                        end = int(label.attrib['end']), 
                                        name = label.attrib['name']))
            assert len(FE) > 0
            annotation = Annotation(frame_name = a.attrib['frameName'], 
                                    target = target, 
                                    FE = FE)
            
            annotations.append(annotation)
        if len(annotations) > 0: # only those with annotations
            result.append((sent_str, annotations))
    return result

            
                
        
