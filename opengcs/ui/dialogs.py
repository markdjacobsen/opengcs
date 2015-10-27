# TODO: make disconnect button work
# TODO: close all ports upon closing program
# TODO: update port status icon / alert to dead ports
# TODO: disconnect needs to refresh the window, removing connection from open ports and adding it to available ports
# TODO: need a hook that detects serial port changes while on the ConnctionsDialog

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from util import serial_ports, import_package
from gcs_state import *
import sys
import os
import functools

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
        self.combo_new_port.addItem('56700')
        self.combo_new_port.addItem('115200')

        self.lineedit_new_port = QLineEdit(self)
        self.lineedit_new_port.setText('14550')
        self.lineedit_new_port.setVisible(False)

        button_connect = QPushButton('&Connect', self)
        button_connect.clicked.connect(self.on_button_connect)


        button_ok = QPushButton('&OK', self)
        button_ok.clicked.connect(self.on_button_ok)

        hbox = QHBoxLayout()
        hbox.addWidget(self.combo_new_connection)
        hbox.addWidget(self.combo_new_port)
        hbox.addWidget(self.lineedit_new_port)
        hbox.addWidget(button_connect)


        hbox2 = QHBoxLayout()
        hbox2.addStretch(1)
        hbox2.addWidget(button_ok)

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
                status.setIcon(QIcon('art/16x16/dialog-clean.png'))
            else:
                status.setIcon(QIcon('art/16x16/dialog-error-2.png'))
            self.table_connections.setItem(row, 0, status)
            self.table_connections.setItem(row, 1, QTableWidgetItem(conn.port))
            self.table_connections.setItem(row, 2, QTableWidgetItem(str(conn.number)))
            btn_disconnect = QPushButton('Disconnect')
            self.table_connections.setCellWidget(row, 3, btn_disconnect)
            btn_disconnect.clicked.connect(functools.partial(self.on_button_disconnect, row))
            row = row + 1

        self.combo_new_connection.clear()
        for port in self.serialports:
            if port not in self.openports:
                self.combo_new_connection.addItem(port)
        self.combo_new_connection.addItem('TCP')
        self.combo_new_connection.addItem('UDP')
        self.combo_new_connection.editTextChanged.connect(self.on_connection_combo_changed)

    def on_button_ok(self):
        self.close()

    def on_button_connect(self):
        conntype = self.combo_new_connection.currentText()
        conn = None

        if conntype == "TCP" or conntype == "UDP":
            try:
                conn = Connection(self.state, str(self.combo_new_connection.currentText()), int(self.lineedit_new_port.text()))
            except ValueError:
                msg_box = QMessageBox()
                msg_box.setText("Please enter a valid port number")
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
        # TODO implmenet disconnect
        port = self.table_connections.item(row, 1).text()
        conn = self.state.mav_network.connections[row]
        print "Disconnect " + conn.port
        conn.close()
        # TODO error between these two lines... the serial connection is not truly closed before
        # remove_connection is called. That means more mavlink packets come in after the
        # close() call, and a new mav gets detected again
        self.state.mav_network.remove_connection(conn)
        self.update_ports()

    def on_connection_combo_changed(self):
        conntype = self.combo_new_connection.currentText()
        if conntype == "TCP" or conntype == "UDP":
            self.combo_new_port.setVisible(False)
            self.lineedit_new_port.setVisible(True)
        else:
            self.combo_new_port.setVisible(True)
            self.lineedit_new_port.setVisible(False)

class AddWidgetDialog (QDialog):
    # TODO allow user to specify location for widget, floating/non floating, tabbed/non tabbed
    # TODO consider having widget settings panel on this window
    def __init__(self, state, parent=None):
        super(AddWidgetDialog, self).__init__(parent)
        self.state = state
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Add a widget')
        self.resize(700,200)

        self.listWidget = QListWidget(self)
        widgets = self.list_widgets()
        for w in widgets:
            i = QListWidgetItem(w.widgetName)
            self.listWidget.addItem(i)

        label = QLabel("Select a widget to add to the current screen")

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

        self.setLayout(vbox)

    def list_widgets(self):
        sys.path.append("ui/widgets/")

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


        # TODO: import classes of widgets in the ui/widgets folder, not just modules
        # possibly helpful: http://stackoverflow.com/questions/547829/how-to-dynamically-load-a-python-class
        widgetModules = []
        for i in f:
            modulename = i[:-3]
            widgetModules.append(__import__(modulename))
        print(widgetModules)

        subs = GCSWidget.__subclasses__()
        # DEBUG
        print(subs)
        return subs


    def on_button_ok(self):
        # TODO add widget upon closing dialog
        self.close()

    def on_button_cancel(self):
        self.close()