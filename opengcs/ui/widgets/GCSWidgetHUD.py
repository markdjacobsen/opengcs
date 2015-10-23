__author__ = 'markjacobsen'
from GCSWidget import *
from PyQt4.QtGui import *
from PyQt4 import QtCore

class GCSWidgetHUD (GCSWidget):

    widgetName = "HUD"

    def __init__(self, state, parent):
        super(GCSWidgetHUD, self).__init__(state, parent)
        self.setObjectName("GCSWidgetHUD")
        self.setWindowTitle("HUD")

        self.label_altitude = QLabel("0", self)
        self.label_airspeed = QLabel("0", self)

        self.label_altitude.move(5, int(parent.height()/2) - 10)
        self.label_airspeed.move(parent.width() - 100, int(parent.height()/2) - 10)
        #self.label_airspeed.move(50, int(parent.height()/2) - 10)

        #p = self.palette()
        #p.setColor(self.backgroundRole(), QtCore.Qt.black)
        #self.setPalette(p)
        #self.setAutoFillBackground(True)
        self.setMinimumSize(200, 200)