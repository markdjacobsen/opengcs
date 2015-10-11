from PyQt4.QtGui import *
from dialogs import *
from ui.widgets.GCSWidget import *
from ui.widgets.GCSWidgetHUD import *
from ui.widgets.GCSWidgetMap import *
from PyQt4 import QtCore, QtGui

import gettext

class MainWindow(QMainWindow):
    def __init__(self, state):
        super(MainWindow, self).__init__()
        self.state = state
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 1000, 500)
        self.setWindowTitle("opengcs - MAV Ground Station")

        self.createActions()
        self.createToolBar()
        self.createStatusBar()
        self.createMenu()


        # Widgets
        widgets = []
        for i in range(0,3):
            widgets.append(GCSWidget("widget " + str(i), self))
        widgets.append(GCSWidgetHUD("HUD",self))
        widgets.append(GCSWidgetMap("HUD",self))
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, widgets[3]);
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, widgets[4]);
        for i in range(0,2):
            self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, widgets[i]);

    def createActions(self):
        # Template for how to build a menu item
        self.actionSettings = QAction(QIcon('art/48x48/applications-system-4.png'), '&Settings', self)
        #testAction.setShortcut('Ctrl+Q')
        self.actionSettings.setStatusTip('Open the settings menu')
        self.actionSettings.setToolTip(('Settings'))
        #testAction.triggered.connect(qApp.quit)
        self.actionSettings.triggered.connect(self.onSettingsAction)

        self.actionConnections = QAction(QIcon('art/48x48/network-globe.png'), '&Connections', self)
        self.actionConnections.setStatusTip('Open connections dialog')
        self.actionConnections.triggered.connect(self.onActionConnections)

        self.actionScreen1 = QAction('&1', self)
        self.actionScreen1.setStatusTip('View screen 1')
        self.actionScreen1.triggered.connect(self.onActionScreen1)

        self.actionScreen2 = QAction('&2', self)
        self.actionScreen2.setStatusTip('View screen 2')
        self.actionScreen2.triggered.connect(self.onActionScreen2)

        # TODO change icon
        self.actionLoadPerspective = QAction(QIcon('art/48x48/network-globe.png'), '&Load Perspective', self)
        self.actionLoadPerspective.setStatusTip('Load perspective file')
        self.actionLoadPerspective.triggered.connect(self.onActionLoadPerspective)

        # TODO change icon
        self.actionSavePerspective = QAction(QIcon('art/48x48/network-globe.png'), '&Save Perspective', self)
        self.actionSavePerspective.setStatusTip('Save perspective file')
        self.actionSavePerspective.triggered.connect(self.onActionSavePerspective)

        # TODO add widget
        self.actionAddWidget = QAction(QIcon('art/48x48/network-globe.png'), '&Add Widget', self)
        self.actionAddWidget.setStatusTip('Add a widget to the current screen')
        self.actionAddWidget.triggered.connect(self.onActionAddWidget)


    def createToolBar(self):
        # Toolbar
        self.toolbar = self.addToolBar('MainToolbar')
        self.toolbar.addAction(self.actionSettings)
        self.toolbar.addAction(self.actionConnections)
        self.toolbar.addAction(self.actionScreen1)
        self.toolbar.addAction(self.actionScreen2)

    def createStatusBar(self):
        self.statusBar().showMessage('')

    def createMenu(self):

        self.menubar = self.menuBar()
        self.menuFile = self.menubar.addMenu('&File')
        self.menuFile.addAction(self.actionSettings)

        self.menuView = self.menubar.addMenu('&View')

        self.chooseScreenMenu = QtGui.QMenu('Choose Screen',self)
        self.chooseScreenMenu.addAction(self.actionScreen1)
        self.chooseScreenMenu.addAction(self.actionScreen2)

        self.menuView.addMenu(self.chooseScreenMenu)
        self.menuView.addAction(self.actionAddWidget)

        self.menuMAV = self.menubar.addMenu('&MAV')
        self.menuMAV.addAction(self.actionConnections)

        self.show()

    def onSettingsAction(self):
        print("Action activated")

    def onActionConnections(self):
        # TODO
        d = ConnectionsDialog(self.state)
        d.exec_()
        d.show()

    def onActionScreen1(self):
        # TODO
        print("TODO onActionScreen1")

    def onActionScreen2(self):
        # TODO
        print("TODO onActionScreen2")

    def onActionSavePerspective(self):
        # TODO
        print("TODO onActionSavePerspective")

    def onActionLoadPerspective(self):
        # TODO
        print("TODO onActionLoadPerspective")

    def onActionAddWidget(self):
        # TODO
        print("TODO onActionAddWidget")
        d = AddWidgetDialog(self.state)
        d.ListWidgets()
        #d.exec_()
        #d.show()


