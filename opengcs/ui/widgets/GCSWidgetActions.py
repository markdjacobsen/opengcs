

import sys
from os import path
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from gcs_state import *
from GCSWidget import *

class GCSWidgetActions (GCSWidget):

    widget_name_plaintext = 'MAV/Swarm Actions'

    def __init__(self, state, parent):

        super(GCSWidgetActions, self).__init__(state, parent)
        self.set_datasource_allowable(WidgetDataSource.SINGLE|WidgetDataSource.SWARM)
        self.setWindowTitle('MAV/Swarm Actions')
        self.setMinimumSize(100, 100)

        self.init_ui()

    def init_ui(self):

        # scrollarea holds mylayout, mylayout holds vbox, vbox holds panes

        self.vbox = QVBoxLayout()
        self.vbox.setContentsMargins(5, 5, 5, 5)
        self.master_widget = QWidget(self)
        self.master_widget.setLayout(self.vbox)
        self.setWidget(self.master_widget)

        button_arm = QPushButton('&Arm/Disarm', self)
        button_arm.clicked.connect(self.on_button_arm)

        button_mode = QPushButton('Set &Mode', self)
        button_mode.clicked.connect(self.on_button_mode)
        self.vbox.addWidget(button_arm)
        self.vbox.addWidget(button_mode)

    def on_button_arm(self):
        for mav in self.get_mavs():
            print("Arming mav " + mav.get_name())
            mav.master.arducopter_arm()
        return

    def on_button_mode(self):

        return

    def resizeEvent(self, event):
        super(GCSWidgetActions, self).refresh()
    #   self.refresh()

    def refresh(self):

        return

    def process_messages(self, m):

        return

    def read_settings(self, settings):

        return

    def write_settings(self, settings):

        return