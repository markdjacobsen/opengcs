# TODO: make disconnect button work - DONE?
# TODO: close all ports upon closing program
# TODO: update port status icon / alert to dead ports
# TODO: disconnect needs to refresh the window, removing connection from open ports and adding it to available ports - DONE?
# TODO: need a hook that detects serial port changes while on the ConnectionsDialog
# TODO: support screen ordering in screens dialog

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from util import serial_ports, import_package
from gcs_state import *
import mainwindow
import sys
import os
import functools
from pymavlink import mavutil
from opengcs import *

from ui.widgets.GCSWidget import GCSWidget

class ConnectionsDialog (QDialog):

    def __init__(self, state, parent=None):
        super(ConnectionsDialog, self).__init__(parent)
        self.state = state
        self.init_ui()

    def init_ui(self):

        self.setWindowTitle('Edit Connections')
        self.resize(700, 200)

        open_connections_label = QLabel('Open connections:', self)
        self.table_connections = QTableWidget(1, 4, self)
        self.table_connections.setHorizontalHeaderLabels(['Status', 'Port', 'Number', 'Disconnect'])
        self.table_connections.horizontalHeader().setResizeMode(0, QHeaderView.ResizeToContents)
        self.table_connections.horizontalHeader().setResizeMode(1, QHeaderView.Stretch)
        self.table_connections.horizontalHeader().setResizeMode(2, QHeaderView.ResizeToContents)
        new_connection_label = QLabel('Open new connection:', self)
        self.combo_new_connection = QComboBox(self)

        self.combo_new_port = QComboBox(self)
        self.combo_new_port.addItem('57600')
        self.combo_new_port.addItem('115200')

        self.lineedit_new_port = QLineEdit(self)
        self.lineedit_new_port.setText('127.0.0.1:14550')
        self.lineedit_new_port.setVisible(False)

        button_connect = QPushButton('&Connect', self)
        button_connect.clicked.connect(self.on_button_connect)


        button_close = QPushButton('&Close', self)
        button_close.clicked.connect(self.on_button_close)

        hbox = QHBoxLayout()
        hbox.addWidget(self.combo_new_connection)
        hbox.addWidget(self.combo_new_port)
        hbox.addWidget(self.lineedit_new_port)
        hbox.addWidget(button_connect)


        hbox2 = QHBoxLayout()
        hbox2.addStretch(1)
        hbox2.addWidget(button_close)

        vbox = QVBoxLayout()
        vbox.addWidget(open_connections_label)
        vbox.addWidget(self.table_connections)
        vbox.addWidget(new_connection_label)
        vbox.addLayout(hbox)
        vbox.addLayout(hbox2)

        self.setLayout(vbox)

        self.update_ports()

    def update_ports(self):

        self.serialports = serial_ports()

        self.table_connections.clearContents()
        self.table_connections.setRowCount(len(self.state.mav_network.connections))

        self.openports = []

        row = 0
        for conn in self.state.mav_network.connections:

            self.openports.append(conn.port)

            item = QTableWidgetItem('0')
            status = QTableWidgetItem()
            if conn.is_port_dead() == False:
                status.setIcon(QIcon(gcsfile('art/16x16/dialog-clean.png')))
            else:
                status.setIcon(QIcon(gcsfile('art/16x16/dialog-error-2.png')))
            self.table_connections.setItem(row, 0, status)
            self.table_connections.setItem(row, 1, QTableWidgetItem(conn.port))
            self.table_connections.setItem(row, 2, QTableWidgetItem(str(conn.number)))
            btn_disconnect = QPushButton('Disconnect')
            self.table_connections.setCellWidget(row, 3, btn_disconnect)
            btn_disconnect.clicked.connect(functools.partial(self.on_button_disconnect, row))
            row = row + 1

        self.combo_new_connection.clear()
        itemCount = 0
        for port in self.serialports:
            if port not in self.openports:
                self.combo_new_connection.addItem(port)
                if port.startswith("/dev/tty.usbserial"):
                    self.combo_new_connection.setCurrentIndex(itemCount)        # KW: Hack to make debugging faster
                    self.combo_new_port.setCurrentIndex(0)
                    itemCount = -1
                if itemCount >= 0:                                              # Test this logic...
                    if port == "/dev/tty.usbmodem1":
                        self.combo_new_connection.setCurrentIndex(itemCount)        # KW: Hack to make debugging faster
                        self.combo_new_port.setCurrentIndex(1)                      # KW move speed to 115200
                    itemCount += 1
        self.combo_new_connection.addItem('tcp')
        self.combo_new_connection.addItem('udp')
        self.combo_new_connection.currentIndexChanged.connect(self.on_connection_combo_changed)

    def on_button_close(self):
        self.close()

    def on_button_connect(self):
        conntype = self.combo_new_connection.currentText()
        conn = None

        if conntype == 'udp' or conntype == 'tcp':
            try:
                conn = Connection(self.state, str(self.combo_new_connection.currentText()), self.lineedit_new_port.text())
            except ValueError:
                msg_box = QMessageBox()
                msg_box.setText('Please enter a valid port number')
                msg_box.exec_()
                return
        else:
            # TODO: I temporarily moved the Connection constructor out of a 'try' block, because it is causing
            # all errors in message processing to be captured by try. I need to figure out how to avoid this,
            # and then move the connection step back into a try block.
            conn = Connection(self.state, str(self.combo_new_connection.currentText()), int(self.combo_new_port.currentText()))

            #try:
            #    conn = Connection(self.state, str(self.newConnectionCombo.currentText()), int(self.newPortCombo.currentText()))
            #except:
            #    msg_box = QMessageBox()
            #    msg_box.setText("Unexpected error connecting to serial port")
            #    msg_box.exec_()
            #    return

        self.state.mav_network.add_connection(conn)

        self.update_ports()

    def on_button_disconnect(self, row):
        conn = self.state.mav_network.connections[row]
        print 'Disconnect ' + conn.port
        conn.close()
        # TODO error between these two lines... the serial connection is not truly closed before
        # remove_connection is called. That means more mavlink packets come in after the
        # close() call, and a new mav gets detected again
        self.state.mav_network.remove_connection(conn)
        self.update_ports()

    def on_connection_combo_changed(self):

        conntype = self.combo_new_connection.currentText()
        if conntype == 'tcp' or conntype == 'udp':
            self.combo_new_port.setVisible(False)
            self.lineedit_new_port.setVisible(True)
        else:
            self.combo_new_port.setVisible(True)
            self.lineedit_new_port.setVisible(False)

