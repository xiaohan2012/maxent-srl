# -*- coding: utf-8 -*-

"""
Parser for Stanford Dependency Parser output to parse back the original data structure in Python

The parser link:

http://nlp.stanford.edu/software/nndep.shtml

"""

import sys
import re
import operator
import textwrap
from StringIO import StringIO

__all__ = ["parse_output"]

class Node(object):
    u"""
    Dependency parse tree node class
    
    >>> n1 = Node("Big", 1, "ADJ")
    >>> n2 = Node("Bang", 0)
    >>> n3 = Node("Big", 1, "BBB")
    >>> n1 == n2
    False
    >>> n1 == n3
    True
    >>> print n1
    Big(ADJ)-1
    >>> print n2
    Bang-0
    >>> n4 = Node(u"EnCompass®", 1)
    >>> print n4
    EnCompass®-1
    >>> n = Node.load_from_str(u"Systems-14")
    >>> print n
    Systems-14
    >>> n = Node.load_from_str(u"Systems-14", {14: Node(u'Systems', 14, "NN")})
    >>> print n
    Systems(NN)-14
    >>> n = Node.load_from_str(u"system-design-14", {14: Node(u'system-design', 14, "NN")})
    >>> print n
    system-design(NN)-14
    >>> n = Node.load_from_str(u"feng-1", [Node('ROOT', 0), Node('feng', 1, "BB")])
    >>> print n
    feng(BB)-1

    """
    def __init__(self, token, index, pos_tag=None):
        self.token = token
        self.index = index
        self.pos_tag = pos_tag
    
    def __unicode__(self):
        if self.index == 0 or self.pos_tag == None:
            return u"%s-%d" %(self.token, self.index)
        else:
            return u"%s(%s)-%d" %(self.token, self.pos_tag, self.index)
            
    def __repr__(self):
        return unicode(self).encode("utf8")

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        else:
            return other.token == self.token and other.index == self.index
    def __hash__(self):
        return hash(repr(self))

    @property        
    def dot_str(self):
        return '"%s" [label="%s"];' %(unicode(self), unicode(self.token))

    @classmethod
    def load_from_str(self, s, all_nodes = None):
        """
        all_nodes can be either dictionary(word index -> Node) or list of Nodes in sentence word order
        """
        # last occuring '-' position
        last_hyphen_index = len(s) - s[::-1].index('-') - 1

        token = s[:last_hyphen_index]
        try:
            word_index = int(s[last_hyphen_index+1:].strip('\'')) # the remind-34' case
        except ValueError:
            raise ValueError("s = %s, last_hypen_index = %d" %(s, last_hyphen_index))

        if all_nodes:
            return all_nodes[word_index]
        else:
            return Node(token, word_index)


ROOT = Node("ROOT", 0)

class Edge(tuple):
    def __new__(cls, from_node, to_node, edge_type):
        # tule is inmutable, so __new__ should be called
        obj = tuple.__new__(Edge, [from_node, to_node, edge_type])
        obj.from_node = from_node
        obj.to_node   = to_node  
        obj.edge_type = edge_type
        
        return obj
        
    def __unicode__(self):
        return u"(%s, %s, %s)" %(unicode(self.from_node), 
                                 unicode(self.to_node), 
                                 unicode(self.edge_type))

    def __repr__(self):
        return unicode(self).encode('utf8')
        
    @property
    def dot_str(self):
        return u'"%s" -> "%s" [label="%s"];' %(unicode(self.from_node), unicode(self.to_node), unicode(self.edge_type))

    def __eq__(self, other):
        if not isinstance(other, Edge):
            return False
        else:
            return other.from_node == self.from_node and other.to_node == self.to_node and other.edge_type == self.edge_type

class DepParseResult(object):
    """
    Dependency parse result

    Example:
    -------
    
    >>> from codecs import open
    >>> t = parse_output(open("data/test_parse_tree.txt", "r", "utf8"))[0]
    >>> dot_str = t.to_dot()
    """
    def __init__(self, sent_id, sentence, nodes, edges):
        self.sent_id = sent_id
        self.sentence = sentence.replace("\"", "\\\"") # escape quote

        self.nodes = nodes
        self.edges = edges

    def to_dot(self):        
        output = u"""digraph sent_%d {\n\t""" %(self.sent_id)
        output += u"""
\tlabelloc="t";
\tlabel="%s";
\t""" %(
    '\\n'.join(
        textwrap.wrap(self.sentence)
    )
)
        
        output += u'\n\t'.join(map(operator.attrgetter('dot_str'), self.nodes))
        output += u'\n\n\t'
        output += u'\n\t'.join(map(operator.attrgetter('dot_str'), self.edges))
        output += u'\n'
        output += u'};\n'
        return output

