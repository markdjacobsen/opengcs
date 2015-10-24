__author__ = 'timk'
import sys
from os import path
from GCSWidget import *
from PyQt4.QtGui import *
from PyQt4 import QtCore

class GCSWidgetHUD2 (GCSWidget):

    widgetName = "HUD 2"

    def __init__(self, state, parent):
        super(GCSWidgetHUD, self).__init__(state, parent)
        self.setObjectName("GCSWidgetHUD2")
        self.setWindowTitle("HUD")
        self.setMinimumSize(200, 200)

        # Get application path and build asset path
        # TODO we should get the apps path from somewhere else, perhaps a config file
        app_dir = path.dirname(sys.argv[0])
        asset_dir = 'art/hud'
        self.asset_path = path.join(app_dir, asset_dir)

        # Initialise HUD elements
        self.init_horizon()
        self.init_compass()

    def init_horizon(self):

        # Labels of artificial horizon widget
        self.label_horizon_bg = QLabel("", self)
        self.label_horizon_fill = QLabel("", self)
        self.label_horizon_bubble = QLabel("", self)
        self.label_horizon_circle = QLabel("", self)
        self.label_horizon_mech = QLabel("", self)

        # Artificial horizon assets
        self.img_horizon_bg = QPixmap(path.join(self.asset_path, 'fi_circle.svg'))
        self.img_horizon_fill = QPixmap(path.join(self.asset_path, 'horizon_back.svg'))
        self.img_horizon_bubble = QPixmap(path.join(self.asset_path, 'horizon_ball.svg'))
        self.img_horizon_circle = QPixmap(path.join(self.asset_path, 'horizon_circle.svg'))
        self.img_horizon_mech = QPixmap(path.join(self.asset_path, 'horizon_mechanics.svg'))

        # Artificial horizon elements positioning
        self.label_horizon_fill.setScaledContents(True)
        self.label_horizon_fill.setGeometry(0, 0, 200, 200)
        self.label_horizon_fill.setPixmap(self.img_horizon_fill)

        self.label_horizon_bubble.setScaledContents(True)
        self.label_horizon_bubble.setGeometry(0, 0, 200, 200)
        self.label_horizon_bubble.setPixmap(self.img_horizon_bubble)

        self.label_horizon_circle.setScaledContents(True)
        self.label_horizon_circle.setGeometry(0, 0, 200, 200)
        self.label_horizon_circle.setPixmap(self.img_horizon_circle)

        self.label_horizon_mech.setScaledContents(True)
        self.label_horizon_mech.setGeometry(0, 0, 200, 200)
        self.label_horizon_mech.setPixmap(self.img_horizon_mech)

        self.label_horizon_bg.setScaledContents(True)
        self.label_horizon_bg.setGeometry(0, 0, 200, 200)
        self.label_horizon_bg.setPixmap(self.img_horizon_bg)


    def init_compass(self):

        # Labels of compass widget
        self.label_compass_bg = QLabel("", self)
        self.label_compass_dial = QLabel("", self)
        self.label_compass_mech = QLabel("", self)

        # Compass assets
        self.img_compass_bg = QPixmap(path.join(self.asset_path, 'fi_circle.svg'))
        self.img_compass_dial = QPixmap(path.join(self.asset_path, 'heading_yaw.svg'))
        self.img_compass_mech = QPixmap(path.join(self.asset_path, 'heading_mechanics.svg'))

        # Compass elements positioning
        self.label_compass_dial.setScaledContents(True)
        self.label_compass_dial.setGeometry(0, 200, 200, 200)
        self.label_compass_dial.setPixmap(self.img_compass_dial)

        self.label_compass_mech.setScaledContents(True)
        self.label_compass_mech.setGeometry(0, 200, 200, 200)
        self.label_compass_mech.setPixmap(self.img_compass_mech)

        self.label_compass_bg.setScaledContents(True)
        self.label_compass_bg.setGeometry(0, 200, 200, 200)
        self.label_compass_bg.setPixmap(self.img_compass_bg)