class EditPerspectiveDialog (QDialog):
    # TODO allow user to specify location for widget, floating/non floating, tabbed/non tabbed
    # TODO consider having widget settings panel on this window
    def __init__(self, state, parent=None):
        super(EditPerspectiveDialog, self).__init__(parent)
        self.state = state
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Edit Perspective')
        self.resize(700,200)

        self.tabwidget = QTabWidget(self)
        #self.tabwidget.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.tabwidget)
        self.setLayout(self.main_layout)

        self.tab_screens = QWidget()
        self.tab_widgets = QWidget()
        self.tab_toolbar = QWidget()

        self.tabwidget.addTab(self.tab_screens, 'Screens')
        self.tabwidget.addTab(self.tab_widgets, 'Widgets')
        self.tabwidget.addTab(self.tab_toolbar, 'Toolbar')

        self.init_tab_screens()
        self.init_tab_widgets()
        self.init_tab_toolbar()

    def init_tab_screens(self):

        hbox = QHBoxLayout()

        # Build the left panel
        vbox_screen_list = QVBoxLayout()
        vbox_screen_list.addWidget(QLabel('Screen list'))

        self.list_screens = QListWidget()
        btn_add_screen = QPushButton('+')
        btn_delete_screen = QPushButton('x')

        box_buttons = QHBoxLayout()
        box_buttons.addWidget(btn_add_screen)
        box_buttons.addWidget(btn_delete_screen)

        vbox_screen_list.addWidget(self.list_screens)
        vbox_screen_list.addLayout(box_buttons)
        hbox.addLayout(vbox_screen_list)

        # Build the right panel
        #vbox_screen_settings = QVBoxLayout()
        #hbox.addLayout(vbox_screen_settings)
        #group = QGroupBox("Screen settings")
        #vbox_screen_settings.addWidget(group)

        layout_screen_settings = QFormLayout()
        layout_screen_settings.addRow('Name:', QLineEdit())
        layout_screen_settings.addRow('Tool Tip Text:', QLineEdit())
        layout_screen_settings.addRow('Status Bar Text:', QLineEdit())
        layout_screen_settings.addRow('Icon:', QLineEdit())
        hbox.addLayout(layout_screen_settings)

        self.tab_screens.setLayout(hbox)

        # Connect controls
        btn_add_screen.clicked.connect(self.on_button_add_screen)
        btn_delete_screen.clicked.connect(self.on_button_delete_screen)

        return

    def init_tab_widgets(self):

        self.listWidget = QListWidget(self)
        self.widgets = self.list_widgets()
        for w in self.widgets:
            #i = QListWidgetItem(w.widgetName)
            i = QListWidgetItem(w)
            self.listWidget.addItem(i)

        label = QLabel('Select a widget to add to the current screen')

        button_cancel = QPushButton('&Cancel', self)
        button_cancel.clicked.connect(self.on_button_cancel)

        button_ok = QPushButton('&OK', self)
        button_ok.clicked.connect(self.on_button_ok)

        hbox1 = QHBoxLayout()
        hbox1.addStretch(1)
        hbox1.addWidget(button_cancel)
        hbox1.addWidget(button_ok)

        vbox = QVBoxLayout()
        vbox.addWidget(label)
        vbox.addWidget(self.listWidget)
        vbox.addLayout(hbox1)

        self.tab_widgets.setLayout(vbox)

    def init_tab_toolbar(self):

        return

    def list_widgets(self):
        sys.path.append('ui/widgets/')

        # Recursive file listing code from
        # http://stackoverflow.com/questions/3207219/how-to-list-all-files-of-a-directory-in-python
        f = []
        # TODO should this be in terms of gcsfile?
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


        # TODO: import classes of widgets in the ui/widgets folder, not just modules
        # possibly helpful: http://stackoverflow.com/questions/547829/how-to-dynamically-load-a-python-class
        widgetModules = []
        for i in f:
            modulename = i[:-3]
            widgetModules.append(__import__(modulename))

        subs = GCSWidget.__subclasses__()
        # DEBUG
        return subs


    def on_button_ok(self):
        # TODO add widget upon closing dialog
        self.close()

    def on_button_cancel(self):
        self.close()

    def on_button_add_screen(self):
        # TODO on_button_add_screen
        print('on_button_add_screen()')

    def on_button_delete_screen(self):
        # TODO on_button_delete_screen
        print('on_button_delete_screen()')