find_seg_regexp = re.compile(r"\[(\S+\s?){4}\]")
def parse_token_pos_line(l, prepend_root = True):
    """
    Parsing the line containing tokens and POS tags information

    l: str
         The token&POS line

    prepend_root: bool
         If True, root is automatically prepended to the list
    
    >>> print parse_token_pos_line(u"[Text=Schneider CharacterOffsetBegin=0 CharacterOffsetEnd=9 PartOfSpeech=NNP] [Text=Electric CharacterOffsetBegin=10 CharacterOffsetEnd=18 PartOfSpeech=NNP]", prepend_root = True)
    [ROOT-0, Schneider(NNP)-1, Electric(NNP)-2]
    >>> print parse_token_pos_line("[Text=Electric CharacterOffsetBegin=10 CharacterOffsetEnd=18 PartOfSpeech=NNP]", prepend_root = False)
    [Electric(NNP)-1]
    """

    def parse_seg(seg_str):
        text_str, _, _, pos_str = seg_str.split()
        try:
            return text_str.split('=')[1], pos_str.split('=')[1]
        except IndexError:
            raise IndexError("text_str=%s, pos_str=%s" %(text_str, pos_str))

    segs = l.strip()[1:-1].split('] [')
    nodes = (
        [ROOT] if prepend_root else []
     )

    for i, seg in enumerate(segs):
        token, pos = parse_seg(seg)
        nodes.append(Node(token, i+1, pos))

    return nodes

def parse_edge_line(l, nodes):
    """
    Parse the edge(of dependency parse tree ) line, return an edge
    
    Param:
    ----------

    l: str
       the edge line

    nodes: list of Node
       nodes listed in sentence words order
    
    
    Return:
    ----------
    
    The edge in the format: (from_node, to_node, edge_type)

    Examples:
    -------------

    >>> nodes = parse_token_pos_line(u"[Text=Schneider CharacterOffsetBegin=0 CharacterOffsetEnd=9 PartOfSpeech=NNP] [Text=Electric CharacterOffsetBegin=10 CharacterOffsetEnd=18 PartOfSpeech=NNP] [Text=Introduces CharacterOffsetBegin=19 CharacterOffsetEnd=29 PartOfSpeech=VBZ] [Text=Strategic CharacterOffsetBegin=30 CharacterOffsetEnd=39 PartOfSpeech=NNP] [Text=Operation CharacterOffsetBegin=40 CharacterOffsetEnd=49 PartOfSpeech=NNP] [Text=Services CharacterOffsetBegin=50 CharacterOffsetEnd=58 PartOfSpeech=NNPS] [Text=Offerings CharacterOffsetBegin=59 CharacterOffsetEnd=68 PartOfSpeech=NNPS] [Text=to CharacterOffsetBegin=69 CharacterOffsetEnd=71 PartOfSpeech=TO] [Text=Simplify CharacterOffsetBegin=72 CharacterOffsetEnd=80 PartOfSpeech=VB] [Text=and CharacterOffsetBegin=81 CharacterOffsetEnd=84 PartOfSpeech=CC] [Text=Optimise CharacterOffsetBegin=85 CharacterOffsetEnd=93 PartOfSpeech=NNP] [Text=Data CharacterOffsetBegin=94 CharacterOffsetEnd=98 PartOfSpeech=NNP] [Text=Centre CharacterOffsetBegin=99 CharacterOffsetEnd=105 PartOfSpeech=NNP] [Text=Systems CharacterOffsetBegin=106 CharacterOffsetEnd=113 PartOfSpeech=NNPS]")
    >>> parse_edge_line(u"root(ROOT-0, Introduces-3)", nodes)
    (ROOT-0, Introduces(VBZ)-3, root)
    >>> parse_edge_line(u"nn(Systems-14, Centre-13)", nodes)
    (Systems(NNPS)-14, Centre(NNP)-13, nn)
    """
    try:
        paren_pos = l.index('(') # pos of the first paren, where we split
    except ValueError:
        raise ValueError("Trying to find parenthesis in `%s`" %(l))

    edge_type = l[:paren_pos]

    rest = l[paren_pos+1:][:-1]
    try:
        from_node, to_node = map(
            lambda s: Node.load_from_str(s, nodes), 
            rest.split(', ')
        )
    except ValueError:
        raise ValueError("Splitting `%s` by `, `" %(rest))
    
    return Edge(from_node, to_node, edge_type)

