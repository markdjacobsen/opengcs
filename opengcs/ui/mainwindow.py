# TODO: figure out appropriate times to rebuild routing table
# TODO: catch when widgets change their datasource

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

        # The MainWindow listens to these events from the GCS state, so it can update
        # widgets as appropriate
        self.state.on_focus_changed.append(self.catch_focus_changed)
        self.state.mav_network.on_network_changed.append(self.catch_network_changed)
        self.state.mav_network.on_mavlink_packet.append(self.forward_packets_to_widgets)

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

    def display_screen(self, screenNumber):
        """
        Display the given screen number, indexed from 0. 0 is the default screen.
        """
        # Erase the current screen
        for w in self.children():
            if isinstance(w,QDockWidget):
                self.removeDockWidget(w)

        # Erase the current mavlink routing table
        self._routing = {}

        screen = self.state.config.perspective['screen'][screenNumber]
        for w in screen['widget']:
            # Initialize and display each widget
            get_class = lambda x: globals()[x]            
            newWidget = get_class(w['type'])(self.state, self)
            newWidget.on_datasource_changed.append(self.catch_widget_datasource_changed)

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

        # We have a new set of widgets on screen, so need to rebuild the routing table
        # to forward mavlink packets to these widgets.
        self.build_routing_dictionary()


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

        # Update the combo boxes for focused object
        # TODO support sorting of focused MAV combo box. Sort keys?
        self.combo_focused_mav.blockSignals(True)
        self.combo_focused_mav.clear()
        for mavkey in self.state.mav_network.mavs:
            mav = self.state.mav_network.mavs[mavkey]
            v = QtCore.QVariant(mav)
            self.combo_focused_mav.addItem(mav.get_name(), v)
            if mav == self.state.focused_object:
                self.combo_focused_mav.setCurrentIndex(self.combo_focused_mav.count()-1)
        self.combo_focused_mav.blockSignals(False)

        # Notify all widgets
        for w in self.children():
            if isinstance(w, GCSWidget):
                w.catch_network_changed()

    def catch_focus_changed(self, object, component_id):

        # Notify all widgets that the focused datasource is changing
        for w in self.children():
            if isinstance(w, GCSWidget):
                w.catch_focus_changed(object, component_id)

        # Upate the routing table for mavlink packets
        self.build_routing_dictionary()

    def on_combo_focused_component(self):
        # _COMPOMENT implement on_combo_focused_component
        return

    def on_combo_focused_mav(self):

        idx = self.combo_focused_mav.currentIndex()
        mav = self.combo_focused_mav.itemData(idx).toPyObject()
        self.state.set_focus(mav)


    def create_debug(self):
        '''
        Create a debug menu. Only called if the 'debug' setting is TRUE
        '''
        self.menu_debug = self.menubar.addMenu('&Debug')

        self.action_debug_network = QAction('&Show MAV Network',self)
        self.action_debug_network.triggered.connect(self.on_debug_network)
        self.menu_debug.addAction(self.action_debug_network)

    def build_routing_dictionary(self):
        """
        This rebuilds the routing table, which keeps track of which widgets are listening to which
        system_ids. Any time a packet comes in, the main window forwards the packet to all widgets
        listening for that system_id.
        """
        self._routing = {}
        for i in range(0,254):
            self._routing[i] = []
        for w in self.children():
            if isinstance(w, GCSWidget):
                if w._track_focused:
                    if isinstance(self.state.focused_object, MAV) and (w._datasource_allowable & WidgetDataSource.SINGLE > 0):
                        self._routing[self.state.focused_object.system_id].append(w)
                    elif isinstance(self.state.focused_object, Swarm) and (w._datasource_allowable & WidgetDataSource.SWARM > 0):
                        for mav in self.state.focused_object.mavs:
                            self._routing[mav.system_id].append(w)

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

    def forward_packets_to_widgets(self, m):
        """
        This captures every mavlink packet traveling over the mav network. It forwards packets
        to widgets listening for specific system_ids.
        """
        system_id = m.get_header().srcSystem
        for w in self._routing[system_id]:
            w.process_messages(m)

            # This code block is used for performance testing. It sends many more packets,
            # to get a sense for how many mavs we can operate without straining the application.
            #for i in range(0,400):
            #    w.process_messages(m)

    def catch_widget_datasource_changed(self, widget, track_focused, object):
        """
        This event listens for a signal from widgets, indicating they are changing their
        datasource. That is a cue to rebuild the routing dictionary.
        """
        self.build_routing_dictionary()

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