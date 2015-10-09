"""
strings.py

Author: Mark Jacobsen
Last Update: 6 Dec 2014
Status: complete

This file defines all the strings used by the application, and supports translation into multiple
languages without needing to use Python's localization features (which require compiling translation
files and are more complex than necessary for our purposes).

Strings are accessed via sapstring(), passing a message identifier string.
All strings are stored in a dictionary, keyed by message identifier string.
The first time sapstring() is called, the dictionary is built from a file called strings.xml. Format is:

<STRINGS>
    <STR id="message identifier">
        <EN>English string</EN>
        <AR>Arabic string</AR
        ... etc ...
    </STR>
</STRINGS

This dictionary is built using the language code specified in config.py
"""

import console
import xml.sax
import config

# This is the dictionary containing all translated strings in the application
_strings = None

def sapstring(str_id):
    """
    Returns a translated string with the given string identifier
    """


    if _strings == None:
        _load_strings()

    try:
        return _strings[str_id]
    except KeyError:
        console.error("Error trying to access string " + str_id)

def _load_strings():
    global _strings
    _strings = {}

    parser = xml.sax.make_parser()
    # turn off namepsaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    # override the default ContextHandler
    Handler = StringXMLHandler()
    parser.setContentHandler( Handler )
    parser.parse("strings.xml")

class StringXMLHandler( xml.sax.ContentHandler ):
    def __init__(self):
        global _strings

        self.CurrentData = ""
        self.msgid = ""
        self.text = ""

    # Call when an element starts
    def startElement(self, tag, attributes):
        self.CurrentData = tag
        if tag == "STR":
            self.msgid = attributes["id"]

    # Call when an elements ends
    def endElement(self, tag):
        if self.CurrentData == config.language:
            # Create the new entry in the dictionary
            _strings[self.msgid] = self.text
        self.CurrentData = ""

    # Call when a character is read
    def characters(self, content):
        if self.CurrentData == config.language:
            self.text = content