def parse_output(obj):
    """
    Param:
    -------
    obj: str or object with `readline` method
         the object to be parsed
    
    Return:
    -------
    The node lists
    The edges

    >>> from codecs import open
    >>> t1 = parse_output(open("data/test_parse_tree.txt", "r", "utf8"))
    >>> len(t1)
    1
    >>> t2 = parse_output(open("data/test_parse_tree.txt", "r", "utf8").read())
    >>> len(t2)
    1
    >>> assert t1[0].nodes == t2[0].nodes
    >>> assert t1[0].edges == t2[0].edges
    >>> print t1[0].nodes
    [ROOT-0, Schneider(NNP)-1, Electric(NNP)-2, Introduces(VBZ)-3, Strategic(NNP)-4, Operation(NNP)-5, Services(NNPS)-6, Offerings(NNPS])-7]
    >>> print t1[0].edges
    [(ROOT-0, Introduces(VBZ)-3, root), (Electric(NNP)-2, Schneider(NNP)-1, nn), (Introduces(VBZ)-3, Electric(NNP)-2, nsubj), (Offerings(NNPS])-7, Strategic(NNP)-4, nn), (Offerings(NNPS])-7, Operation(NNP)-5, nn), (Offerings(NNPS])-7, Services(NNPS)-6, nn), (Introduces(VBZ)-3, Offerings(NNPS])-7, dobj)]
    >>> t3 = parse_output(open("data/test_parse_tree_multi_sent_case.txt", "r", "utf8").read())
    >>> len(t3) 
    2
    """
    SENT_PREFIX = "Sentence #"
    if isinstance(obj, basestring):
        obj = StringIO(obj)
    else:
        assert hasattr(obj, 'readline'), "obj should have `readline` method "
        assert hasattr(obj, 'readlines'), "obj should have `readlines` method "
        
    results = []
    
    sent_id = 1
    
    # spends the first line as it's useless        
    l = obj.readline()
    assert l.startswith(SENT_PREFIX)
    while True:
        sentence = obj.readline().strip()
        
        if len(sentence) == 0: #end of story
            break
            
        nodes = parse_token_pos_line(obj.readline(),  
                                     prepend_root = True)
        edges = []
        for l in obj:
            if len(l.strip()) == 0: # skip non-sense lines
                continue
            if l.startswith(SENT_PREFIX):
                break
            edges.append(parse_edge_line(l.strip(), nodes))
            
        results.append(DepParseResult(sent_id, sentence, nodes, edges))
        sent_id += 1

    return results

if __name__ == "__main__":
    import argparse, os
    from codecs import open
        
    parser = argparse.ArgumentParser("Parse and visualize Dependence parse tree file(produced by Stanford CoreNLP package). Output is dot file")
    parser.add_argument("-i", type=str, required = True, nargs="+",
                        dest = "input_paths",
                        help = "Input file paths"
    )

    parser.add_argument("--display", 
                        action = "store_true",
                        help = "Wheter to display or not"
    )
    
    parser.add_argument("-o", type=str, nargs="+",
                        dest = "output_dir",
                        help = "Output directory(default to current directory)"
    )
    
    args = parser.parse_args()
    for path in args.input_paths:
        file_name = os.path.basename(path).split('.')[0]

        with open(path, "r", "utf8") as f_in:
            rs = parse_output(f_in)
            
            if args.output_dir:
                with open(output_path, "w", "utf8") as f_out:
                    output_path = os.path.join(args.output_dir, file_name + ".dot")
                    for r in rs:
                        f_out.write(r.to_dot() + '\n')
            else:
                for r in rs:
                    print r.to_dot().encode('utf8')
