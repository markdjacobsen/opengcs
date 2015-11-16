
from GCSWidget import *
from PyQt4.QtGui import *
from opengcs import *
from gcs_state import *
import math

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

        self.setWidget(self.scrollarea)

    def resizeEvent(self, event):

        self.refresh()

    def refresh(self):

        print("refresh()")

        # Remove old panes
        for i in range(0,self.vbox.count()):
            self.vbox.removeItem(self.vbox.itemAt(0))

        mavlist = []
        self.routing_dictionary = {}

        if isinstance(self._datasource, MAV):
            mavlist.append(self._datasource)
        elif isinstance(self._datasource, Swarm):
            for mav in self._datasource.mavs:
                mavlist.append(mav)
        print(mavlist)
        for mav in mavlist:
            pane = GCSWidgetConsolePane(self, self.state, mav)
            self.vbox.addWidget(pane)
            self.routing_dictionary[mav.system_id] = pane

        return

    def process_messages(self, m):

        # Forward the packet to the appropriate MAV pane
        self.routing_dictionary[m.get_header().srcSystem].process_messages(m)
        return

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
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        mylayout = QWidget(self)
        mylayout.setLayout(vbox)

        f = QFont( "Arial", 14, QFont.Bold)
        self.label_name = QLabel(str(self.mav.system_id), self)
        self.label_name.setFont(f)
        self.label_altitude = QLabel('', self)
        self.label_airspeed = QLabel('', self)
        self.label_gndspeed = QLabel('', self)
        self.label_heading = QLabel('', self)
        self.label_throttle = QLabel('', self)
        self.label_climb = QLabel('', self)
        self.label_roll = QLabel('', self)
        self.label_pitch = QLabel('', self)
        self.label_WP = QLabel('', self)
        self.label_WPDist = QLabel('', self)
        self.label_WPBearing = QLabel('', self)
        self.label_wind = QLabel('', self)

        self.scene = QGraphicsScene()
        self.hud = QGraphicsView(self.scene)


        vbox.addWidget(self.label_name)
        vbox.addWidget(self.hud.viewport())
        vbox.addWidget(self.label_altitude)
        vbox.addWidget(self.label_airspeed)
        vbox.addWidget(self.label_gndspeed)
        vbox.addWidget(self.label_heading)
        vbox.addWidget(self.label_throttle)
        vbox.addWidget(self.label_climb)
        vbox.addWidget(self.label_wind)
        vbox.addWidget(self.label_roll)
        vbox.addWidget(self.label_pitch)
        vbox.addWidget(self.label_WP)
        vbox.addWidget(self.label_WPDist)
        vbox.addWidget(self.label_WPBearing)

        self.setLayout(vbox)

    def process_messages(self, m):

        mtype = m.get_type()

        if mtype == "VFR_HUD":
            self.label_airspeed.setText("AS: {:.1f}".format(m.airspeed))
            self.label_gndspeed.setText("GS: {:.1f}".format(m.groundspeed))
            self.label_heading.setText("Hdg: {:.0f}".format(m.heading))
            self.label_throttle.setText("Thr {:.0%}".format(m.throttle))
            self.label_altitude.setText("{:.0f}m".format(m.alt))
            self.label_climb.setText("{:.2f}".format(m.climb))

        if mtype == "ATTITUDE":
            self.label_roll.setText("Roll: {:.0f}".format(math.degrees(m.roll)))
            self.label_pitch.setText("Pitch: {:.0f}".format(math.degrees(m.pitch)))

        elif type == 'WIND':
            self.label_wind.setText('Wind: %u/%.2f' % (m.direction, m.speed))

        elif type == 'NAV_CONTROLLER_OUTPUT':
            self.console.set_status('Distance %u' % m.wp_dist)
            self.console.set_status('Bearing %u' % m.target_bearing)

        elif type in ['WAYPOINT_CURRENT', 'MISSION_CURRENT']:
            self.console.set_status('WP', 'WP %u' % m.seq)
