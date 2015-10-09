from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication
from PyQt5.QtGui import QIcon
from dialogs import *

import gettext

class MainWindow(QMainWindow):
    def __init__(self, state):
        super(MainWindow, self).__init__()
        self.state = state
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 1000, 500)
        self.setWindowTitle("opengcs - MAV Ground Station")
        self.statusBar().showMessage('TODO implement status bar')

        # Template for how to build a menu item
        testAction = QAction(QIcon('art/48x48/applications-system-4.png'), '&Foo', self)
        testAction.setShortcut('Ctrl+Q')
        testAction.setStatusTip('Click to exit the application')
        testAction.setToolTip(('Exit application'))
        #testAction.triggered.connect(qApp.quit)
        testAction.triggered.connect(self.exampleSlot)

        actionConnections = QAction(QIcon('exit.png'), '&Connections', self)
        actionConnections.setStatusTip('Open connections dialog')
        actionConnections.triggered.connect(self.on_action_connections)

        # Toolbar
        self.toolbar = self.addToolBar('Foo')
        self.toolbar.addAction(testAction)


        menubar = self.menuBar()
        menuFile = menubar.addMenu('&File')
        menuFile.addAction(testAction)

        menuView = menubar.addMenu('&View')

        menuMAV = menubar.addMenu('&MAV')
        menuMAV.addAction(actionConnections)



        self.show()

    def exampleSlot(self):
        print("Action activated")

    def on_action_connections(self):
        # TODO
        d = ConnectionsDialog(self.state)
        d.exec_()
        d.show()

