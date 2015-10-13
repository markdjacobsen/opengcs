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
        super(GCSWidget, self).__init__("GCS Widget", parent)
        self.state = state


        self.setWidget(QtGui.QLabel("hello"));
        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea);

