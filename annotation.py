import sys, io
from lxml import etree
from collections import namedtuple
Annotation = namedtuple('Annotation', ['frame_name', 'target', 'FE'])
Target = namedtuple('Target', ['start', 'end'])
FrameElement = namedtuple('FrameElement', ['start', 'end', 'name'])

parser = etree.XMLParser(ns_clean=True)

#######################
# Remove namespace by using an XSL transformation
#######################
xslt="""<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="xml" indent="no"/>

<xsl:template match="/|comment()|processing-instruction()">
    <xsl:copy>
      <xsl:apply-templates/>
    </xsl:copy>
</xsl:template>

<xsl:template match="*">
    <xsl:element name="{local-name()}">
      <xsl:apply-templates select="@*|node()"/>
    </xsl:element>
</xsl:template>

<xsl:template match="@*">
    <xsl:attribute name="{local-name()}">
      <xsl:value-of select="."/>
    </xsl:attribute>
</xsl:template>
</xsl:stylesheet>
"""

xslt_doc=etree.parse(io.BytesIO(xslt))
transform=etree.XSLT(xslt_doc)
    
def parse_fulltext(path):
    """
    Return the annotations of sentences that contain at least one manual annotation
    
    It's something like:
    [(sentence_string, [annotation1, anntatation2]), (....), (....)]
    
    >>> result = parse_fulltext("test_data/annotation.xml")
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
    
    # for DNI etc cases
    >>> result = parse_fulltext("test_data/annotation_dni.xml")
    >>> result[0][1][0]
    Annotation(frame_name='Importance', target=Target(start=60, end=63), FE=[FrameElement(start=65, end=70, name='Factor')])
    >>> result[0][1][1]
    Annotation(frame_name='Rewards_and_punishments', target=Target(start=154, end=163), FE=[])
    """
    tree = etree.parse(path, parser)
    tree=transform(tree) # remove namespace
    result = []
    for sent in tree.xpath('sentence'):
        sent_str = sent.xpath('text')[0].text.decode('utf8')
        annotations = []
        for a in sent.xpath('annotationSet[@status="MANUAL"]'):
            target_label = a.xpath('layer[@name="Target"]/label')
            if len(target_label) == 1:
                target_node = target_label[0]
            else:
                continue
                
            target = Target(start = int(target_node.attrib['start']),
                            end = int(target_node.attrib['end']))
            
            FE = []
            for label in a.xpath('layer[@name="FE"]/label[not(@itype)] '): # exclude null instantiation ones
                if 'start' in label.attrib: # if it has `start` key
                    FE.append(FrameElement(start = int(label.attrib['start']), 
                                           end = int(label.attrib['end']), 
                                           name = label.attrib['name']))

            if len(FE) == 0:
                sys.stderr.write('No valid FrameElement found in\n %s' %(a))

            annotation = Annotation(frame_name = a.attrib['frameName'], 
                                    target = target, 
                                    FE = FE)
            
            annotations.append(annotation)
        if len(annotations) > 0: # only those with annotations
            result.append((sent_str, annotations))

    if len(result) == 0:
        sys.stderr.write("WARNING: no result found for %s" %(path))

    return result

            
                
        
