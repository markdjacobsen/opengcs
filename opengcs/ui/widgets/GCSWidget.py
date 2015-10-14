"""
This is the root class for all opengcs widgets
"""

from PyQt4 import QtCore, QtGui


class GCSWidget (QtGui.QDockWidget):

    # This is the name that will appear in the widget list on the "Add New Widget" window.
    # That window searches through the entire widgets directory, recursively searches
    # through all the GCSWidget-derived classes, and pulls out this name. Override it in
    # your class.
    widgetName = "GCSWidget"

    def __init__(self, state, parent):
        super(GCSWidget, self).__init__("TODO", parent)
        self.state = state
        self.setWindowTitle("Blank Widget (Base Class)")

        self.setWidget(QtGui.QLabel("Inherit from GCSWidget to create your own widget"));
        #self.mousePressEvent.connect(self.on_mouse)

    def mousePressEvent(self, QMouseEvent):
        print("Features" + str(self.features()))
        print("Height: " + str(self.height()), "Width: " + str(self.width()))
        print("Is floating: " + str(self.isFloating()))
        print("Pos: " + str(self.pos()))
        print("Size: " + str(self.size()))
        print("X: " + str(self.x))
        print("Y: " + str(self.y))


