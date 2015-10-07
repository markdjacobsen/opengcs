#!/usr/bin/python

import sys
from ui.mainwindow import *
from PyQt5 import QtWidgets


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()