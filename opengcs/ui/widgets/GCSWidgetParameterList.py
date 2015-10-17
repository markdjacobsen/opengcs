from GCSWidget import *
from PyQt4.QtGui import *
from PyQt4 import QtCore
import fnmatch

# TODO need a clear architecture for reloading data, refreshing view, applyin filter and conditional formatting
# TODO move filter and buttons from an hbox into a toolbar (see GCSWidgetMAVNetwork)

class GCSWidgetParameterList (GCSWidget):

    widgetName = "ParameterList"

    def __init__(self, state, parent):
        super(GCSWidgetParameterList, self).__init__(state, parent)

        self.setWindowTitle("Parameter List")
        self.setMinimumSize(150, 150)
        self.state.on_focused_mav_changed.append(self.mav_changed)

        self.all_params = []
        self.filtered_params = []

        self.InitUI()
        #self.Refresh()

    def InitUI(self):
        self.paramTable = QTableWidget(0,2,self)
        self.paramTable.setHorizontalHeaderLabels(['Parameter','Value'])
        self.paramTable.horizontalHeader().setResizeMode(0,QHeaderView.Stretch)
        self.paramTable.horizontalHeader().setResizeMode(1,QHeaderView.ResizeToContents)

        self.filterLineEdit = QLineEdit()
        self.filterLineEdit.textChanged.connect(self.on_filter_changed)
        self.settingsButton = QPushButton('...')





        # Create toolbar
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QtCore.QSize(16,16))
        self.toolbar.addWidget(self.filterLineEdit)
        self.toolbar.addWidget(self.settingsButton)

        vbox = QVBoxLayout()
        vbox.addWidget(self.paramTable)
        vbox.setMenuBar(self.toolbar)


        #self.action_settings = QAction('...', self)
        #self.action_settings.setStatusTip('Open settings')
        #self.action_settings.triggered.connect(self.on_button_settings)

        #self.toolbar.addAction(self.action_settings)


        mylayout = QWidget()
        mylayout.setLayout(vbox)
        self.setWidget(mylayout)
        #self.setLayout(vbox)
        #self.setWidget(vbox)


        return

    def on_filter_changed(self):
        self.ApplyFilter()

    def Refresh(self):
        self.paramTable.clearContents()

        if self.target == MAVTarget.FOCUSED:
            mav = self.state.focusedMav
        else:
            # TODO handle specific mav assignments
            return

        self.all_params = mav.mav_param

        self.paramTable.setRowCount(mav.mav_param_count)
        row = 0
        for key in mav.mav_param:
            self.paramTable.setItem(row,0,QTableWidgetItem(key))
            self.paramTable.setItem(row,1,QTableWidgetItem(str(mav.mav_param[key])))
            row = row + 1

        self.paramTable.sortByColumn(0, QtCore.Qt.AscendingOrder)

    def ApplyFilter(self):
        pattern = str(self.filterLineEdit.text())

        if self.paramTable.rowCount() == 0:
            return
        for i in range(0,self.paramTable.rowCount()):
            if len(fnmatch.filter([self.paramTable.item(i,0).text()], pattern)) > 0:
                self.paramTable.setRowHidden(i, False)
            else:
                self.paramTable.setRowHidden(i,True)


    def mav_changed(self):
        mav = self.state.focusedMav
        mav.on_params_initialized.append(self.Refresh)
        self.Refresh()



