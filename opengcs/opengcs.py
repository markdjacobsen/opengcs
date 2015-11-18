#!/usr/bin/python

import sys
from ui.mainwindow import *
from PyQt4 import QtGui
import gcs_state
import os
import pyqtgraph as pg

global state

# Input is a relative filename to the opengcs directory (i.e. art/48x48/toolbar_screen.jpg
# Output is an absolute path
def gcsfile(filename):
    # Convert filename to str() in case gcsfile() is passed a QString
    return os.path.join(gcsdir, str(filename))

# Input is an absolute filename
# Output is a relative filename to the opengcs directory
def relfile(filename):
    return os.path.relpath(str(filename), gcsdir)

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