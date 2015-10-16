"""
This is the root class for all opengcs widgets
"""
# TODO change connection icon based on status (alive, dead, etc.) of connection
# TODO change MAV icon based on type of vehicle and connection status
# TODO refreshing occurs at wrong tiems, and does not pick up new connections unless manually refreshed
# TODO add an option for displaying a list of MAVs instead of a tree view
# TODO add support for components
# TODO double-clicking a MAV should change the focused MAV
# TODO create a context menu
# TODO context menu for connection: Disconnect
# TODO context menu for MAV: Set Focus

from GCSWidget import *
from PyQt4.QtGui import *
from PyQt4.QtCore import QSize


class GCSWidgetMAVNetwork (GCSWidget):

    widgetName = "MAV Network"

    def __init__(self, state, parent):
        super(GCSWidgetMAVNetwork, self).__init__(state, parent)

        self.setWindowTitle("MAV Network")
        #self.setWidget(QtGui.QLabel("Map Widget"))

        self.tree = QTreeWidget()

        self.tree.header().setVisible(False)


        vbox = QVBoxLayout()

        vbox.addWidget(self.tree)

        mylayout = QWidget()
        mylayout.setLayout(vbox)
        self.setWidget(mylayout)

        # Toolbar
        #self.toolbar = self.addToolBar('MainToolbar')
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(16,16))
        self.action_tree = QAction(QIcon('art/16x16/user-available.png'), '&Tree', self)
        self.action_tree.setStatusTip('View tree of all devices')
        self.action_tree.triggered.connect(self.on_button_tree)
        self.toolbar.addAction(self.action_tree)
        vbox.setMenuBar(self.toolbar)

        self.refresh_data()

        self.state.on_mav_registered.append(self.refresh_data)
        self.state.on_connection_registered.append(self.refresh_data)
        self.state.on_mav_unregistered.append(self.refresh_data)
        self.state.on_connection_unregistered.append(self.refresh_data)

    def refresh_data(self):
        self.tree.clear()
        for connection in self.state.connections:
            print(connection.port)
            conn_item = QTreeWidgetItem(self.tree, [connection.port])
            #conn_item = QTreeWidgetItem(self.tree, ['Connection'])
            #conn_item = QTreeWidgetItem(self.tree)
            #conn_item.setText(0,'Connection')
            conn_item.setIcon(0,QIcon('art/16x16/user-available.png'))
            #conn_item.setUserData()
            self.tree.addTopLevelItem(conn_item)
            for mav in connection.mavs:
                print(mav)
                mav_item = QTreeWidgetItem(conn_item, [mav.name])
                #mav_item = QTreeWidgetItem(conn_item, ['MAV'])
                mav_item.setIcon(0,QIcon('art/16x16/arrow-right-2.png'))
                #conn_item.addChild(mav_item)

    def on_button_tree(self):
        self.refresh_data()