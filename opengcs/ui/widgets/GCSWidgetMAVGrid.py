# -*- coding: utf-8 -*-

from GCSWidget import *
from PyQt4.QtGui import *

class MAVGridColumn():
    def __init__(self, item_type, col_name, label):
        self.item_type = item_type
        self.col_name = col_name
        self.label = label

class GCSWidgetMAVGrid (GCSWidget):

    widget_name_plaintext = "MAV Grid"

    def __init__(self, state, parent):

        super(GCSWidgetMAVGrid, self).__init__(state, parent)
        self.set_datasource_allowable(WidgetDataSource.SINGLE)
        self.setWindowTitle("MAV Grid")
        self.setMinimumSize(300, 300)

        self.init_ui()

    def init_ui(self):

        self.grid = QTableWidget(1, 4, self)
        self.grid.setHorizontalHeaderLabels(['MAV', 'Alt', 'AS', 'Mode','WP'])
        self.setWidget(self.grid)

        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(16,16))

        self.action_settings = QAction(QIcon('art/16x16/settings.png'), '&Settings', self)
        self.action_settings.setStatusTip('Edit widget settings')
        self.action_settings.triggered.connect(self.on_button_settings)
        self.toolbar.addAction(self.action_settings)

        self.refresh()

    def resizeEvent(self, event):

        self.refresh()



    def refresh(self):

        return

    def on_button_settings(self):
        print("on_button_settings")

    def process_messages(self, m):

        mtype = m.get_type()

        #if mtype == "VFR_HUD":
        return