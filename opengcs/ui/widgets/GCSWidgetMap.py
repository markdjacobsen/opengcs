__author__ = 'markjacobsen'
from GCSWidget import *
from PyQt4 import QtCore, QtGui

class GCSWidgetMap (GCSWidget):

    widget_name_plaintext = "Map"

    def __init__(self, state, parent):
        super(GCSWidgetMap, self).__init__(state, parent)
        self.setWindowTitle("Map")
        self.setWidget(QtGui.QLabel("Map Widget"))
        self.setMinimumSize(400, 400)

        # Placeholder color background
        p = self.palette()
        p.setColor(self.backgroundRole(), QtCore.Qt.blue)
        self.setPalette(p)
        self.setAutoFillBackground(True)

    def refresh(self):

        super(GCSWidgetMap, self).refresh()