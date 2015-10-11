"""
This is the root class for all opengcs widgets
"""

from PyQt4 import QtCore, QtGui


class GCSWidget (QtGui.QDockWidget):
    def __init__(self, state, parent):
        super(GCSWidget, self).__init__("GCS Widget", parent)
        self.state = state


        self.setWidget(QtGui.QLabel("hello"));
        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea);
