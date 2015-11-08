# TODO: figure out appropriate times to rebuild routing table
# TODO: catch when widgets change their datasource
# TODO: support screen ordering
# TODO: fix disappearing toolbars for widgets

# Notes
#
# The main window includes a menu, toolbar, statusbar, and a widget area. OpenGCS supports multiple "screens"
# filled with widgets, and screens can be selected from the toolbar. The mainwindow class handles switching
# between screens and displaying the appropriate widgets.
#
# The mainwindow class also takes responsibility for saving/restoring settings between sessions, using the
# QSettings architecture. "Window settings" include data about window geometry and the various screens.
# "Screen settings" include the details of a particular screen, including the settings for each widget
# on that screen.
#
# The main window also takes responsibility for forwarding mavlink packets from the MAV network to the
# appropriate widgets. It maintains a routing dictionary indicating which widgets are listening for
# which system ids.

from PyQt4.QtGui import *
from dialogs import *
from ui.widgets.GCSWidget import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from gcs_state import *
import shutil
import functools
import os.path

import gettext

class Screen:
    """
    This class contains information for a "Screen." The main window can have multiple "screens", which can be
    selected from the toolbar
    """
    def __init__(self, name='New Screen', iconfile='art/48x48/toolbar_screen.png', tooltip='', statustip='', order=0, uuid=None):
        if uuid:
            self.uuid = uuid
        else:
            self.uuid = QUuid.createUuid().toString()
        self.name = name
        self.iconfile = iconfile
        self.tooltip = tooltip
        self.statustip = statustip
        self.order = order


