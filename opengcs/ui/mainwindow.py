from PyQt4.QtGui import *
from dialogs import *
from ui.widgets.GCSWidget import *
from ui.widgets.GCSWidgetHUD import *
from ui.widgets.GCSWidgetMap import *
from ui.widgets.GCSWidgetMAVNetwork import *
from ui.widgets.GCSWidgetParameterList import *
from ui.widgets.GCSWidgetGauges import *
from PyQt4 import QtCore, QtGui
import functools

import gettext

class MainWindow(QMainWindow):
    def __init__(self, state):
        super(MainWindow, self).__init__()
        self.state = state
        self.initUI()

        # The MainWindow listens to these events from the GCS state, so it can update
        # widgets as appropriate
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
        if self.state.debug:
            self.create_debug()

        self.active_screen = 0
        self.display_screen(self.active_screen)

    def display_screen(self, screen_number):
        """
        Display the given screen number, indexed from 0. 0 is the default screen.
        """
        # Erase the current screen
        for w in self.children():
            if isinstance(w, QDockWidget):
                self.removeDockWidget(w)

        screen = self.state.config.perspective['screen'][screen_number]
        for w in screen['widget']:
            get_class = lambda x: globals()[x]            
            new_widget = get_class(w['type'])(self.state, self)
            location = w['location'].lower()
            if location == 'center':
                self.setCentralWidget(new_widget)
            elif location == 'left':
                self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, new_widget)
            elif location == 'right':
                self.addDockWidget(QtCore.Qt.RightDockWidgetArea, new_widget)
            elif location == 'top':
                self.addDockWidget(QtCore.Qt.TopDockWidgetArea, new_widget)
            else:
                self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, new_widget)

    def create_actions(self):
        """
        Create the PyQt actions used by the main window
        """

        self.action_settings = QAction(QIcon('art/48x48/applications-system-4.png'), '&Settings', self)
        self.action_settings.setStatusTip('Open the settings menu')
        self.action_settings.setToolTip(('Settings'))
        self.action_settings.triggered.connect(self.on_action_settings)

        self.action_connections = QAction(QIcon('art/48x48/network-globe.png'), '&Connections', self)
        self.action_connections.setStatusTip('Open connections dialog')
        self.action_connections.triggered.connect(self.on_action_connections)

        # TODO change 'load perspective' icon
        self.action_load_perspective = QAction(QIcon('art/48x48/network-globe.png'), '&Load Perspective', self)
        self.action_load_perspective.setStatusTip('Load perspective file')
        self.action_load_perspective.triggered.connect(self.on_action_load_perspective)

        # TODO change 'save perspective' icon
        self.action_save_perspective = QAction(QIcon('art/48x48/network-globe.png'), '&Save Perspective', self)
        self.action_save_perspective.setStatusTip('Save perspective file')
        self.action_save_perspective.triggered.connect(self.on_action_save_perspective)

        self.action_add_widget = QAction(QIcon('art/48x48/network-globe.png'), '&Add Widget', self)
        self.action_add_widget.setStatusTip('Add a widget to the current screen')
        self.action_add_widget.triggered.connect(self.on_action_add_widget)

        self.action_view_fullscreen = QAction('&Full Screen',self)
        self.action_view_fullscreen.setStatusTip('View OpenGCS in full screen mode')
        self.action_view_fullscreen.triggered.connect(self.on_action_view_fullscreen)
        self.action_view_fullscreen.setCheckable(True)

        self.actions_screens = []
        screen_number = 0
        for screen in self.state.config.perspective['screen']:
            action = QAction(QIcon(screen['icon']), screen['name'], self)
            action.setToolTip(screen['tooltip'])
            action.triggered.connect(functools.partial(self.on_action_screen,screen_number))
            action.setCheckable(True)
            self.actions_screens.append(action)
            screen_number = screen_number + 1
            # TODO add screen selection keyboard shortcuts
        self.actions_screens[0].setChecked(True)

    def create_toolbar(self):
        """
        Create the toolbar items used by the main window
        """
        self.toolbar = self.addToolBar('MainToolbar')
        self.toolbar.setObjectName("MainToolbar")
        self.toolbar.addAction(self.action_settings)
        self.toolbar.addAction(self.action_connections)

        for actionScreen in self.actions_screens:
            self.toolbar.addAction(actionScreen)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.toolbar.addWidget(spacer)
        self.label_focused_mav = QLabel("Focused MAV: ")
        self.combo_focused_mav = QComboBox()
        self.label_focused_component = QLabel("Focused Component: ")
        self.combo_focused_component = QComboBox()

        self.combo_focused_mav.currentIndexChanged.connect(self.on_combo_focused_mav)
        self.combo_focused_component.currentIndexChanged.connect(self.on_combo_focused_component)

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
        self.menu_file = self.menubar.addMenu('&File')
        self.menu_file.addAction(self.action_settings)

        self.menu_view = self.menubar.addMenu('&View')

        self.menu_view_choose_screen = QtGui.QMenu('Choose Screen',self)
        for action_screen in self.actions_screens:
            self.menu_view_choose_screen.addAction(action_screen)

        self.menu_view.addMenu(self.menu_view_choose_screen)
        self.menu_view.addAction(self.action_add_widget)
        self.menu_view.addAction(self.action_view_fullscreen)

        self.menu_mav = self.menubar.addMenu('&MAV')
        self.menu_mav.addAction(self.action_connections)

        self.show()

    def on_action_view_fullscreen(self):
        if self.action_view_fullscreen.isChecked():
            self.showFullScreen()
        else:
            self.showNormal()


    def on_action_settings(self):
        print("TODO on_action_settings")
        # TODO move FetchParameterHelp action to somewhere that makes sense
        self.state.fetch_parameter_help()

    def on_action_connections(self):
        d = ConnectionsDialog(self.state)
        d.exec_()

    def on_action_screen(self, screenNumber):
        self.active_screen = screenNumber
        self.display_screen(self.active_screen)
        for i in range(0,len(self.actions_screens)):
            action_screen = self.actions_screens[i]
            if i == screenNumber:
                action_screen.setChecked(True)
            else:
                action_screen.setChecked(False)

    def on_action_save_perspective(self):
        # TODO on_action_save_perspective
        print("TODO onActionSavePerspective")

    def on_action_load_perspective(self):
        # TODO on_action_load_perspective
        print("TODO onActionLoadPerspective")

    def on_action_add_widget(self):
        # TODO on_action_add_widget
        print("TODO onActionAddWidget")
        d = AddWidgetDialog(self.state)
        d.exec_()
        d.show()

    def catch_network_changed(self):

        # Update combo boxes
        # TODO support sorting of focused MAV combo box. Sort keys?
        print("mainwindow.catch_network_changed()")
        self.combo_focused_mav.blockSignals(True)
        self.combo_focused_mav.clear()
        #print("MAV count: " + str(len(self.state.mav_network.mavs)))
        for mavkey in self.state.mav_network.mavs:
            print("mav found")
            mav = self.state.mav_network.mavs[mavkey]
            v = QtCore.QVariant(mav)
            self.combo_focused_mav.addItem(mav.get_name(), v)
            if mav == self.state.focused_mav:
                self.combo_focused_mav.setCurrentIndex(self.combo_focused_mav.count()-1)
        self.combo_focused_mav.blockSignals(False)

        # Notify all widgets
        for w in self.children():
            if isinstance(w, GCSWidget):
                w.catch_network_changed()

    def catch_focused_mav_changed(self):

        # Notify all widgets
        for w in self.children():
            if isinstance(w, GCSWidget):
                w.catch_focused_mav_changed()

    def catch_focused_component_changed(self):
        # TODO implement catch_focused_component_changed
        print("mainwindow.catch_focused_component_changed()")

    def on_combo_focused_component(self):
        # TODO implement on_combo_focused_component
        return

    def on_combo_focused_mav(self):

        print("main.window_oncombo_focused_mav()")
        idx = self.combo_focused_mav.currentIndex()
        mav = self.combo_focused_mav.itemData(idx).toPyObject()
        self.state.set_focused_mav(mav)


    def create_debug(self):
        '''
        Create a debug menu. Only called if the 'debug' setting is TRUE
        '''
        self.menu_debug = self.menubar.addMenu('&Debug')

        self.action_debug_network = QAction('&Show MAV Network',self)
        self.action_debug_network.triggered.connect(self.on_debug_network)
        self.menu_debug.addAction(self.action_debug_network)

    def on_debug_network(self):

        print("MAV Network")
        print("-----------")
        for conn in self.state.mav_network.connections:
            print conn.get_name()

            for mavkey in conn.mavs:
                mav = conn.mavs[mavkey]
                print "  " + mav.get_name()

                # TODO when implementing components
                #for component in mav:
                #    print "  " + component.get_name()

"""
These methods use the QSettings system to load window geometry, but I still
haven't decided if they're the right solution to persist window settings.

    def closeEvent(self, e):
        # Use the QSettings system to store window geometry in the registry
        settings = QSettings()
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        super(MainWindow, self).closeEvent(e)

    def readSettings(self):
        print("readSettings")
        settings = QSettings()
        self.restoreGeometry(settings.value("myWidget/geometry").toByteArray());
        self.restoreState(settings.value("myWidget/windowState").toByteArray());
"""
