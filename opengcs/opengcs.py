#!/usr/bin/python

import sys
from ui.mainwindow import *
from PyQt4 import QtGui
import gcs_state
import os


def main():
    # Create a root data object
    state = gcs_state.GCSState()
    state.path = os.path.dirname(__file__)

    # Launch the main application window
    app = QtGui.QApplication(sys.argv)
    app.setWindowIcon(QIcon(state.config.settings['appicon']))
    window = MainWindow(state)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()