__author__ = 'markjacobsen'
from GCSWidget import *
from PyQt4 import QtCore, QtGui

class GCSWidgetMap (GCSWidget):

    widgetName = "Map"

    def __init__(self, state, parent):
        super(GCSWidgetMap, self).__init__(state, parent)
        self.setObjectName("GCSWidgetMap")
        self.setWindowTitle("Map")
        self.setWidget(QtGui.QLabel("Map Widget"))

        p = self.palette()
        p.setColor(self.backgroundRole(), QtCore.Qt.blue)
        self.setPalette(p)
        self.setAutoFillBackground(True)
        self.setMinimumSize(400, 400)
