"""
This is the root class for all opengcs widgets
"""

from PyQt4 import QtCore, QtGui

class MAVTarget:
    ALL = -1
    FOCUSED = -2


class GCSWidget (QtGui.QDockWidget):

    # This is the name that will appear in the widget list on the "Add New Widget" window.
    # That window searches through the entire widgets directory, recursively searches
    # through all the GCSWidget-derived classes, and pulls out this name. Override it in
    # your class.
    widgetName = "GCSWidget"

    def __init__(self, state, parent):
        super(GCSWidget, self).__init__("TODO", parent)
        self.state = state
        self.target = MAVTarget.FOCUSED
        self.setWindowTitle("Blank Widget (Base Class)")
        self.title = self.titleBarWidget()

        self.create_menu()

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_menu)

    def refresh(self):
        return

    def create_menu(self):

        self.action_floating = QtGui.QAction('&Float Mode', self)
        #actionFloating.setStatusTip('Open the settings menu')
        #actionFloating.setToolTip(('Settings'))
        self.action_floating.triggered.connect(self.on_action_floating)
        self.action_floating.setCheckable(True)

        self.action_tabbed = QtGui.QAction('&Tabbed Mode', self)
        self.action_tabbed.triggered.connect(self.on_action_tabbed)
        self.action_tabbed.setCheckable(True)

        self.action_titlebar = QtGui.QAction('&Show Title Bar', self)
        self.action_titlebar.triggered.connect(self.on_action_titlebar)
        self.action_titlebar.setCheckable(True)

    def show_menu(self):
        menu = QtGui.QMenu()
        menu.addAction(self.action_floating)
        menu.addAction(self.action_tabbed)
        menu.addAction(self.action_titlebar)
        selectedItem = menu.exec_(QtGui.QCursor.pos())

    def on_action_floating(self):
        # TODO decide how to handle central widgets, which can be floated but not unfloated
        self.setFloating(self.action_floating.isChecked())

    def on_action_tabbed(self):
        # TODO on_action_tabbed
        print("on_action_tabbed")
        #self.tabifyDockWidget()

    def on_action_titlebar(self):
        # TODO on_action_titlebar is not working
        # Need to figure out which flags to clear/set to get the right behavior
        print("on_action_titlebar")
        if self.action_titlebar.isChecked() == False:
            print("hide")
            self.setTitleBarWidget(None)
            #self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        else:
            print("show")
            self.setTitleBarWidget(self.title)
            #self.setWindowFlags(None)

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






    def mousePressEvent(self, QMouseEvent):
        # DEBUG this exists to assist with layout management
        print("Features" + str(self.features()))
        print("Height: " + str(self.height()), "Width: " + str(self.width()))
        print("Is floating: " + str(self.isFloating()))
        print("Pos: " + str(self.pos()))
        print("Size: " + str(self.size()))
        print("X: " + str(self.x))
        print("Y: " + str(self.y))


