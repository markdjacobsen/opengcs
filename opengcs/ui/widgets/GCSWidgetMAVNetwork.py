"""
This is the root class for all opengcs widgets
"""
# TODO change connection icon based on status (alive, dead, etc.) of connection
# TODO change MAV icon based on type of vehicle and connection status
# TODO add support for components
# TODO double-clicking a MAV should change the focused MAV
# TODO create a context menu
# TODO context menu for connection: Disconnect
# TODO context menu for MAV: Set Focus

from GCSWidget import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from gcs_state import *

class MAVTreeWidgetItem (QTreeWidgetItem):
    def __init__(self, tree, text, data_object):
        super(MAVTreeWidgetItem, self).__init__(tree, text)
        self.data_object = data_object

class GCSWidgetMAVNetwork (GCSWidget):

    widgetName = "MAV Network"

    def __init__(self, state, parent):

        super(GCSWidgetMAVNetwork, self).__init__(state, parent)
        self.setObjectName("GCSWidgetMAVNetwork")
        self.setWindowTitle("MAV Network")


        self.tree = QTreeWidget()
        self.tree.header().setVisible(False)
        self.tree.itemDoubleClicked.connect(self.on_item_double_click)


        vbox = QVBoxLayout()

        vbox.addWidget(self.tree)

        mylayout = QWidget()
        mylayout.setLayout(vbox)
        self.setWidget(mylayout)

        # Toolbar
        #self.toolbar = self.addToolBar('MainToolbar')
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(16,16))

        self.action_connections = QAction(QIcon('art/16x16/cc_connect_icon&16.png'), '&Connections', self)
        self.action_connections.setStatusTip('View all network connections')
        self.action_connections.triggered.connect(self.on_button_connections)
        self.action_connections.setCheckable(True)
        self.action_connections.setChecked(True)

        self.action_groups = QAction(QIcon('art/16x16/cc_list_num_icon&16.png'), '&Groups', self)
        self.action_groups.setStatusTip('View groups of MAVs')
        self.action_groups.triggered.connect(self.on_button_groups)
        self.action_groups.setCheckable(True)

        self.action_mavs = QAction(QIcon('art/16x16/cc_paper_airplane_icon&16.png'), '&MAVs', self)
        self.action_mavs.setStatusTip('View individual MAVs')
        self.action_mavs.triggered.connect(self.on_button_mavs)
        self.action_mavs.setCheckable(True)


        self.toolbar.addAction(self.action_connections)
        self.toolbar.addAction(self.action_mavs)
        self.toolbar.addAction(self.action_groups)

        vbox.setMenuBar(self.toolbar)

        self.refresh()

        #self.state.on_mav_registered.append(self.refresh_data)
        #self.state.on_connection_registered.append(self.refresh_data)
        #self.state.on_mav_unregistered.append(self.refresh_data)
        #self.state.on_connection_unregistered.append(self.refresh_data)

    def refresh(self):
        super(GCSWidgetMAVNetwork, self).refresh()

        self.tree.clear()

        if self.action_connections.isChecked():
            for connection in self.state.mav_network.connections:
                conn_item = MAVTreeWidgetItem(self.tree, [connection.port], connection)
                conn_item.setIcon(0,QIcon('art/16x16/user-available.png'))
                self.tree.addTopLevelItem(conn_item)

                for mav in self.state.mav_network.get_mavs_on_connection(connection):
                    mav_item = MAVTreeWidgetItem(conn_item, [mav.name], mav)
                    mav_item.setIcon(0,QIcon('art/16x16/arrow-right-2.png'))

        elif self.action_mavs.isChecked():
            for mavkey in self.state.mav_network.mavs:
                mav = self.state.mav_network.mavs[mavkey]

                mav_item = MAVTreeWidgetItem(self.tree, [mav.get_name()], mav)
                mav_item.setIcon(0,QIcon('art/16x16/arrow-right-2.png'))
                self.tree.addTopLevelItem(mav_item)

        elif self.action_groups.isChecked():
            # TODO implement refresh() for group view
            swarms = self.state.config.perspective['swarm']
            for swarm in swarms:
                swarm_item = MAVTreeWidgetItem(self.tree, [swarm['name']], swarm)

                #color = self.palette().pop()
                #color = self.palette()
                color = QColor(swarm['color'])
                pixmap = QPixmap(16, 16)
                pixmap.fill(color)
                swarm_item.setIcon(0, QIcon(pixmap))

                self.tree.addTopLevelItem(swarm_item)

    def on_button_connections(self):
        # TODO implement on_button_connections
        self.action_connections.setChecked(True)
        self.action_groups.setChecked(False)
        self.action_mavs.setChecked(False)
        print("GCSWidgetMAVNetwork.on_button_connections()")
        self.refresh()

    def on_button_groups(self):
        self.action_groups.setChecked(True)
        self.action_mavs.setChecked(False)
        self.action_connections.setChecked(False)
        self.refresh()

    def on_button_mavs(self):
        self.action_groups.setChecked(False)
        self.action_connections.setChecked(False)
        self.action_mavs.setChecked(True)
        self.refresh()

    def on_item_double_click(self, item, col):
        print(item.data_object)
        if isinstance(item.data_object, MAV):
            self.state.set_focus(item.data_object)


"""
    def catch_network_changed(self):
        print("MAVNetwork changed")
        self.refresh()
        return
"""