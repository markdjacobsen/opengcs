# -*- coding: utf-8 -*-

from datetime import timedelta
from math import degrees
from GCSWidget import *
from PyQt4.QtGui import *
from PyQt4 import QtCore
from pymavlink import mavutil
from opengcs import *

# TODO window geometry is saved differently for each screen
# TODO need to figure out how to remove toolbar
# TODO toolbar needs to update after editing screens
# TODO delete widgets from perspective files when closed
# TODO HUD scale factors will need to vary based on the size of the widget

# This is a reusable widget for displaying a horizon line, given roll and pitch.
# It is used by the GCSWidgetHud widget below, and is also used in the GCSWidgetConsole.
class HorizonWidget (QWidget):

    def __init__(self, parent):
        super(HorizonWidget, self).__init__(parent)
        self.parent = parent
        self.roll_deg = 0
        self.pitch_deg = 0
        self.initUI()
        self.show()


    def initUI(self):
        """
        Initialize the user interface for the main window
        """
        self.setMinimumSize(75, 75)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setFixedSize(75, 75)
        self.img = QPixmap(gcsfile('art/hud/horizon_back.png'))

    def paintEvent(self, QPaintEvent):

        # During a paint event, we essentially translate and rotate the coordinate system
        # and then draw a scaled version of the horizon. We apply some scaling/zooming
        # because the image needs to be bigger than the widget, so no whitepsace shows
        # around the edges during rotations.
        painter = QPainter(self)#.parent)
        painter.save()
        painter.translate(self.width()/2, self.height()/2 + (self.pitch_deg*5))
        painter.rotate(-self.roll_deg)

        source = QRectF(0, 0, self.img.width(), self.img.height())
        dest = QRectF(-self.width()*2, -self.height()*2, self.width()*4, self.height()*4)
        painter.drawPixmap(dest, self.img, source)
        painter.restore()

