#import sys
#from os import path
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from pymavlink import mavutil
#from gcs_state import *
from GCSWidget import *
import mission
import pprint


class GCSWidgetActions (GCSWidget):

    widget_name_plaintext = 'MAV/Swarm Actions'

    def __init__(self, state, parent):

        super(GCSWidgetActions, self).__init__(state, parent)
        self.set_datasource_allowable(WidgetDataSource.SINGLE|WidgetDataSource.SWARM)
        self.setWindowTitle('MAV/Swarm Actions')
        self.setMinimumSize(100, 100)

        #pprint.pprint(mavutil.mavlink.enums)        # Debugging
        self.init_ui()

    def init_ui(self):

        # scroll area holds mylayout, mylayout holds vbox, vbox holds panes

        self.vbox = QVBoxLayout()
        self.vbox.setContentsMargins(5, 5, 5, 5)
        self.master_widget = QWidget(self)
        self.master_widget.setLayout(self.vbox)
        self.setWidget(self.master_widget)

        layout_status = QHBoxLayout()
        self.mode_label = QLabel('---Mode---', self)
        self.mode_label.setAlignment(Qt.AlignCenter);
        layout_status.addWidget(self.mode_label)
        self.armed_label = QLabel('---IsArmed?---', self)
        self.armed_label.setAlignment(Qt.AlignCenter);
        layout_status.addWidget(self.armed_label)
        self.wp_label = QLabel('---WP---', self)
        self.wp_label.setAlignment(Qt.AlignCenter);
        layout_status.addWidget(self.wp_label)
        self.vbox.addLayout(layout_status)

        # Arm/disarm
        layout_arm = QHBoxLayout()
        button_arm = QPushButton('&Arm', self)
        button_arm.clicked.connect(self.on_button_arm)
        layout_arm.addWidget(button_arm)

        button_disarm = QPushButton('&Disarm', self)
        button_disarm.clicked.connect(self.on_button_disarm)
        layout_arm.addWidget(button_disarm)
        self.vbox.addLayout(layout_arm)

        layout_discrete_modes = QHBoxLayout()
        # Auto / Execute mission - are these the same??  Don't think so
        button_auto = QPushButton('&Auto', self)
        button_auto.clicked.connect(self.on_button_auto)
        layout_discrete_modes.addWidget(button_auto)

        # Execute mission
        button_start_mission = QPushButton('&Start Miss.', self)
        button_start_mission.clicked.connect(self.on_button_start_mission)
        layout_discrete_modes.addWidget(button_start_mission)

        # RTL
        button_rtl = QPushButton('&RTL', self)
        button_rtl.clicked.connect(self.on_button_rtl)
        layout_discrete_modes.addWidget(button_rtl)
        self.vbox.addLayout(layout_discrete_modes)

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
        self.refresh()

    def refresh(self):
        print("Action panel refresh")
        # TODO KW: figure out how to optimize out clearing and resetting when unnecessary
        self.combo_modes.clear()
        self.combo_wps.clear()

        mavs = self.get_mavs()
        if len(mavs) > 0:
            mav = mavs[0]       # TODO KW: Temporary hack - not going to work for swarms or multi mavs
            mode_map = mav.master.mode_mapping()
            modes = mode_map.keys()
            self.combo_modes.addItems(modes)

            if mav.mission is not None and mav.mission.received_complete:
                wps_text = []
                for wp in mav.mission:
                    wps_text.append(str(wp.wp_msg.seq) + ": " + str(wp.wp_msg.command) + ": " + mavutil.mavlink.enums['MAV_CMD'][wp.wp_msg.command].name)
                self.combo_wps.addItems(wps_text)

        else:
            print("Action widget modes: no mavs")

    # TODO KW: ArduCopter only?  What happens if send to ArduPlane?
    def on_button_arm(self):
        for mav in self.get_mavs():
            print("Arming mav: " + mav.get_name())
            mav.master.arducopter_arm()
        return

    def on_button_disarm(self):
        for mav in self.get_mavs():
            print("Disarming mav: " + mav.get_name())
            mav.master.arducopter_disarm()
        return

    def on_button_auto(self):
        for mav in self.get_mavs():
            print("Setting mav to auto: " + mav.get_name())
            mav.master.set_mode_auto()
        return

    def on_button_start_mission(self):
        for mav in self.get_mavs():
            print("Starting mission for mav: " + mav.get_name() + " - NOT IMPLEMENTED")
            # TODO KW: Implement this
        return

    def on_button_rtl(self):
        for mav in self.get_mavs():
            print("RTL'ing mav: " + mav.get_name())
            mav.master.set_mode_rtl()
        return

    def on_button_mode(self):
        mode = str(self.combo_modes.currentText())
        for mav in self.get_mavs():
            print("Setting mode for mav: " + mav.get_name() +" to: " + mode)
            mav.master.set_mode(mode)
        return


    def on_button_set_wp(self):
        wp_seq = self.combo_wps.currentIndex()
        for mav in self.get_mavs():
            print("Setting waypoint for mav: " + mav.get_name() +" to: " + str(wp_seq))
            mav.master.waypoint_set_current_send(wp_seq)
        return

    def on_button_set_alt(self):
        altitude = self.spinbox_speed.value()
        for mav in self.get_mavs():
            print("Setting altitude for mav: " + mav.get_name() +" to: " + str(altitude))
            mav.master.mav.command_long_send(mav.master.target_system, mav.master.target_component,
                    mavutil.mavlink.MAV_CMD_NAV_CONTINUE_AND_CHANGE_ALT, 0, 0, 0, 0, 0, 0, 0, altitude)     # TODO KW: Confirm this is the right command to use
        return

    def on_button_set_speed(self):
        speed = self.spinbox_speed.value()
        for mav in self.get_mavs():
            print("Setting speed for mav: " + mav.get_name() +" to: " + str(speed))
            # TODO KW: Mavlink 1.0 only - see the messages implemented in mavutil.py which have code for multiple versions (this applies to many commands here)
            # TODO KW: Implement a generic command_long_send here or in pymavlink?
            # TODO KW: Would like to improve all these mav.master.mav.... pointers
            mav.master.mav.command_long_send(mav.master.target_system, mav.master.target_component,     # Note: Setting airspeed (vs. groundspeed)
                    mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED, 0, speed, -1, 0, 0, 0, 0, 0)
        return

    def resizeEvent(self, event):
        super(GCSWidgetActions, self).refresh()
    #   self.refresh()

    # TODO KW: Optimize the UI updating so that we are not updating it unless necessary
    def process_messages(self, m):
        mtype = m.get_type()
        if mtype == 'HEARTBEAT':
            flightmode = mavutil.mode_string_v10(m)
            self.mode_label.setText("%s" % flightmode)

            if m.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED:
                self.armed_label.setText("ARMED")
                self.armed_label.setStyleSheet("QLabel { color : red; font-weight: bold}");
            else:
                self.armed_label.setText("Disarmed")
                self.armed_label.setStyleSheet("QLabel { color : green; font-weight: bold}");
        if mtype == 'MISSION_CURRENT':
            self.wp_label.setText("WP " + str(m.seq))

        # TODO KW: Capture these sys text essages in a UI element (temporarily putting this here to capture them in the console)
        elif mtype == "STATUSTEXT":                         # TODO KW: Are there text/values after "command received: "
            print("Status text message: " + m.text)
        elif mtype == "COMMAND_ACK":
            print("Command acknowledged message: " + str(m.command) + " " + str(m.result))      # TODO KW: need to decode these fields
        return

    def read_settings(self, settings):

        return

    def write_settings(self, settings):

        return