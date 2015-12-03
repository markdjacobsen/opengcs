# TODO Allow horizontal expansion of panes

from GCSWidget import *
from PyQt4.QtGui import *
from opengcs import *
from gcs_state import *
from pymavlink import mavutil
import math
from GCSWidgetHUD import *

class GCSWidgetConsole (GCSWidget):

    widget_name_plaintext = 'Console'

    def __init__(self, state, parent):

        super(GCSWidgetConsole, self).__init__(state, parent)
        self.set_datasource_allowable(WidgetDataSource.SINGLE|WidgetDataSource.SWARM)
        self.setWindowTitle('Console')
        self.setMinimumSize(100, 100)

        # Darker background between MAV panes
        bg_palette = QPalette()
        bg_palette.setColor(QPalette.Background, QColor(100,100,100))
        self.setAutoFillBackground(True)
        self.setPalette(bg_palette)

        self.init_ui()
        self.refresh()

    def init_ui(self):

        # scrollarea holds mylayout, mylayout holds vbox, vbox holds panes

        self.vbox = QVBoxLayout()
        self.vbox.setContentsMargins(5, 5, 5, 5)
        self.mylayout = QWidget(self)
        self.mylayout.setLayout(self.vbox)
        #self.setWidget(mylayout)

        self.scrollarea = QScrollArea(self)
        self.scrollarea.setWidget(self.mylayout)
        self.scrollarea.setWidgetResizable(True)

        #self.scrollarea.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.setWidget(self.scrollarea)

    def resizeEvent(self, event):
        super(GCSWidgetConsole, self).refresh()
    #   self.refresh()

    def refresh(self):

        # Clear out the routing dictionary first, so no messages are delivered to
        # widgets that we are deleting
        self.routing_dictionary = {}

        # Remove existing panes
        for i in range(0, self.vbox.count()):
            widget = self.vbox.takeAt(0).widget()
            if widget is not None:
                widget.deleteLater()
                widget.hide()

        mavlist = []

        if isinstance(self._datasource, MAV):
            mavlist.append(self._datasource)
        elif isinstance(self._datasource, Swarm):
            for mav in self._datasource.mavs:
                mavlist.append(mav)

        for mav in mavlist:
            pane = GCSWidgetConsolePane(self.mylayout, self.state, mav)
            self.vbox.addWidget(pane, 0)
            self.routing_dictionary[mav.system_id] = pane
        self.vbox.addStretch(1)
        return

    def process_messages(self, m):

        # Forward the packet to the appropriate MAV pane
        # Need to check that the key exists, in case we're in the process of rebuilding the dictionary
        # when a message comes in
        if m.get_header().srcSystem in self.routing_dictionary:
            self.routing_dictionary[m.get_header().srcSystem].process_messages(m)

    def read_settings(self, settings):

        return

    def write_settings(self, settings):

        return


