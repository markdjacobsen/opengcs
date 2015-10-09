# TODO: open connection
# TODO: have a verbose option for showing mavlink feed
# TODO: read open connections from state
# TODO: remove open connections from botom list
# TODO: automatic updating of port status
# TODO: alerting to dead ports

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
import PyQt5.QtCore
from util import serial_ports
from gcs_state import *

class ConnectionsDialog (QDialog):
    def __init__(self, state, parent=None):
        super(ConnectionsDialog, self).__init__(parent)
        self.state = state
        self.InitUI()

    def InitUI(self):
        self.setWindowTitle('Edit Connections')
        self.resize(700,200)

        openConnectionsLabel = QLabel('Open connections:', self)
        self.serialports = serial_ports()

        self.connectionTable = QTableWidget(len(self.serialports),5,self)
        self.connectionTable.setHorizontalHeaderLabels(['Checked','Port','Number','Status','Disconnect'])
        for p in range(0,len(self.serialports)):
            connected = QTableWidgetItem('0')
            connected.setCheckState(PyQt5.QtCore.Qt.Checked)
            self.connectionTable.setItem(p,0,connected)
            self.connectionTable.setItem(p,1,QTableWidgetItem(self.serialports[p]))
            self.connectionTable.setItem(p,2,QTableWidgetItem('2'))
            imgItem = QTableWidgetItem()
            imgItem.setIcon(QIcon('art/16x16/dialog-clean.png'))
            self.connectionTable.setItem(p,3,imgItem)

            btnDisconnect = QPushButton('Disconnect')
            self.connectionTable.setCellWidget(p,4,btnDisconnect)



        newConnectionLabel = QLabel('Open new connection:', self)
        self.newConnectionCombo = QComboBox(self)
        self.newConnectionCombo.addItems(self.serialports)
        self.newConnectionCombo.addItem('TCP')
        self.newConnectionCombo.addItem('UDP')
        self.newConnectionCombo.currentTextChanged.connect(self.on_connection_combo_changed)


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

    def on_button_ok(self):
        self.close()

    def on_button_connect(self):
        # TODO
        print("on_button_connect()")
        conntype = self.newConnectionCombo.currentText()
        if conntype == "TCP" or conntype == "UDP":
            try:
                conn = Connection(self.newConnectionCombo.currentText(), int(self.newPortText.text()))
            except ValueError:
                msgBox = QMessageBox()
                msgBox.setText("Please enter a valid port number")
                msgBox.exec_()
                return
        else:
            conn = Connection(self.newConnectionCombo.currentText(), int(self.newPortCombo.currentText()))

    def on_connection_combo_changed(self):
        print("combo changed")
        conntype = self.newConnectionCombo.currentText()
        if conntype == "TCP" or conntype == "UDP":
            self.newPortCombo.setVisible(False)
            self.newPortText.setVisible(True)
        else:
            self.newPortCombo.setVisible(True)
            self.newPortText.setVisible(False)
