from GCSWidget import *
from PyQt4.QtGui import *
from PyQt4 import QtCore
from pymavlink import mavutil

class GCSWidgetHUD (GCSWidget):

    widgetName = "HUD"

    def __init__(self, state, parent):

        super(GCSWidgetHUD, self).__init__(state, parent)
        self.setObjectName("GCSWidgetHUD")
        self.set_datasource_allowable(WidgetDataSource.SINGLE)
        self.init_ui()

    def init_ui(self):
        self.label_altitude = QLabel("0", self)
        self.label_airspeed = QLabel("0", self)
        self.label_throttle = QLabel("0", self)
        self.label_heading = QLabel("0", self)
        self.label_climbrate = QLabel("0", self)

        self.refresh()

    def resizeEvent(self, event):

        self.refresh()

    def refresh(self):

        super(GCSWidgetHUD, self).refresh()
        w = self.geometry().width()
        h = self.geometry().height()

        self.label_altitude.move(5, h/2-10)
        self.label_airspeed.move(w-25, h/2-10)
        self.label_throttle.move(5, 20)
        self.label_heading.move(w/2 - 10, 50)
        self.label_climbrate.move(w-25,20)

        self.setWindowTitle("HUD")
        self.setMinimumSize(200, 200)

    def process_messages(self, m):
        # This is a dummy handler to illustrate how message processing is done.
        # See the mavlink protocol for message types and member variables:
        # https://pixhawk.ethz.ch/mavlink/
        mtype = m.get_type()
        if mtype == "VFR_HUD":
            self.label_altitude.setText(str(m.alt))
            self.label_airspeed.setText(str(m.airspeed))
            self.label_throttle.setText(str(m.throttle))
            self.label_heading.setText(str(m.heading))
            self.label_climbrate.setText(str(m.climb))
        if mtype == "SYS_STATUS":
            voltage = m.voltage_battery
            current = m.current_battery
            remaining = m.battery_remaining
            droprate = m.drop_rate_comm
        if mtype == "ATTITUDE":
            roll = m.roll
            pitch = m.pitch