__author__ = 'markjacobsen'
from GCSWidget import *
from PyQt4 import QtCore, QtGui

class GCSWidgetHUD (GCSWidget):

    widgetName = "HUD"

    def __init__(self, state, parent):
        super(GCSWidget, self).__init__(state, parent)

        self.setWindowTitle("HUD")


        p = self.palette()
        p.setColor(self.backgroundRole(), QtCore.Qt.black)
        self.setPalette(p)
        self.setAutoFillBackground(True)
        self.setMinimumSize(200, 200)