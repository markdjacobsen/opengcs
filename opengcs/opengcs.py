#!/usr/bin/python

import sys
from ui.mainwindow import *
from PyQt4 import QtGui
import gcs_state
import os
import pyqtgraph as pg

global state

def gcsfile(filename):
    return gcsdir + '/' + filename

def main():

    # Create a root data object
    state = gcs_state.GCSState()
    state.path = os.path.dirname(__file__)

    # Launch the main application window
    app = QtGui.QApplication(sys.argv)
    app.setOrganizationName("Uplift Aeronautics")
    app.setOrganizationDomain("uplift.aero")
    app.setApplicationName("OpenGCS")
    app.setWindowIcon(QIcon(state.config.settings['appicon']))
    window = MainWindow(state)
    sys.exit(app.exec_())



__version__ = '0.0.1'
gcsdir = os.path.dirname(__file__)
if __name__ == '__main__':
    main()