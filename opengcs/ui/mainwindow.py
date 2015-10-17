from PyQt4.QtGui import *
from dialogs import *
from ui.widgets.GCSWidget import *
from ui.widgets.GCSWidgetHUD import *
from ui.widgets.GCSWidgetMap import *
from ui.widgets.GCSWidgetMAVNetwork import *
from ui.widgets.GCSWidgetParameterList import *
from PyQt4 import QtCore, QtGui
import functools

import gettext

class MainWindow(QMainWindow):
    def __init__(self, state):
        super(MainWindow, self).__init__()
        self.state = state
        self.initUI()

        self.state.on_focused_mav_changed.append(self.catch_focused_mav_changed)
        self.state.on_focused_component_changed.append(self.catch_focused_component_changed)
        self.state.mav_network.on_network_changed.append(self.catch_network_changed)

    def initUI(self):
        """
        Initialize the user interface for the main window
        """
        self.setGeometry(300, 300, 1000, 500)
        self.setWindowTitle(self.state.config.settings['windowtitle'])
        self.setWindowIcon(QIcon(self.state.config.settings['windowicon']))

        self.create_actions()
        self.create_toolbar()
        self.create_statusbar()
        self.create_menu()

        self.activeScreen = 0
        self.display_screen(self.activeScreen)

    def display_screen(self, screenNumber):
        """
        Display the given screen number, indexed from 0. 0 is the default screen.
        """
        # Erase the current screen
        for w in self.children():
            if isinstance(w,QDockWidget):
                self.removeDockWidget(w)

        screen = self.state.config.perspective['screen'][screenNumber]
        for w in screen['widget']:
            get_class = lambda x: globals()[x]            
            newWidget = get_class(w['type'])(self.state, self)
            location = w['location'].lower()
            if location == 'center':
                self.setCentralWidget(newWidget)
            elif location == 'left':
                self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, newWidget)
            elif location == 'right':
                self.addDockWidget(QtCore.Qt.RightDockWidgetArea, newWidget)
            elif location == 'top':
                self.addDockWidget(QtCore.Qt.TopDockWidgetArea, newWidget)
            else:
                self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, newWidget)

    def create_actions(self):
        """
        Create the PyQt actions used by the main window
        """

        self.actionSettings = QAction(QIcon('art/48x48/applications-system-4.png'), '&Settings', self)
        self.actionSettings.setStatusTip('Open the settings menu')
        self.actionSettings.setToolTip(('Settings'))
        self.actionSettings.triggered.connect(self.on_action_settings)

        self.actionConnections = QAction(QIcon('art/48x48/network-globe.png'), '&Connections', self)
        self.actionConnections.setStatusTip('Open connections dialog')
        self.actionConnections.triggered.connect(self.on_action_connections)

        # TODO change 'load perspective' icon
        self.actionLoadPerspective = QAction(QIcon('art/48x48/network-globe.png'), '&Load Perspective', self)
        self.actionLoadPerspective.setStatusTip('Load perspective file')
        self.actionLoadPerspective.triggered.connect(self.on_action_load_perspective)

        # TODO change 'save perspective' icon
        self.actionSavePerspective = QAction(QIcon('art/48x48/network-globe.png'), '&Save Perspective', self)
        self.actionSavePerspective.setStatusTip('Save perspective file')
        self.actionSavePerspective.triggered.connect(self.on_action_save_perspective)

        self.actionAddWidget = QAction(QIcon('art/48x48/network-globe.png'), '&Add Widget', self)
        self.actionAddWidget.setStatusTip('Add a widget to the current screen')
        self.actionAddWidget.triggered.connect(self.on_action_add_widget)

        self.action_view_fullscreen = QAction('&Full Screen',self)
        self.action_view_fullscreen.setStatusTip('View OpenGCS in full screen mode')
        self.action_view_fullscreen.triggered.connect(self.on_action_view_fullscreen)
        self.action_view_fullscreen.setCheckable(True)

        self.actionsScreens = []
        screenNumber = 0
        for screen in self.state.config.perspective['screen']:
            action = QAction(QIcon(screen['icon']), screen['name'], self)
            action.setToolTip(screen['tooltip'])
            action.triggered.connect(functools.partial(self.on_action_screen,screenNumber))
            self.actionsScreens.append(action)
            screenNumber = screenNumber + 1
            # TODO add screen selection keyboard shortcuts

    def create_toolbar(self):
        """
        Create the toolbar items used by the main window
        """
        self.toolbar = self.addToolBar('MainToolbar')
        self.toolbar.addAction(self.actionSettings)
        self.toolbar.addAction(self.actionConnections)

        for actionScreen in self.actionsScreens:
            self.toolbar.addAction(actionScreen)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.toolbar.addWidget(spacer)
        self.label_focused_mav = QLabel("Focused MAV: ")
        self.combo_focused_mav = QComboBox()
        self.label_focused_component = QLabel("Focused Component: ")
        self.combo_focused_component = QComboBox()

        self.toolbar.addWidget(self.label_focused_mav)
        self.toolbar.addWidget(self.combo_focused_mav)
        self.toolbar.addWidget(self.label_focused_component)
        self.toolbar.addWidget(self.combo_focused_component)


    def create_statusbar(self):
        """
        Create the status bar used by the main window
        """
        self.statusBar().showMessage('')

    def create_menu(self):
        """
        Create the menu used by the main window
        """
        self.menubar = self.menuBar()
        self.menuFile = self.menubar.addMenu('&File')
        self.menuFile.addAction(self.actionSettings)

        self.menuView = self.menubar.addMenu('&View')

        self.chooseScreenMenu = QtGui.QMenu('Choose Screen',self)
        for actionScreen in self.actionsScreens:
            self.chooseScreenMenu.addAction(actionScreen)

        self.menuView.addMenu(self.chooseScreenMenu)
        self.menuView.addAction(self.actionAddWidget)
        self.menuView.addAction(self.action_view_fullscreen)

        self.menuMAV = self.menubar.addMenu('&MAV')
        self.menuMAV.addAction(self.actionConnections)

        self.show()

    def on_action_view_fullscreen(self):
        if self.action_view_fullscreen.isChecked():
            self.showFullScreen()
        else:
            self.showNormal()


    def on_action_settings(self):
        print("Action activated")
        # TODO move FetchParameterHelp action to somewhere that makes sense
        self.state.fetch_parameter_help()

    def on_action_connections(self):
        d = ConnectionsDialog(self.state)
        d.exec_()

    def on_action_screen(self, screenNumber):
        print("DEBUG onActionScreen " + str(screenNumber))
        self.activeScreen = screenNumber
        self.display_screen(self.activeScreen)

    def on_action_save_perspective(self):
        # TODO onActionSavePerspective
        print("TODO onActionSavePerspective")

    def on_action_load_perspective(self):
        # TODO onActionLoadPerspective
        print("TODO onActionLoadPerspective")

    def on_action_add_widget(self):
        # TODO onActionAddWidget
        print("TODO onActionAddWidget")
        d = AddWidgetDialog(self.state)
        d.exec_()
        d.show()

    def catch_network_changed(self):
        for w in self.children():
            if isinstance(w, GCSWidget):
                w.catch_network_changed()


    def catch_focused_mav_changed(self):
        for w in self.children():
            if isinstance(w, GCSWidget):
                w.catch_focused_mav_changed()

    def catch_focused_component_changed(self):
        print("mainwindow.catch_focused_component_changed()")