class MainWindow(QMainWindow):
    def __init__(self, state):
        super(MainWindow, self).__init__()
        self.state = state
        self.screens = []
        self.toolbar = None

        # Load autosave.ini, or create a new one based on default.ini
        if not os.path.isfile('ui/perspectives/autosave.ini'):
            shutil.copyfile('ui/perspectives/default.ini', 'ui/perspectives/autosave.ini')
        self.perspective = QSettings('ui/perspectives/autosave.ini', QSettings.IniFormat)

        self.load_widget_library()
        self.initUI()
        self.show()

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
        self.active_screen = 0
        self.refresh()

    def refresh(self):

        self.read_window_settings()
        self.create_actions()
        self.display_active_screen()

    def display_active_screen(self):
        """
        Display the widgets for the active screen.
        """
        # Erase all widgets on screen
        for w in self.children():
            if isinstance(w,QDockWidget):
                self.removeDockWidget(w)

        # Load widget/layout info for the current screen
        self.read_screen_settings()
        self.create_toolbar()
        self.create_menu()
        self.create_statusbar()

        # We have a new set of widgets on screen, so need to rebuild the routing table
        # to forward mavlink packets to these widgets.
        self.build_routing_dictionary()


    def create_actions(self):
        """
        Create the PyQt actions used by the main window
        """

        self.action_settings = QAction(QIcon('art/48x48/toolbar_settings.png'), '&Settings', self)
        self.action_settings.setStatusTip('Open the settings menu')
        self.action_settings.setToolTip(('Settings'))
        self.action_settings.triggered.connect(self.on_action_settings)

        self.action_connections = QAction(QIcon('art/48x48/toolbar_connections.png'), '&Connections', self)
        self.action_connections.setStatusTip('Open connections dialog')
        self.action_connections.triggered.connect(self.on_action_connections)

        # TODO change 'load perspective' icon
        self.action_load_perspective = QAction('&Load Perspective', self)
        self.action_load_perspective.setStatusTip('Load perspective file')
        self.action_load_perspective.triggered.connect(self.on_action_load_perspective)

        # TODO change 'save perspective' icon
        self.action_save_perspective = QAction('&Save Perspective', self)
        self.action_save_perspective.setStatusTip('Save perspective file')
        self.action_save_perspective.triggered.connect(self.on_action_save_perspective)

        self.action_edit_perspective = QAction('&Edit Perspective', self)
        self.action_edit_perspective.setStatusTip('Edit the current perspective')
        self.action_edit_perspective.triggered.connect(self.on_action_edit_perspective)

        self.action_add_widget = QAction('&Add Widget', self)
        self.action_add_widget.setStatusTip('Add a widget to the current screen')
        self.action_add_widget.triggered.connect(self.on_action_add_widget)

        self.action_view_fullscreen = QAction('&Full Screen',self)
        self.action_view_fullscreen.setStatusTip('View OpenGCS in full screen mode')
        self.action_view_fullscreen.triggered.connect(self.on_action_view_fullscreen)
        self.action_view_fullscreen.setCheckable(True)

        self.action_add_screen = QAction('Edit &Screens', self)
        self.action_add_screen.setStatusTip('Edit the screens in this perspective')
        self.action_add_screen.triggered.connect(self.on_action_edit_screens)


        # Build a list of actions corresponding to the list of screens
        self.actions_screens = []
        screen_number = 0
        for screen in self.screens:
            action = QAction(QIcon(screen.iconfile), screen.name, self)
            action.setToolTip(screen.tooltip)
            action.setStatusTip(screen.statustip)
            action.triggered.connect(functools.partial(self.on_action_screen,screen_number))
            action.setCheckable(True)
            self.actions_screens.append(action)
            screen_number = screen_number + 1
            # TODO add screen selection keyboard shortcuts

        self.actions_screens[self.active_screen].setChecked(True)

    def create_toolbar(self):
        """
        Create the toolbar items used by the main window
        """

        if self.toolbar:
            self.removeToolBar(self.toolbar)

        self.toolbar = self.addToolBar('MainToolBar')
        self.toolbar.setObjectName("MainToolBar")

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

        self.populate_focus_combobox()
        #self.toolbar.addWidget(self.label_focused_component)
        #self.toolbar.addWidget(self.combo_focused_component)

    def create_statusbar(self):
        """
        Create the status bar used by the main window
        """
        self.statusBar().showMessage('')

    def create_menu(self):
        """
        Create the menu used by the main window
        """
        self.menubar = QMenuBar(self)
        self.setMenuBar(self.menubar)

        self.menu_file = self.menubar.addMenu('&File')
        self.menu_file.addAction(self.action_settings)

        self.menu_view = self.menubar.addMenu('&View')

        self.menu_view_choose_screen = QMenu('Choose Screen', self)
        for action_screen in self.actions_screens:
            self.menu_view_choose_screen.addAction(action_screen)

        self.menu_view.addMenu(self.menu_view_choose_screen)
        self.menu_view.addAction(self.action_edit_perspective)
        self.menu_view.addAction(self.action_save_perspective)
        self.menu_view.addAction(self.action_load_perspective)
        self.menu_view.addAction(self.action_view_fullscreen)
        self.menu_view.addAction(self.action_add_widget)
        self.menu_view_choose_screen.addAction(self.action_add_screen)

        self.menu_mav = self.menubar.addMenu('&MAV')
        self.menu_mav.addAction(self.action_connections)

        #self.show()

    def on_action_view_fullscreen(self):
        if self.action_view_fullscreen.isChecked():
            self.showFullScreen()
        else:
            self.showNormal()


    def on_action_settings(self):
        '''
        Launch the Settings dialog
        '''
        print("TODO on_action_settings")

    def on_action_connections(self):
        '''
        Launch the Connections dialog
        '''
        d = ConnectionsDialog(self.state)
        d.exec_()

    def on_action_screen(self, screen_number):
        '''
        Switch to the specified screen number
        '''

        # Save the settings for the old screen before loading the new screen
        self.write_screen_settings()

        # Load the new screen
        self.active_screen = screen_number
        self.display_active_screen()

        # Ensure the new screen action is checked and the old one is dechecked
        for i in range(0,len(self.actions_screens)):
            action_screen = self.actions_screens[i]
            if i == screen_number:
                action_screen.setChecked(True)
            else:
                action_screen.setChecked(False)

    def on_action_save_perspective(self):

        # Ensure we have saved the most recent changes to autosave.ini
        self.write_screen_settings()
        self.write_window_settings()

        # Get a destination filename
        filename = QFileDialog.getSaveFileName(self, 'Save Perspective File', 'ui/perspectives/untitled.ini', 'Perspective Files (*.ini)')

        # Copy the autosave.ini file to the new file
        shutil.copyfile('ui/perspectives/autosave.ini', filename)

    def on_action_load_perspective(self):

        # Get a source filename
        filename = QFileDialog.getOpenFileName(self, 'Open Perspective File', 'ui/perspectives', 'Perspective Files (*.ini)')
        print(filename)

        # Copy the file to overwrite autosave.ini
        shutil.copyfile(filename, 'ui/perspectives/autosave.ini')

        # Reload settings
        self.perspective = QSettings('ui/perspectives/autosave.ini', QSettings.IniFormat)
        self.active_screen = 0
        self.read_window_settings()
        self.display_active_screen()


    def on_action_edit_perspective(self):

        d = EditPerspectiveDialog(self.state)
        d.exec_()
        d.show()

    def on_action_edit_screens(self):

        d = EditScreensDialog(self.state, self.screens, self)
        d.exec_()
        d.show()

        # If the user selects OK in the dialog, they have possibly
        # made changes we need to save. Then we redraw verything.
        # If they cancel, doing a refrsh() will reload screen
        # settings from the configuraiton file and overwrite any
        # changes they made and then cancelled.
        if d.result == True:
            self.screen_count = len(self.screens)
            self.write_window_settings()
            self.refresh()
        else:

            self.refresh()


    def on_action_add_widget(self):
        # TODO on_action_add_widget

        d = AddWidgetDialog(self.state, self)
        d.exec_()
        d.show()
        if d.result == False:
            return

        self.add_gcs_widget(d.widget, d.widget_position)


    def catch_network_changed(self):

        self.populate_focus_combobox()

    def populate_focus_combobox(self):

        # Update the combo boxes for focused object
        # TODO support sorting of focused MAV combo box. Sort keys?
        self.combo_focused_mav.blockSignals(True)
        self.combo_focused_mav.clear()
        print("main_window.catch_network_changed")
        for mavkey in self.state.mav_network.mavs:
            mav = self.state.mav_network.mavs[mavkey]
            v = QVariant(mav)
            self.combo_focused_mav.addItem(mav.get_name(), v)
            if mav == self.state.focused_object:
                self.combo_focused_mav.setCurrentIndex(self.combo_focused_mav.count()-1)
        self.combo_focused_mav.blockSignals(False)

        # Notify all widgets
        for w in self.children():
            if isinstance(w, GCSWidget):
                w.catch_network_changed()

    def catch_focus_changed(self, focused_object, component_id):

        # Notify all widgets that the focused datasource is changing
        for w in self.children():
            if isinstance(w, GCSWidget):
                w.catch_focus_changed(focused_object, component_id)

        # Update the combo box
        for i in range(self.combo_focused_mav.count()):
            data = self.combo_focused_mav.itemData(i).toPyObject()
            if data == focused_object:
                self.combo_focused_mav.setCurrentIndex(i)
                break

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

        self.action_debug_network = QAction('&Show MAV Network', self)
        self.action_debug_network.triggered.connect(self.on_debug_network)
        self.menu_debug.addAction(self.action_debug_network)

    def build_routing_dictionary(self):
        """
        This rebuilds the routing table, which keeps track of which widgets are listening to which
        system_ids. Any time a packet comes in, the main window forwards the packet to all widgets
        listening for that system_id.
        """
        self._routing = {}
        for i in range(0, 254):
            self._routing[i] = []
        for w in self.children():
            if isinstance(w, GCSWidget):
                if w._track_focused and not w.isClosing:
                    if isinstance(self.state.focused_object, MAV) and w.get_datasource_allowed(WidgetDataSource.SINGLE):
                        self._routing[self.state.focused_object.system_id].append(w)
                    elif isinstance(self.state.focused_object, Swarm) and w.get_datasource_allowed(WidgetDataSource.SWARM):
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

    def catch_widget_datasource_changed(self, widget, track_focused, object):
        """
        This event listens for a signal from widgets, indicating they are changing their
        datasource. That is a cue to rebuild the routing dictionary.
        """
        self.build_routing_dictionary()

    def closeEvent(self, e):
        # Use the QSettings system to store window geometry in the registry
        self.write_window_settings()
        self.write_screen_settings()

    def read_window_settings(self):
        """
        Read window-level settings from the persperctive .INI file. This includes the window
        geometry and metadata about the screens contained within that window.
        """

        # We save/restore geometry at the window level, because this just affects the dimensions
        # for the main window and is constant across all screens.
        self.restoreGeometry(self.perspective.value("mainwindow/geometry").toByteArray())

        # Clear out old screen information
        self.screens = []

        # Read the number of screens in the configuration file, defaulting to 1 if file doesn't exist
        try:
            self.screen_count = self.perspective.value("mainwindow/screencount").toPyObject().toInt()[0]
        except:
            self.screen_count = 1



        # Iterate over those screens, build a Screen object, and add to the screens list
        for i in range(0, self.screen_count):

            # Load the screen objects from the perspective .INI file
            try:
                uuid = self.perspective.value("mainwindow/screenuuids").toPyObject()[i]
                groupname_screen = "screen-" + uuid
                self.perspective.beginGroup(groupname_screen)
                screenname = self.perspective.value('name').toPyObject()
                iconfilename = self.perspective.value('iconfile').toPyObject()
                tooltip = self.perspective.value('tooltip').toPyObject()
                statustip = self.perspective.value('statustip').toPyObject()
                order = self.perspective.value('order').toPyObject()
                self.perspective.endGroup()
            except:
                uuid = QUuid.createUuid().toString()
                screenname = 'New Screen'
                iconfilename = 'art/48x48/toolbar_screen.png'
                tooltip = ""
                statustip = ""
                order = 0

            screen = Screen(screenname, iconfilename, tooltip, statustip, order, uuid)
            self.screens.append(screen)

    def write_window_settings(self):
        """
        Write window-level settings from the persperctive .INI file. This includes the window
        geometry and metadata about the screens contained within that window.
        """
        screen_dictionary = {}
        i = 0
        for screen in self.screens:
            screen_dictionary[i] = screen.uuid
            i += 1

        # Write the number of screens
        self.perspective.beginGroup('mainwindow')
        self.perspective.setValue('screencount', str(self.screen_count))
        self.perspective.setValue('screenuuids', QVariant(screen_dictionary))
        self.perspective.setValue('geometry', self.saveGeometry())
        self.perspective.endGroup()

        # Iterate over the screens and save screen data to the configuration file
        i = 0
        for screen in self.screens:
            groupname_screen = 'screen-' + screen.uuid
            self.perspective.beginGroup(groupname_screen)
            self.perspective.setValue('name', screen.name)
            self.perspective.setValue('iconfile', screen.iconfile)
            self.perspective.setValue('tooltip', screen.tooltip)
            self.perspective.setValue('statustip', screen.statustip)
            self.perspective.setValue('order', screen.order)
            self.perspective.endGroup()
            i += 1

    def write_screen_settings(self):
        """
        Screen settings include the widget layout for a particular screen. The window state is
        also saved with each screen, because the state includes screen-specific data like widget
        layout.
        """

        groupname_screen = 'screen-' + self.screens[self.active_screen].uuid

        # Clear out everything for this screen in the .INI file, which ensures we clear out
        # any widgets that have been removed in the UI.
        self.perspective.remove(groupname_screen + '/widgets')
        self.perspective.remove(groupname_screen + '/widget-positions')
        self.perspective.remove(groupname_screen + '/state')

        # Save which widgets are on the screen, and their object names
        widget_dict = {}
        widget_position_dict = {}
        for w in self.children():
            if isinstance(w, GCSWidget):
                if not w.isClosing:
                    classname = QString(str(w.__class__.__name__))
                    widget_dict[QString(w.objectName())] = classname
                    widget_position_dict[QString(w.objectName())] = self.dockWidgetArea(w)
        widget_variant = QVariant(widget_dict)
        widget_position_variant = QVariant(widget_position_dict)

        # Save the window geometry
        self.perspective.beginGroup(groupname_screen)
        self.perspective.setValue('widgets', widget_variant)
        self.perspective.setValue('widget-positions', widget_position_variant)
        self.perspective.setValue('state', self.saveState())

        # Save individual widget settings
        for w in self.children():
            if isinstance(w, GCSWidget):
                groupname_widget = w.objectName()
                self.perspective.beginGroup(groupname_widget)
                w.write_settings(self.perspective)
                self.perspective.endGroup() # End widget group

        # End screen group
        self.perspective.endGroup()

    def read_screen_settings(self):
        """
        Screen settings include the widget layout for a particular screen. The window state is
        also restored with each screen, because the state includes screen-specific data like widget
        layout.
        """

        groupname_screen = 'screen-' + self.screens[self.active_screen].uuid

        # Load the window settings, which will restore all these widgets to
        # their appropriate geometries
        self.perspective.beginGroup(groupname_screen)

        # Read dictionaries contaiing widget class names and locations
        widget_dict = self.perspective.value('widgets').toPyObject()
        widget_position_dict = self.perspective.value('widget-positions').toPyObject()

        # Test for None, in case the .INI file is empty or doesn't exist
        # Then create the widgets listed in the .INI file
        if widget_dict != None:
            for key in widget_dict:
                position = widget_position_dict[key]


                # The goal here is to instantiate a new widget object based on the name
                # stored in the .INI widget dictionary. I had a lot of trouble with this,
                # and there is probably a better way, but this is what I came up with...
                # iterating through the class object we saved when we first launched
                # the program and imported all the widget files/classes.
                for w in self.widget_library:
                    if widget_dict[key] == w.__name__:
                        newWidget = w(self.state, self)
                        newWidget.setObjectName(key)
                        self.addDockWidget(widget_position_dict[key], newWidget)

        # TODO Load widget settings here
        for w in self.children():
            if isinstance(w, GCSWidget):
                groupname_widget = w.objectName()
                self.perspective.beginGroup(groupname_widget)
                w.read_settings(self.perspective)
                self.perspective.endGroup() # End widget group

        # Now restore the window and state layout
        #self.restoreState(self.perspective.value("state").toByteArray())
        self.perspective.endGroup()

        # This is a bit hackish, but restoreState() also restores the toolbar states. Since
        # we want to keep control of drawing our own toolbars, I delete everything created by
        # restoreState()
        # TODO this accidentally wipes out the widget toolbars as well
        toolbars = self.findChildren(QToolBar)
        for toolbar in toolbars:
            self.removeToolBar(toolbar)

    def add_gcs_widget(self, classobject, position):
        """
        This is called when the user wants to add a widget to a screen, i.e. using the Add Widget
        dialog box. Note that when widgets are reconstructed from a perspective file, different code
        is used (the read_screen_settings() method).
        """

        # Create the widget
        newWidget = classobject(self.state, self)

        # The main window needs to be updated if this widget changes datasources
        newWidget.on_datasource_changed.append(self.catch_widget_datasource_changed)

        if position == 'Center':
            self.setCentralWidget(newWidget)
        elif position == 'Left':
            self.addDockWidget(Qt.LeftDockWidgetArea, newWidget)
        elif position == 'Right':
            self.addDockWidget(Qt.RightDockWidgetArea, newWidget)
        elif position == 'Top':
            self.addDockWidget(Qt.TopDockWidgetArea, newWidget)
        elif position == 'Bottom':
            self.addDockWidget(Qt.BottomDockWidgetArea, newWidget)
        else:
            self.addDockWidget(Qt.RightDockWidgetArea, newWidget)
            newWidget.setFloating(True)

        # Rebuild the mavlink routing dictionary so this widget can get updates
        self.build_routing_dictionary()

        # Update the perpsective .INI file to include the new widget
        self.write_screen_settings()

    def load_widget_library(self):
        """
        This is called once by MainWindow to import everything in the widgets folder and save
        a list of widget classes.
        """

        sys.path.append('ui/widgets/')

        # Recursive file listing code from
        # http://stackoverflow.com/questions/3207219/how-to-list-all-files-of-a-directory-in-python
        f = []
        path = self.state.path + '/ui/widgets'
        #print path
        for (dirpath, dirnames, filenames) in os.walk(path):
            f.extend(filenames)
            break

        # List comprehension code from
        # http://stackoverflow.com/questions/2152898/filtering-a-list-of-strings-based-on-contents
        f = [k for k in f if '.pyc' not in k]
        f = [k for k in f if '__init__.py' not in k]
        f = [k for k in f if 'GCSWidget.py' not in k]


        # This essentially runs:
        # from ui.widgets.GCSWidgetExample import GCSWidgetExample
        # for each file in the widgets folder
        widgetModules = []
        for i in f:
            modulename = i[:-3]
            widgetModules.append(__import__('ui.widgets.' + modulename, globals(), locals(), [modulename]))

        # This generates a list of GCSWidget-derived classes
        self.widget_library = GCSWidget.__subclasses__()

    def on_widget_closed(self):
        print("on_widget_closed")
        # Rebuild the mavlink routing dictionary so this widget can get updates
        self.build_routing_dictionary()
        print('a')
        # Update the perpsective .INI file to include the new widget
        self.write_screen_settings()
        print('b')