class AddWidgetDialog (QDialog):

    def __init__(self, state, parent):
        super(AddWidgetDialog, self).__init__(parent)
        self.state = state
        self.parent = parent
        self.widgets = parent.widget_library
        self.init_ui()
        self.widget_name = None
        self.widget_position = None
        self.result = False

    def init_ui(self):
        self.setWindowTitle('Add Widget')
        self.resize(400,200)


        self.listWidget = QListWidget(self)

        for w in self.widgets:
            i = QListWidgetItem(w.widget_name_plaintext)
            self.listWidget.addItem(i)

        label = QLabel('Select a widget to add to the current screen')

        self.combo_position = QComboBox(self)
        self.combo_position.addItem('Left')
        self.combo_position.addItem('Right')
        self.combo_position.addItem('Top')
        self.combo_position.addItem('Bottom')
        self.combo_position.addItem('Center')
        self.combo_position.addItem('Floating')

        button_cancel = QPushButton('&Cancel', self)
        button_cancel.clicked.connect(self.on_button_cancel)

        button_ok = QPushButton('&OK', self)
        button_ok.clicked.connect(self.on_button_ok)

        hbox1 = QHBoxLayout()
        hbox1.addStretch(1)
        hbox1.addWidget(button_cancel)
        hbox1.addWidget(button_ok)

        vbox = QVBoxLayout()
        vbox.addWidget(label)
        vbox.addWidget(self.listWidget)
        vbox.addWidget(QLabel('Position for new widget:'))
        vbox.addWidget(self.combo_position)
        vbox.addLayout(hbox1)

        self.setLayout(vbox)

    def on_button_ok(self):
        # TODO add widget upon closing dialog
        self.widget_position = self.combo_position.currentText()

        row = self.listWidget.currentRow()
        self.widget = self.widgets[row]
        self.result = True
        self.close()

    def on_button_cancel(self):
        self.result = False
        self.close()

