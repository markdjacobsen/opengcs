# This class loads an interactive checklist from an XML file and stores it in a Checklist object.
# The checklist object contains code for navigating the checklist.
# The checklist user interface in SAPStation uses one of these Checklist objects as inputs.

import xml.sax
import os
import config

PANEL_TEXT = 0
PANEL_MEDIA = 1
PANEL_CODE = 2

TYPE_NORMAL = 0
TYPE_PROBLEM = 1
TYPE_ABORT = 2

class ChecklistButton():
    """
    Represents a single button on a checklist item. Text and color are self-explanatory.
    'Code' points to a code block that will execute when the user presses the button.
    'Link' is a string with the id for the next checklist step that occurs after clicking.
    This object corresponds to a <BUTTON> object in the XML file.
    """
    def __init__(self):
        self.text = ""
        self.color = ""
        self.code = None
        self.link = ""
        self.visible = True
        self.enabled = True

class ChecklistPanel():
    def __init__(self):
        self.type = PANEL_TEXT
        self.resource = ""


class ChecklistStep():
    """
    This class contains all the info for a given checklist step, and corresponds to a
    <STEP> object in the XML file.
    """
    def __init__(self):
        self.title = ""
        self.type = TYPE_NORMAL
        self.panels = []
        self.buttons = []


class Checklist():
    """
    This object contains an entire preflight checklist for an aircraft. It consists of a dictionary
    of steps, and a key corresponding to the first step.
    """
    def __init__(self):
        self.first = ""
        self.steps = {}
        self.directory = ""

    def load(self,filename):
        parser = xml.sax.make_parser()
        parser.setFeature(xml.sax.handler.feature_namespaces, 0)
        # override the default ContextHandler
        Handler = ChecklistXMLHandler()
        parser.setContentHandler( Handler )
        parser.parse(filename)

        self.directory = os.path.dirname(os.path.realpath(filename))


        self.steps = Handler.steps
        self.first = Handler.first

    def print_all(self):
        print("First: " + self.first)
        for key in self.steps:
            step = self.steps[key]
            print("\n\nSTEP")
            print("Title: " + step.title)
            s = ["Normal","Problem","Abort"]
            print("Type:  " + s[step.type])
            for p in step.panels:
                s = ["Text", "Media", "Code"]
                print("Panel: " + s[p.type])
                print("Rsrc:  " + p.resource)

            for b in step.buttons:
                print("BUTTON")
                print("Text:    " + str(b.text))
                print("Color:   " + str(b.color))
                print("Code:    " + str(b.code))
                print("Link:    " + str(b.link))
                print("Visible: " + str(b.visible))
                print("Enabled: " + str(b.enabled))

class ChecklistXMLHandler( xml.sax.ContentHandler ):
    def __init__(self):
        self.steps = {}

        self.current_tag = ""   # Always holds the name of the element we are in
        self.stepid = ""
        self.text = ""

        # These flags indicate which type of element we are in when parsing the
        # file. The tags get set in startELement() and get reset in endElement()
        # IN_LANGUAGE is unique because it is a catch-all for any element not
        # explicitly defined in the Checklist structure, like TITLE or BUTTON.
        # This will catch language codes like EN, AR, etc.
        self.IN_STEP = False
        self.IN_PANEL = False
        self.IN_BUTTON = False
        self.IN_EXPANDED = False
        self.IN_LANGUAGE = False

        self.current_checklist_step = None
        self.current_checklist_panel = None
        self.current_checklist_button = None



    # Call when an element starts
    def startElement(self, tag, attributes):
        self.current_tag = tag
        if tag == "STEP":
            # If we are entering a new STEP element, create a new Checklist Item
            # and add it to the dictionary with the correct id
            self.IN_STEP = True
            self.current_checklist_step = ChecklistStep()
            self.stepid = attributes["id"]
            if "type" in attributes:
                a = attributes["type"]
                if a == "normal":
                    self.current_checklist_step.type = TYPE_NORMAL
                elif a == "problem":
                    self.current_checklist_step.type = TYPE_PROBLEM
                elif a == "abort":
                    self.current_checklist_step.type = TYPE_ABORT

            self.steps[self.stepid] = self.current_checklist_step
        elif tag == "FIRST":
            self.first = attributes["id"]
        elif tag == "BUTTON":
            # We are entering a new BUTTON element, so create a new ChecklistButton
            # and add it to the
            self.IN_BUTTON = True
            self.current_checklist_button = ChecklistButton()
            if "color" in attributes:
                self.current_checklist_button.color = attributes["color"]
            if "link" in attributes:
                self.current_checklist_button.link = attributes["link"]
            if "enabled" in attributes:
                a = attributes["enabled"]
                if a == "true":
                    self.current_checklist_button.enabled = True
                else:
                    self.current_checklist_button.enabled = False
            if "visible" in attributes:
                a = attributes["visible"]
                if a == "true":
                    self.current_checklist_button.visible = True
                else:
                    self.current_checklist_button.visible = False

            self.current_checklist_step.buttons.append(self.current_checklist_button)
        elif tag == "TITLE":
            self.IN_TITLE = True
        elif tag == "PANEL":
            self.IN_PANEL = True
            self.current_checklist_panel = ChecklistPanel()
            if "type" in attributes:
                t = attributes["type"]
                if t=="text":
                    self.current_checklist_panel.type = PANEL_TEXT
                elif t=="media":
                    self.current_checklist_panel.type = PANEL_MEDIA
                elif t=="code":
                    self.current_checklist_panel.type = PANEL_CODE
            self.current_checklist_step.panels.append(self.current_checklist_panel)
        elif tag == "CHECKLIST":
            return
        elif tag == config.language:
            self.IN_LANGUAGE = True

    # Call when an elements ends
    def endElement(self, tag):
        if tag == "STEP":
            self.IN_STEP = False
        elif tag == "BUTTON":
            self.IN_BUTTON = False
        elif tag == "TITLE":
            self.IN_TITLE = False
        elif tag == "PANEL":
            self.IN_PANEL = False
        elif tag == "CHECKLIST":
            return
        elif tag == config.language:
            self.IN_LANGUAGE = False

    # Call when a character is read
    def characters(self, content):
        # We only need ot read characters in a language tab
        if self.IN_LANGUAGE == True:
            if self.IN_TITLE == True:
                self.current_checklist_step.title = content
            elif self.IN_PANEL == True:
                self.current_checklist_panel.resource = content
            elif self.IN_BUTTON == True:
                self.current_checklist_button.text = content


# This is used for testing and debugging. It loads a test checklist and outputs the contents
# to the console, to ensure that everything has loaded from XML
if __name__ == "__main__":
    checklist1 = Checklist()
    checklist1.load("Aircraft/Fx61/checklist.xml")
    checklist1.print_all()