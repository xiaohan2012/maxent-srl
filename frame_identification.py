import sys
from pathlib import Path
from annotation import (parse_fulltext, distribute_annotations)

def parse_xml_and_distribute(xml_path, target_dir):
    annotations = parse_fulltext(xml_path)
    distribute_annotations(annotations, target_dir, print_sent_path = True)


if __name__ == "__main__":
    size = 1
    target_dir = 'data/frame_identification'
    for i, p in enumerate(Path("/cs/fs2/home/hxiao/Downloads/fndata-1.5/fulltext/").glob("*.xml")):
        if i == size:
            break
        sys.stderr.write("Processing file: '%s'\n" %p.absolute())
        parse_xml_and_distribute(str(p.absolute()), target_dir)
