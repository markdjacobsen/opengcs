from PyQt5 import QtWidgets
import gettext

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 1000, 500)
        self.setWindowTitle("opengcs - MAV Ground Station")
        self.show()