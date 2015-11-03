# TODO widgets need to be assigned a datasource when created

"""
This is the root class for all opengcs widgets

All widgets should inherit from this. Child widgets must:

- Call the __init__ superconstructor as the first line of their __init__
- In the init() call, call set_allowable_datasource().
- In the init() call, call set_datasource()
- override refresh() and call the super refresh()
  has/have focus in the main window.
"""

import sys
import uuid
from os import path
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from gcs_state import *

class WidgetDataSource:
    """
    These constants specify whether a widget is displaying a single aircraft, or a
    swarm of aircraft.
    """
    SINGLE = 0b10
    SWARM = 0b01



FOCUSED = [0]


class GCSWidget (QDockWidget):

    # This is the name that will appear in the widget list on the "Add New Widget" window.
    # That window searches through the entire widgets directory, recursively searches
    # through all the GCSWidget-derived classes, and pulls out this name. Override it in
    # your class.
    widget_name_plaintext = "GCSWidget"

    def __init__(self, state, parent, uuid=None):

        super(GCSWidget, self).__init__("GCSWidget", parent)
        self.state = state

        # We give every widget a UUID, which is used to track the widget's settings in
        # pespective .INI files
        if uuid:
            self.setObjectName(uuid)
        else:
            self.setObjectName(QUuid.createUuid().toString())

        # Signals other code can subscribe to
        self.on_datasource_changed = []

        # Default: Single MAV, tracking focused object
        self.set_datasource_allowable(WidgetDataSource.SINGLE)
        self.set_datasource(True)

        self.setWindowTitle("Blank Widget (Base Class)")

        # Save a reference, so we can reconstruct title bar if user closes it
        self.title_bar = self.titleBarWidget()

        self.create_menu()

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_menu)
        self.set_colors()

        # Get application path and build asset path
        # TODO we should get the app's path from somewhere else, perhaps a config file
        app_dir = path.dirname(sys.argv[0])
        asset_dir = 'art/hud'
        self.asset_path = path.join(app_dir, asset_dir)

    def __str__(self):
        return self.widget_name_plaintext

    def set_colors(self):
        """
        Color codes widgets based on what mav or swarm it represents. This is a human factors
         feature so everything for each aircraft/swarm can be distinguished by a specific
         color.
        """
        # TODO implement set_colors. Need to think more about how to handle swarm vs mav colors.
        # Perhaps a hatching pattern for one, and solid colors for the other?
        if self._datasource is Swarm or self._datasource is MAV:
            p = self.palette()
            # TODO
            p.setColor(self.backgroundRole(), QColor(self._datasource.color))
            self.setPalette(p)
            self.setAutoFillBackground(True)
        else:
            p = self.palette()
            p.setColor(self.backgroundRole(), QWidget().palette().color(QPalette.Window))
            self.setPalette(p)
            self.setAutoFillBackground(True)

    def refresh(self):

        # Check to ensure that the widget is tracking the focused object, if necessary
        if self._track_focused:
            if isinstance(self.state.focused_object, MAV) and (self._datasource_allowable & WidgetDataSource.SINGLE > 0):
                self._datasource = self.state.focused_object
            elif isinstance(self.state.focused_object, Swarm) and (self._datasource_allowable & WidgetDataSource.SWARM > 0):
                self._datasource = self.state.focused_object
            else:
                self._datasource = None

        # Takes care of color-coding the widget based on the datasource object
        self.set_colors()

    def create_menu(self):

        self.action_floating = QAction('&Float Mode', self)
        #actionFloating.setStatusTip('Open the settings menu')
        #actionFloating.setToolTip(('Settings'))
        self.action_floating.triggered.connect(self.on_action_floating)
        self.action_floating.setCheckable(True)

        self.action_tabbed = QAction('&Tabbed Mode', self)
        self.action_tabbed.triggered.connect(self.on_action_tabbed)
        self.action_tabbed.setCheckable(True)

        self.action_titlebar = QAction('&Show Title Bar', self)
        self.action_titlebar.triggered.connect(self.on_action_titlebar)
        self.action_titlebar.setCheckable(True)
        self.action_titlebar.setChecked(True)

    def show_menu(self):
        menu = QMenu()
        menu.addAction(self.action_floating)
        menu.addAction(self.action_tabbed)
        menu.addAction(self.action_titlebar)
        selectedItem = menu.exec_(QCursor.pos())

    def on_action_floating(self):
        # TODO decide how to handle central widgets, which can be floated but not unfloated
        self.setFloating(self.action_floating.isChecked())
        # Force widgets to have a title bar when they are floating
        if self.action_floating.isChecked():
            self.setShowTitlebar(True)
            self.action_titlebar.setChecked(True)

    def on_action_tabbed(self):
        # TODO on_action_tabbed
        print("on_action_tabbed")
        #self.tabifyDockWidget()

    def on_action_titlebar(self):
        # TODO on_action_titlebar is not working
        # Need to figure out which flags to clear/set to get the right behavior
        print("on_action_titlebar")
        self.setShowTitlebar(self.action_titlebar.isChecked())
        """
        if self.action_titlebar.isChecked() == False:
            print("hide")
            self.setTitleBarWidget(None)
            #self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        else:
            print("show")
            self.setTitleBarWidget(self.title_bar)
            #self.setWindowFlags(None)
        """

    def setShowTitlebar(self, value):
        if value:
            self.setTitleBarWidget(self.title_bar)
        else:
            self.setTitleBarWidget(QWidget())


    def catch_focus_changed(self, object, component_id):
        """
        Called automatically when the focused mav is changed.

        The default GCS widget behavior is to call the refresh() function.
        Widgets inheriting from GCSWidget may override this to customize
        their own behavior.
        """
        self.refresh()

    def catch_network_changed(self):
        """
        Called automatically when the structure of the MAV network is
        changed (MAV or component is added or removed).
        Default behavior is to trigger a refresh.

        """
        self.refresh()
        return

    def set_datasource(self, track_focused, object=None):
        """
        Set the data source type
        """
        self._track_focused = track_focused
        self._datasource = object

        for signal in self.on_datasource_changed:
            signal(track_focused, object)

    def get_datasource(self):

        return self._datasource

    def set_datasource_allowable(self, datasource_allowable):
        """
        Specifies which data sources this widget is capable of dispalying... single, swarm, or both.

        :param datasource_allowable: OR'd bits from the WidgetDataSource, indicating single, swarm, or both
        :return:
        """
        self._datasource_allowable = datasource_allowable

    def get_datasource_allowed(self, source):
        """
        Returns if this widget is allowed to use the given type of datasource.

        :param source: the source to check (i.e. WidgetDataSource.SINGLE)
        :return: 1 if allowed, 0 otherwise
        """
        return (self._datasource_allowable & source > 0)

    def process_messages(self, m):
        """
        Override this to handle incoming mavlink messages. The widget will only receive messages from sys_ids
        that the widget has specified as a datasource.
        :param m: mavlink message packet
        """
        return

    def write_settings(self, settings):
        """
        Override to save widget-specific settings that will persist when the application is closed
        and reloaded. The 'settings' parameter is a QSettings object that is created by the calling
        code. A beginGroup() call will already have been made, so all you need to do is save your settings
        like follows:

        settings.setValue("widget_property_1", self.property_1)

        """
        return

    def read_settings(self, settings):
        """
        Override to load widget-specific settings from persistent files. The 'settings' parameter is
        a QSettings object that is created by the calling code. A beginGroup() call will arleady have
        been made, so all you need to do is save your settings like follows:

        self.property_1 = settings.value("property_1").toString()
        """
        return
