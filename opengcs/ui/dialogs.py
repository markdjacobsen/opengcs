# TODO: have a verbose option for showing mavlink feed
# TODO: bug - clicking "OK" causes window to reopen a second time before closing
# TODO: make disconnect button work
# TODO: close all ports upon closing program
# TODO: update port status icon / alert to dead ports

from PyQt4.QtGui import *
import PyQt4.QtCore
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
        self.InitUI()

    def InitUI(self):
        self.setWindowTitle('Edit Connections')
        self.resize(700,200)

        openConnectionsLabel = QLabel('Open connections:', self)
        self.connectionTable = QTableWidget(1,4,self)
        self.connectionTable.setHorizontalHeaderLabels(['Status','Port','Number','Disconnect'])
        self.connectionTable.horizontalHeader().setResizeMode(0,QHeaderView.ResizeToContents)
        self.connectionTable.horizontalHeader().setResizeMode(1,QHeaderView.Stretch)
        newConnectionLabel = QLabel('Open new connection:', self)
        self.newConnectionCombo = QComboBox(self)

        self.newPortCombo = QComboBox(self)
        self.newPortCombo.addItem('56700')
        self.newPortCombo.addItem('115200')

        self.newPortText = QLineEdit(self)
        self.newPortText.setText('14550')
        self.newPortText.setVisible(False)

        connectButton = QPushButton('&Connect', self)
        connectButton.clicked.connect(self.on_button_connect)


        OKButton = QPushButton('&OK', self)
        OKButton.clicked.connect(self.on_button_ok)

        hbox = QHBoxLayout()
        hbox.addWidget(self.newConnectionCombo)
        hbox.addWidget(self.newPortCombo)
        hbox.addWidget(self.newPortText)
        hbox.addWidget(connectButton)


        hbox2 = QHBoxLayout()
        hbox2.addStretch(1)
        hbox2.addWidget(OKButton)

        vbox = QVBoxLayout()
        vbox.addWidget(openConnectionsLabel)
        vbox.addWidget(self.connectionTable)
        vbox.addWidget(newConnectionLabel)
        vbox.addLayout(hbox)
        vbox.addLayout(hbox2)

        self.setLayout(vbox)

        self.UpdatePorts()

    def UpdatePorts(self):
        self.serialports = serial_ports()

        self.connectionTable.clearContents()
        self.connectionTable.setRowCount(len(self.state.connections))

        self.openports = []

        row = 0
        for conn in self.state.connections:

            self.openports.append(conn.port)

            item = QTableWidgetItem('0')
            status = QTableWidgetItem()
            if conn.getPortDead() == False:
                status.setIcon(QIcon('art/16x16/dialog-clean.png'))
            else:
                status.setIcon(QIcon('art/16x16/dialog-error-2.png'))
            self.connectionTable.setItem(row,0,status)
            self.connectionTable.setItem(row,1,QTableWidgetItem(conn.port))
            self.connectionTable.setItem(row,2,QTableWidgetItem(conn.number))
            btnDisconnect = QPushButton('Disconnect')
            self.connectionTable.setCellWidget(row,3,btnDisconnect)
            btnDisconnect.clicked.connect(functools.partial(self.on_button_disconnect, row))
            row = row + 1

        self.newConnectionCombo.clear()
        for port in self.serialports:
            if port not in self.openports:
                self.newConnectionCombo.addItem(port)
        self.newConnectionCombo.addItem('TCP')
        self.newConnectionCombo.addItem('UDP')
        self.newConnectionCombo.editTextChanged.connect(self.on_connection_combo_changed)




    def on_button_ok(self):
        self.close()

    def on_button_connect(self):
        # TODO
        #mav1 = MAV()
        #mav1.connect('/dev/tty.usbmodemfa141',115200)
        #print("Connected")
        #return
        #conn = Connection('/dev/tty.usbmodemfa141',115200)
        #self.state.connections.append(conn)
        #self.UpdatePorts()
        #return


        print("on_button_connect()")
        conntype = self.newConnectionCombo.currentText()
        conn = None

        if conntype == "TCP" or conntype == "UDP":
            try:
                conn = Connection(str(self.newConnectionCombo.currentText()), int(self.newPortText.text()))
            except ValueError:
                msgBox = QMessageBox()
                msgBox.setText("Please enter a valid port number")
                msgBox.exec_()
                return
        else:
            try:
                conn = Connection(str(self.newConnectionCombo.currentText()), int(self.newPortCombo.currentText()))
            except:
                msgBox = QMessageBox()
                msgBox.setText("Unexpected error connecting to serial port")
                msgBox.exec_()
                return

        self.state.connections.append(conn)

        self.UpdatePorts()


    def on_button_disconnect(self, row):
        print "Disconnect " + str(row)

    def on_connection_combo_changed(self):
        print("combo changed")
        conntype = self.newConnectionCombo.currentText()
        if conntype == "TCP" or conntype == "UDP":
            self.newPortCombo.setVisible(False)
            self.newPortText.setVisible(True)
        else:
            self.newPortCombo.setVisible(True)
            self.newPortText.setVisible(False)

class AddWidgetDialog (QDialog):
    def __init__(self, state, parent=None):
        super(AddWidgetDialog, self).__init__(parent)
        self.state = state
        self.InitUI()

    def InitUI(self):
        self.setWindowTitle('Add a widget')
        self.resize(700,200)

        self.listWidget = QListWidget(self)
        widgets = self.ListWidgets()
        for w in widgets:
            i = QListWidgetItem(w.widgetName)
            self.listWidget.addItem(i)

        label = QLabel("Select a widget to add to the current screen")

        CancelButton = QPushButton('&Cancel', self)
        CancelButton.clicked.connect(self.on_button_cancel)

        OKButton = QPushButton('&OK', self)
        OKButton.clicked.connect(self.on_button_ok)

        hbox1 = QHBoxLayout()
        hbox1.addStretch(1)
        hbox1.addWidget(CancelButton)
        hbox1.addWidget(OKButton)

        vbox = QVBoxLayout()
        vbox.addWidget(label)
        vbox.addWidget(self.listWidget)
        vbox.addLayout(hbox1)

        self.setLayout(vbox)

    def ListWidgets(self):
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


        widgetModules = []
        for i in f:
            modulename = i[:-3]
            widgetModules.append(__import__(modulename))

        subs = GCSWidget.__subclasses__()
        return subs


    def on_button_ok(self):
        # TODO
        self.close()

    def on_button_cancel(self):
        self.close()