class EditScreensDialog (QDialog):

    def __init__(self, state, screens, parent):
        super(EditScreensDialog, self).__init__(parent)
        self.state = state
        self.parent = parent
        self.screens = screens
        self.init_ui()
        self.selected_screen = None
        self.uuids_to_delete = []

    def init_ui(self):
        self.setWindowTitle('Edit Screens')
        self.resize(600,200)

        hbox = QHBoxLayout()

        # Build the left panel
        vbox_screen_list = QVBoxLayout()
        vbox_screen_list.addWidget(QLabel('Screen list'))

        self.list_screens = QListWidget()
        self.list_screens.currentItemChanged.connect(self.on_button_item_changed)

        btn_add_screen = QPushButton('+')
        btn_add_screen.clicked.connect(self.on_button_add_screen)
        btn_delete_screen = QPushButton('x')
        btn_delete_screen.clicked.connect(self.on_button_delete_screen)

        box_screen_buttons = QHBoxLayout()
        box_screen_buttons.addWidget(btn_add_screen)
        box_screen_buttons.addWidget(btn_delete_screen)

        vbox_screen_list.addWidget(self.list_screens)
        vbox_screen_list.addLayout(box_screen_buttons)
        hbox.addLayout(vbox_screen_list)

        self.line_name = QLineEdit()
        self.line_tooltip = QLineEdit()
        self.line_statustip = QLineEdit()
        self.btn_icon = QPushButton()

        self.line_name.textChanged.connect(self.on_text_changed)
        self.line_tooltip.textChanged.connect(self.on_text_changed)
        self.line_statustip.textChanged.connect(self.on_text_changed)
        self.line_name.editingFinished.connect(self.on_name_finished)
        self.btn_icon.clicked.connect(self.on_button_icon)


        layout_screen_settings = QFormLayout()
        layout_screen_settings.addRow('Name:', self.line_name)
        layout_screen_settings.addRow('Tool Tip Text:', self.line_tooltip)
        layout_screen_settings.addRow('Status Bar Text:', self.line_statustip)
        layout_screen_settings.addRow('Icon (new):', self.btn_icon)
        hbox.addLayout(layout_screen_settings)

        button_cancel = QPushButton('&Cancel', self)
        button_cancel.clicked.connect(self.on_button_cancel)

        button_ok = QPushButton('&OK', self)
        button_ok.clicked.connect(self.on_button_ok)

        hbox_dialog_buttons = QHBoxLayout()
        hbox_dialog_buttons.addStretch(1)
        hbox_dialog_buttons.addWidget(button_cancel)
        hbox_dialog_buttons.addWidget(button_ok)

        vbox_main_layout = QVBoxLayout()
        vbox_main_layout.addLayout(hbox)
        vbox_main_layout.addLayout(hbox_dialog_buttons)

        self.setLayout(vbox_main_layout)

        self.refresh()

    def refresh(self):

        for screen in self.screens:
            self.list_screens.addItem(screen.name)

    def on_button_ok(self):
        # TODO add widget upon closing dialog
        self.result = True
        self.close()

    def on_button_icon(self):
        # If the user clicks on the icon button, allow them to choose a new icon file
        filename = str(QFileDialog.getOpenFileName(self, 'Select Icon File', os.getcwd(), 'Image Files (*.png *.jpg *.bmp)'))
        self.screens[self.list_screens.currentRow()].iconfile = filename
        icon = QIcon(self.selected_screen.iconfile)
        self.btn_icon.setIconSize(QSize(64, 64))
        self.btn_icon.setIcon(icon)

    def on_button_cancel(self):
        self.setResult(False)
        self.result = False
        self.close()

    def on_button_add_screen(self):

        new_screen = mainwindow.Screen()
        self.screens.append(new_screen)
        new_item = QListWidgetItem(new_screen.name)
        self.list_screens.addItem(new_item)
        self.list_screens.setCurrentItem(new_item)

    def on_button_delete_screen(self):

        self.selected_screen = self.screens[self.list_screens.currentRow()]
        if isinstance(self.selected_screen, mainwindow.Screen):
            if self.list_screens.count() == 1:
                # TODO: messagebox about deleting last row
                return
            # TODO why is this not disappearing from the list?
            self.list_screens.takeItem(self.list_screens.currentIndex().row())
            self.screens.remove(self.selected_screen)
            self.uuids_to_delete.append(self.selected_screen.uuid)

    def on_button_item_changed(self):

        self.selected_screen = self.screens[self.list_screens.currentRow()]

        self.line_name.blockSignals(True)
        self.line_tooltip.blockSignals(True)
        self.line_statustip.blockSignals(True)

        if isinstance(self.selected_screen, mainwindow.Screen):
            self.line_name.setText(self.selected_screen.name)
            self.line_tooltip.setText(self.selected_screen.tooltip)
            self.line_statustip.setText(self.selected_screen.statustip)
            self.line_name.setEnabled(True)
            self.line_tooltip.setEnabled(True)
            self.line_statustip.setEnabled(True)
            self.btn_icon.setEnabled(True)

            icon = QIcon(self.selected_screen.iconfile)
            self.btn_icon.setIconSize(QSize(64, 64))
            self.btn_icon.setIcon(icon)

        else:
            self.line_name.setText('')
            self.line_icon.setText('')
            self.line_tooltip.setText('')
            self.line_statustip.setText('')
            self.line_name.setText('')
            self.btn_icon.setIcon(None)
            self.line_name.setEnabled(False)
            self.line_icon.setEnabled(False)
            self.line_tooltip.setEnabled(False)
            self.line_statustip.setEnabled(False)
            self.btn_icon.setEnabled(False)

        self.line_name.blockSignals(False)
        self.line_tooltip.blockSignals(False)
        self.line_statustip.blockSignals(False)


    def on_text_changed(self):

        if isinstance(self.selected_screen, mainwindow.Screen):
            self.selected_screen.name = self.line_name.text()
            self.selected_screen.tooltip = self.line_tooltip.text()
            self.selected_screen.statustip = self.line_statustip.text()

    def on_name_finished(self):
        item = self.list_screens.currentItem()
        item.setText(self.line_name.text())
