"""
This is the root class for all opengcs widgets
"""
# TODO change connection icon based on status (alive, dead, etc.) of connection
# TODO change MAV icon based on type of vehicle and connection status
# TODO add support for components
# TODO create a context menu
# TODO context menu for connection: Disconnect
# TODO context menu for MAV: Set Focus

from GCSWidget import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from gcs_state import *

class MAVTreeWidgetItem (QTreeWidgetItem):
    def __init__(self, tree, text, data_object, color='#FFFFFF'):
        super(MAVTreeWidgetItem, self).__init__(tree, text)
        self.data_object = data_object
        color = QColor(color)
        pixmap = QPixmap(16, 16)
        pixmap.fill(color)
        self.setIcon(0, QIcon(pixmap))

class GCSWidgetMAVNetwork (GCSWidget):

    widget_name_plaintext = "MAV Network"

    def __init__(self, state, parent):

        super(GCSWidgetMAVNetwork, self).__init__(state, parent)
        self.setWindowTitle("MAV Network")
        self.set_datasource_allowable(WidgetDataSource.NA)


        self.tree = QTreeWidget()
        self.tree.header().setVisible(False)
        self.tree.itemDoubleClicked.connect(self.on_item_double_click)


        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.tree)
        mylayout = QWidget()
        mylayout.setLayout(vbox)
        self.setWidget(mylayout)

        # Toolbar
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(16,16))

        self.action_connections = QAction(QIcon('art/16x16/tree_btn_connections.png'), '&Connections', self)
        self.action_connections.setStatusTip('View all network connections')
        self.action_connections.triggered.connect(self.on_button_connections)
        self.action_connections.setCheckable(True)
        self.action_connections.setChecked(True)

        self.action_swarms = QAction(QIcon('art/16x16/tree_btn_swarms.png'), '&Swarms', self)
        self.action_swarms.setStatusTip('View groups of MAVs')
        self.action_swarms.triggered.connect(self.on_button_swarms)
        self.action_swarms.setCheckable(True)

        self.action_mavs = QAction(QIcon('art/16x16/tree_btn_mavs.png'), '&MAVs', self)
        self.action_mavs.setStatusTip('View individual MAVs')
        self.action_mavs.triggered.connect(self.on_button_mavs)
        self.action_mavs.setCheckable(True)


        self.toolbar.addAction(self.action_connections)
        self.toolbar.addAction(self.action_mavs)
        self.toolbar.addAction(self.action_swarms)

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
                conn_item.setIcon(0,QIcon('art/16x16/status_green.png'))
                self.tree.addTopLevelItem(conn_item)

                for mav in self.state.mav_network.get_mavs_on_connection(connection):
                    mav_item = MAVTreeWidgetItem(conn_item, [mav.get_name()], mav)
                    mav_item.setIcon(0,QIcon('art/16x16/tree_mav.png'))

        elif self.action_mavs.isChecked():
            for mavkey in self.state.mav_network.mavs:
                mav = self.state.mav_network.mavs[mavkey]

                mav_item = MAVTreeWidgetItem(self.tree, [mav.get_name()], mav)
                mav_item.setIcon(0,QIcon('art/16x16/tree_mav.png'))
                self.tree.addTopLevelItem(mav_item)

        elif self.action_swarms.isChecked():

            # TODO implement refresh() for group view
            for swarm in self.state.mav_network.swarms:
                swarm_item = MAVTreeWidgetItem(self.tree, [swarm.name], swarm, swarm.color)
                self.tree.addTopLevelItem(swarm_item)
                for mav in swarm.mavs:
                    mav_item = MAVTreeWidgetItem(swarm_item, [mav.get_name()], mav, mav.color)

    def on_button_connections(self):
        # TODO implement on_button_connections
        self.action_connections.setChecked(True)
        self.action_swarms.setChecked(False)
        self.action_mavs.setChecked(False)
        self.refresh()

    def on_button_swarms(self):
        self.action_swarms.setChecked(True)
        self.action_mavs.setChecked(False)
        self.action_connections.setChecked(False)
        self.refresh()

    def on_button_mavs(self):
        self.action_swarms.setChecked(False)
        self.action_connections.setChecked(False)
        self.action_mavs.setChecked(True)
        self.refresh()

    def on_item_double_click(self, item, col):

        if isinstance(item.data_object, MAV) or isinstance(item.data_object, Swarm):
            self.state.set_focus(item.data_object)

    def read_settings(self, settings):
        # Read which view we're using: 0 = connections, 1 = mavs, 2 = swarms
        if settings.value("treeview") == 0:
            self.on_button_connections()
        elif settings.value("treeview") == 1:
            self.on_button_mavs()
        else:
            self.on_button_swarms()
        return

    def write_settings(self, settings):
        # Write which view we're using: 0 = connections, 1 = mavs, 2 = swarms
        if self.action_connections.isChecked():
            settings.setValue("treeview", 0)
        elif self.action_mavs.isChecked():
            settings.setValue("treeview", 1)
        else:
            settings.setValue("treeview", 2)
        return

    def show_menu(self):

        print(self.tree.currentItem().data_object)
        super(GCSWidgetMAVNetwork, self).show_menu()
        self.action_arm = QAction('&Arm/Disarm', self)
        self.action_arm.triggered.connect(self.on_action_arm)
        self.menu.addAction(self.action_arm)

    def on_action_arm(self):
        print('on_action_arm()')



"""
    def catch_network_changed(self):
        print("MAVNetwork changed")
        self.refresh()
        return
"""