class GCSWidgetConsolePane(QFrame):

    def __init__(self, parent, state, mav):

        super(GCSWidgetConsolePane, self).__init__(parent)
        self.state = state
        self.mav = mav
        # MAV panes have a white background
        bg_palette = QPalette()
        bg_palette.setColor(QPalette.Background, QColor(255,255,255))
        self.setAutoFillBackground(True)
        self.setPalette(bg_palette)

        self.init_ui()

    def init_ui(self):

        self.setFrameStyle(QFrame.Panel|QFrame.Raised)
        self.setMinimumSize(400, 140)
        self.setFixedSize(400,140)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        vbox_master = QVBoxLayout(self)
        vbox_master.setContentsMargins(0, 0, 0, 0)
        mylayout = QWidget(self)
        mylayout.setLayout(vbox_master)


        self.horizon = HorizonWidget(self)
        self.horizon.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        f = QFont( "Arial", 14, QFont.Bold)
        self.label_name = QLabel(self.mav.get_name(), self)
        self.label_name.setFont(f)

        self.label_altitude = QLabel('', self)
        self.label_airspeed = QLabel('A', self)
        self.label_gndspeed = QLabel('G', self)
        self.label_heading = QLabel('', self)
        self.label_throttle = QLabel('', self)
        self.label_climb = QLabel('', self)
        self.label_roll = QLabel('', self)
        self.label_pitch = QLabel('', self)
        self.label_WP = QLabel('WP ', self)
        self.label_WPDist = QLabel('WP Dist', self)
        self.label_WPBearing = QLabel('WP Bearing', self)
        self.label_wind = QLabel('Wind ', self)
        self.label_mode = QLabel('Mode', self)

        self.horizon.setGeometry(50, 80, 75, 75)

        hbox_columns = QHBoxLayout()
        vbox_master.addWidget(self.label_name)
        vbox_master.addLayout(hbox_columns)
        vbox_primary_data = QVBoxLayout()
        vbox_supplementary_data = QVBoxLayout()
        hbox_columns.addLayout(vbox_primary_data)
        hbox_columns.addWidget(self.horizon)
        hbox_columns.addLayout(vbox_supplementary_data)

        vbox_primary_data.addWidget(self.label_altitude)
        vbox_primary_data.addWidget(self.label_airspeed)
        vbox_primary_data.addWidget(self.label_gndspeed)
        vbox_primary_data.addWidget(self.label_heading)

        hbox_supp_row1 = QHBoxLayout()
        hbox_supp_row2 = QHBoxLayout()
        vbox_supplementary_data.addLayout(hbox_supp_row1)
        vbox_supplementary_data.addLayout(hbox_supp_row2)

        #vbox_master.addWidget(self.horizon)
        #vbox_master.addWidget(self.label_altitude)
        #vbox_master.addWidget(self.label_airspeed)
        #vbox_master.addWidget(self.label_gndspeed)

        hbox_supp_row1.addWidget(self.label_mode)
        hbox_supp_row1.addWidget(self.label_throttle)
        hbox_supp_row1.addWidget(self.label_climb)
        hbox_supp_row1.addWidget(self.label_roll)
        hbox_supp_row1.addWidget(self.label_pitch)

        hbox_supp_row2.addWidget(self.label_WP)
        hbox_supp_row2.addWidget(self.label_WPBearing)
        hbox_supp_row2.addWidget(self.label_WPDist)
        hbox_supp_row2.addWidget(self.label_wind)

        self.setLayout(vbox_master)

    def process_messages(self, m):

        mtype = m.get_type()

        if mtype == "VFR_HUD":
            self.label_airspeed.setText("AS: {:.1f}".format(m.airspeed))
            self.label_gndspeed.setText("GS: {:.1f}".format(m.groundspeed))
            self.label_heading.setText("Hdg: {:.0f}".format(m.heading))
            self.label_throttle.setText("Thr {:.0%}".format(m.throttle))
            self.label_altitude.setText("Alt: {:.0f}m".format(m.alt))
            self.label_climb.setText("Clmb: {:.1f}".format(m.climb))

        elif mtype == "ATTITUDE":
            #self.label_roll.setText("Roll: {:.0f}".format(math.degrees(m.roll)))
            #self.label_pitch.setText("Pitch: {:.0f}".format(math.degrees(m.pitch)))
            self.horizon.roll_deg = math.degrees(m.roll)
            self.horizon.pitch_deg = math.degrees(m.pitch)
            self.horizon.update()

        elif mtype == 'WIND':
            self.label_wind.setText('Wind: %u/%.2f' % (m.direction, m.speed))

        elif mtype == 'NAV_CONTROLLER_OUTPUT':
            self.label_WPDist.setText('WP Dist %u' % m.wp_dist)
            self.label_WPBearing.setText('Bearing %u' % m.target_bearing)

        elif mtype in ['WAYPOINT_CURRENT', 'MISSION_CURRENT']:
            self.label_WP.setText('WP %u' % m.seq)

        elif mtype == 'HEARTBEAT':
            flightmode = mavutil.mode_string_v10(m)
            self.label_mode.setText("%s" % flightmode)
