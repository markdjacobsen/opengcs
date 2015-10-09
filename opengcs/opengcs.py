#!/usr/bin/python

import sys
from ui.mainwindow import *
from PyQt5 import QtWidgets
import gcs_state


def main():
    # Create a root data object
    state = gcs_state.GCSState()

    # Launch the main application window
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(state)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()