class GCSWidgetHUD (GCSWidget):

    widget_name_plaintext = "HUD"

    def __init__(self, state, parent):

        super(GCSWidgetHUD, self).__init__(state, parent)
        self.set_datasource_allowable(WidgetDataSource.SINGLE)
        self.setWindowTitle("HUD")
        self.setMinimumSize(300, 300)
        #self.setMaximumSize(400, 822)

        self.init_ui()

    def init_ui(self):

        # HUD assets
        #img_horizon_bg = QPixmap(path.join(self.asset_path, 'horizon_back.png'))
        #img_pitch_ladder = QPixmap(path.join(self.asset_path, 'horizon_back.png'))
        #img_roll_caret = QPixmap(path.join(self.asset_path, 'horizon_back.png'))

        self.horizon = HorizonWidget(self)
        self.horizon.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # HUD labels
        #self.label_horizon_bg = QLabel("", self)
        #self.label_horizon_bg.setScaledContents(True)
        #self.label_horizon_bg.setPixmap(img_horizon_bg)

        # Labels on artificial horizon
        self.label_throttle = QLabel("Thr 000%", self)
        self.label_heading = QLabel("Hdg 000°", self)
        #self.label_roll = QLabel("Roll -000.00°", self)
        #self.label_pitch = QLabel("Pitch -000.00°", self)
        self.label_rssi = QLabel("RSSI 100%", self)
        self.label_uptime = QLabel("T 0:00:00", self)
        self.label_airspeed = QLabel("AS 000.00m/s", self)
        self.label_gndspeed = QLabel("GS 000.00m/s", self)
        self.label_gps_sats = QLabel("GPS Sats 00", self)
        self.label_gps_fix = QLabel("GPS Fix 0", self)
        self.label_gps_lat = QLabel("Lat 000°00'00\"", self)
        self.label_gps_lon = QLabel("Lon 000°00'00\"", self)

        # Labels for quick info
        self.label_altitude_txt = QLabel("Altitude", self)
        self.label_altitude_val = QLabel("-0000.00m", self)
        self.label_gndspeed_txt = QLabel("GroundSpeed", self)
        self.label_gndspeed_val = QLabel("000.00m/s", self)
        self.label_dist_wp_txt = QLabel("Dist to WP", self)
        self.label_dist_wp_val = QLabel("0000.00m", self)
        #self.label_yaw_txt = QLabel("Yaw", self)
        #self.label_yaw_val = QLabel("-000.00°", self)
        self.label_climb_txt = QLabel("Vertical Speed", self)
        self.label_climb_val = QLabel("-000.00m/s", self)
        self.label_dist_mav_txt = QLabel("Dist to MAV", self)
        self.label_dist_mav_val = QLabel("0000.00m", self)

        self.refresh()

    def resizeEvent(self, event):

        self.refresh()

    def refresh(self):

        #print("refresh()")

        super(GCSWidgetHUD, self).refresh()


        w = self.geometry().width()
        h = self.geometry().height() - 22  # 22 pixels for title bar

        self.horizon.setFixedWidth(w)
        self.horizon.setFixedHeight(h)

        self.horizon.update()
        #self.label_horizon_bg.setGeometry(1, 22, w-2, h/3-2)

        self.label_throttle.move(3, 16)
        self.label_heading.move(w/2-28, 16)
        #self.label_roll.move(w/2-40, 50)
        #self.label_pitch.move(w/2-45, h/6)
        self.label_rssi.move(w-73, 16)
        self.label_uptime.move(w-64, 31)
        self.label_airspeed.move(3, h/3-20)
        self.label_gndspeed.move(3, h/3-5)
        self.label_gps_sats.move(w-82, h/3-50)
        self.label_gps_fix.move(w-65, h/3-35)
        self.label_gps_lat.move(w-102, h/3-20)
        self.label_gps_lon.move(w-106, h/3-5)

        self.label_altitude_txt.move(3, h/3+20)
        self.label_altitude_val.move(3, h/3+35)
        self.label_gndspeed_txt.move(w-95, h/3+20)
        self.label_gndspeed_val.move(w-74, h/3+35)
        self.label_dist_wp_txt.move(3, h/3+60)
        self.label_dist_wp_val.move(3, h/3+75)
        #self.label_yaw_txt.move(w-30, h/3+60)
        #self.label_yaw_val.move(w-57, h/3+75)
        self.label_climb_txt.move(3, h/3+100)
        self.label_climb_val.move(3, h/3+115)
        self.label_dist_mav_txt.move(w-83, h/3+100)
        self.label_dist_mav_val.move(w-69, h/3+115)

    def _dec2dms(self, val):
        """
        Converts a value to decimal, minutes and seconds.
        :param val: int or float
        :return: decs, mins, secs as integers
        """

        mins, secs = divmod(val*3600, 60)
        decs, mins = divmod(mins, 60)

        return int(decs), int(mins), int(secs)

    def process_messages(self, m):
        # This is a dummy handler to illustrate how message processing is done.
        # See the mavlink protocol for message types and member variables:
        # https://pixhawk.ethz.ch/mavlink/

        mtype = m.get_type()
        #print(mtype)

        if mtype == "VFR_HUD":
            self.label_airspeed.setText("AS {:.2f}m/s".format(m.airspeed))
            self.label_gndspeed.setText("GS {:.2f}m/s".format(m.groundspeed))
            self.label_gndspeed_val.setText("{:.2f}m/s".format(m.groundspeed))
            self.label_heading.setText("Hdg {:.0f}".format(m.heading))
            self.label_throttle.setText("Thr {:.0%}".format(m.throttle))
            self.label_altitude_val.setText("{:.2f}m".format(m.alt))
            self.label_climb_val.setText("{:.2f}".format(m.climb))

        if mtype == "ATTITUDE":
            self.horizon.roll_deg = degrees(m.roll)
            self.horizon.pitch_deg = degrees(m.pitch)

            #self.label_roll.setText("Roll {:.2f}°".format(degrees(m.roll)))
            #self.label_pitch.setText("Pitch {:.2f}°".format(degrees(m.pitch)))
            #self.label_yaw_val.setText("{:.2f}".format(degrees(m.yaw)))
            #rollspeed = m.rollspeed
            #pitchspeed = m.pitchspeed
            #yawspeed = m.yawspeed
            self.horizon.update()

        if mtype == "SYSTEM_TIME":
            self.label_uptime.setText("T {}".format(timedelta(seconds=m.time_boot_ms/1000)))

        if mtype == "SYS_STATUS":
            voltage = m.voltage_battery
            current = m.current_battery
            remaining = m.battery_remaining
            droprate = m.drop_rate_comm
            load = m.load

        if mtype == "GPS_RAW_INT":
            self.label_gps_sats.setText("GPS Sats {}".format(m.satellites_visible))
            self.label_gps_fix.setText("GPS Fix {}".format(m.fix_type))
            gps_lat_dec = m.lat / 10000000.0
            self.label_gps_lat.setText("Lat {}°{}'{}\"".format(*self._dec2dms(gps_lat_dec)))
            gps_lon_dec = m.lon / 10000000.0
            self.label_gps_lon.setText("Lon {}°{}'{}\"".format(*self._dec2dms(gps_lon_dec)))
            gps_hdop = m.eph / 100.0
            gps_vdop = m.epv / 100.0
            gps_alt = m.alt / 1000.0

        if mtype == "NAV_CONTROLLER_OUTPUT":
            self.label_dist_wp_val.setText("{:.2f}m".format(m.wp_dist))
