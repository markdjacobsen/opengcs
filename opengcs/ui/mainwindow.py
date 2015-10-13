from PyQt4.QtGui import *
from dialogs import *
from ui.widgets.GCSWidget import *
from ui.widgets.GCSWidgetHUD import *
from ui.widgets.GCSWidgetMap import *
from PyQt4 import QtCore, QtGui
import functools

import gettext

class MainWindow(QMainWindow):
    def __init__(self, state):
        super(MainWindow, self).__init__()
        self.state = state
        self.initUI()

    def initUI(self):
        """
        Initialize the user interface for the main window
        """
        self.setGeometry(300, 300, 1000, 500)
        self.setWindowTitle(self.state.config.settings['windowtitle'])
        self.setWindowIcon(QIcon(self.state.config.settings['windowicon']))

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
        """
        Create the PyQt actions used by the main window
        """
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

        self.screenActions = []
        screenNumber = 0
        for screen in self.state.config.perspective['screen']:
            action = QAction(QIcon(screen['icon']), screen['name'], self)
            action.setToolTip(screen['tooltip'])
            action.triggered.connect(functools.partial(self.onActionScreen,screenNumber))
            self.screenActions.append(action)
            screenNumber = screenNumber + 1

    def createToolBar(self):
        """
        Create the toolbar items used by the main window
        """
        self.toolbar = self.addToolBar('MainToolbar')
        self.toolbar.addAction(self.actionSettings)
        self.toolbar.addAction(self.actionConnections)

        for screenAction in self.screenActions:
            self.toolbar.addAction(screenAction)

    def createStatusBar(self):
        """
        Create the status bar used by the main window
        """
        self.statusBar().showMessage('')

    def createMenu(self):
        """
        Create the menu used by the main window
        """
        self.menubar = self.menuBar()
        self.menuFile = self.menubar.addMenu('&File')
        self.menuFile.addAction(self.actionSettings)

        self.menuView = self.menubar.addMenu('&View')

        self.chooseScreenMenu = QtGui.QMenu('Choose Screen',self)
        for screenAction in self.screenActions:
            self.chooseScreenMenu.addAction(screenAction)

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

    def onActionScreen(self, screenNumber):
        # TODO
        print("TODO onActionScreen " + str(screenNumber))

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
        d.exec_()
        d.show()


