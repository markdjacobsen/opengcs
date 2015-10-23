"""
This is the root class for all opengcs widgets

All widgets should inherit from this. Child widgets must:

- Call the __init__ superconstructor as the first line of their __init__
- override refresh() and call the super refresh()

"""

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class MAVTarget:
    ALL = -1
    FOCUSED = -2
    GROUP = -3


class GCSWidget (QDockWidget):

    # This is the name that will appear in the widget list on the "Add New Widget" window.
    # That window searches through the entire widgets directory, recursively searches
    # through all the GCSWidget-derived classes, and pulls out this name. Override it in
    # your class.
    widgetName = "GCSWidget"

    def __init__(self, state, parent):

        super(GCSWidget, self).__init__("GCSWidget", parent)
        self.setObjectName("GCSWidget")
        self.state = state
        self.source_type = MAVTarget.FOCUSED
        self.setWindowTitle("Blank Widget (Base Class)")

        # Save a reference, so we can reconstruct titele bar if user closes it
        self.title_bar = self.titleBarWidget()

        self.create_menu()

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_menu)
        self.set_colors()

    def set_colors(self):

        if self.source_type == MAVTarget.GROUP:
            p = self.palette()
            p.setColor(self.backgroundRole(), QColor(255,0,0))
            self.setPalette(p)
            self.setAutoFillBackground(True)
        else:
            p = self.palette()
            p.setColor(self.backgroundRole(), QWidget().palette().color(QPalette.Window))
            self.setPalette(p)
            self.setAutoFillBackground(True)

    def refresh(self):
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


    def catch_focused_mav_changed(self):
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

        The default GCS widget behavior is to call the refresh() function.
        Widgets inheriting from GCSWidget may override this to customize
        their own behavior.
        """
        self.refresh()
        return






    # def mousePressEvent(self, QMouseEvent):
    #     # DEBUG this exists to assist with layout management
    #     print("Features" + str(self.features()))
    #     print("Height: " + str(self.height()), "Width: " + str(self.width()))
    #     print("Is floating: " + str(self.isFloating()))
    #     print("Pos: " + str(self.pos()))
    #     print("Size: " + str(self.size()))
    #     print("X: " + str(self.x))
    #     print("Y: " + str(self.y))


