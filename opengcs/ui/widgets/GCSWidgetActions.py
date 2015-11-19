

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
        self.vbox.addWidget(button_arm)

        button_rtl = QPushButton('&RTL', self)
        button_rtl.clicked.connect(self.on_button_rtl)
        self.vbox.addWidget(button_rtl)

        # Mode selection
        layout_mode = QHBoxLayout()
        self.combo_modes = QComboBox(self)
        button_mode = QPushButton('Set &Mode', self)
        button_mode.clicked.connect(self.on_button_mode)
        layout_mode.addWidget(self.combo_modes)
        layout_mode.addWidget(button_mode)
        self.vbox.addLayout(layout_mode)

        # Set WP
        layout_wp = QHBoxLayout()
        self.combo_wps = QComboBox(self)
        button_set_wp = QPushButton('Set &WP', self)
        button_set_wp.clicked.connect(self.on_button_set_wp)
        layout_wp.addWidget(self.combo_wps)
        layout_wp.addWidget(button_set_wp)
        self.vbox.addLayout(layout_wp)

        # Change alt
        layout_alt = QHBoxLayout()
        self.spinbox_alt = QSpinBox(self)
        button_set_alt = QPushButton('Change &Alt', self)
        button_set_alt.clicked.connect(self.on_button_set_alt)
        layout_alt.addWidget(self.spinbox_alt)
        layout_alt.addWidget(button_set_alt)
        self.vbox.addLayout(layout_alt)

        # Change speed
        layout_speed = QHBoxLayout()
        self.spinbox_speed = QSpinBox(self)
        button_set_speed = QPushButton('Change &Speed', self)
        button_set_speed.clicked.connect(self.on_button_set_speed)
        layout_speed.addWidget(self.spinbox_speed)
        layout_speed.addWidget(button_set_speed)
        self.vbox.addLayout(layout_speed)

        self.vbox.addStretch(1)

    def on_button_arm(self):
        for mav in self.get_mavs():
            print("Arming mav " + mav.get_name())
            mav.master.arducopter_arm()
        return

    def on_button_mode(self):

        print('on_button_mode()')
        return

    def on_button_set_wp(self):

        print('on_button_set_wp()')
        return

    def on_button_rtl(self):

        print('on_button_rtl()')
        return

    def on_button_set_alt(self):

        print('on_button_set_alt()')
        return

    def on_button_set_speed(self):

        print('on_button_set_speed()')
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