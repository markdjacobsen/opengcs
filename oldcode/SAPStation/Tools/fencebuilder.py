"""
This converts coordinates from a KML polygon into a C array that can be copy-pasted into ArduPlane.
Output looks like this:

Vector2l syria[25];
void build_syria(void)
{
	syria[0].x = 327726855;
	syria[0].y = 358393879;
	...
}

This is the coordinate format used by ArduPlane
"""
__author__ = 'markjacobsen'

from argparse import ArgumentParser
import xml.sax
from decimal import *

class PolygonKMLHandler( xml.sax.ContentHandler ):
    def __init__(self):
        self.IN_COORDINATES = False
        self.coordinates = ""

    # Call when an element starts
    def startElement(self, tag, attributes):
        self.current_tag = tag
        if tag == "coordinates":
            self.IN_COORDINATES = True

    # Call when an elements ends
    def endElement(self, tag):
        if tag == "coordinates":
            self.IN_COORDINATES = False

    # Call when a character is read
    def characters(self, content):
        # We only need ot read characters in a language tab
        if self.IN_COORDINATES == True:
            self.coordinates = self.coordinates + content


parser = ArgumentParser(description='')
parser.add_argument('filename', action='store', help='KML filename')
parser.add_argument('--name', action='store', help='Name for vector array', default="polygon")
args = parser.parse_args()
parser = xml.sax.make_parser()
parser.setFeature(xml.sax.handler.feature_namespaces, 0)
Handler = PolygonKMLHandler()
parser.setContentHandler( Handler )
parser.parse(args.filename)

trimmed = Handler.coordinates.strip('\t\n\r')
splits = trimmed.split(' ')
n = len(splits)-1

print "Vector2l " + args.name + "[" + str(n) + "];"
print "void build_" + args.name + "(void)\n{"
i = 0
for point in splits:
    elements = point.split(',')
    if len(elements) < 2:
        continue

    SEVENPLACES = Decimal(10) ** -7
    float_lat = Decimal(elements[1]).quantize(SEVENPLACES)
    float_lon = Decimal(elements[0]).quantize(SEVENPLACES)
    string_lat = str(float_lat).replace(".","")
    string_lon = str(float_lon).replace(".","")

    print "\t" + args.name + "[" + str(i) + "].x = " + string_lat + ";"
    print "\t" + args.name + "[" + str(i) + "].y = " + string_lon + ";"
    i = i + 1
print "}"