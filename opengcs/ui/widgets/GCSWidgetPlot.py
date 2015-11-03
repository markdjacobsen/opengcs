from GCSWidget import *
from PyQt4.QtGui import *
from PyQt4 import QtCore
from pymavlink import mavutil
import pyqtgraph as pg
import numpy as np


class GCSWidgetPlot (GCSWidget):

    widget_name_plaintext = "Plot"

    def __init__(self, state, parent):

        super(GCSWidgetPlot, self).__init__(state, parent)
        self.set_datasource_allowable(WidgetDataSource.SINGLE|WidgetDataSource.SWARM)
        self.setMinimumSize(300, 300)
        self.init_ui()

    def init_ui(self):

        self.startTime = pg.ptime.time()

        self.data_x = np.arange(100)
        #self.data_x = np.zeros(shape=(1,1000))
        self.data_y = np.arange(100)
        self.plot_widget = pg.PlotWidget()
        self.curve_y = self.plot_widget.plot(self.data_y)
        self.setWidget(self.plot_widget)

        # Example of how to plot multiple curves on one plotWidget
        #for i in range(3):
        #    plotWidget.plot(x, y[i], pen=(i,3))

    def resizeEvent(self, event):

        return

    def refresh(self):

        super(GCSWidgetPlot, self).refresh()

    def process_messages(self, m):
        # This is a dummy handler to illustrate how message processing is done.
        # See the mavlink protocol for message types and member variables:
        # https://pixhawk.ethz.ch/mavlink/
        mtype = m.get_type()
        if mtype == "VFR_HUD":
            self.heading = m.heading

            now = pg.ptime.time()
            self.data_x[:-1] = self.data_x[1:]
            self.data_x[-1] = now

            self.data_y[:-1] = self.data_y[1:]
            self.data_y[-1] = self.heading
            self.curve_y.setData(self.data_y)