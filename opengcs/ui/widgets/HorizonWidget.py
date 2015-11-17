from PyQt4.QtGui import *
from PyQt4.QtCore import *
from opengcs import *

class HorizonWidget (QWidget):

    def __init__(self, parent):
        super(HorizonWidget, self).__init__(parent)
        self.parent = parent
        self.roll_deg = 0
        self.pitch_deg = 0
        self.initUI()
        self.show()


    def initUI(self):
        """
        Initialize the user interface for the main window
        """
        self.setMinimumSize(75, 75)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setFixedSize(75, 75)
        self.img = QPixmap(gcsfile('art/hud/horizon_back.png'))

    def paintEvent(self, QPaintEvent):

        painter = QPainter(self)#.parent)
        painter.save()
        painter.translate(self.width()/2, self.height()/2 + (self.pitch_deg*5))
        painter.rotate(-self.roll_deg)

        source = QRectF(0, 0, self.img.width(), self.img.height())
        dest = QRectF(-self.width()*2, -self.height()*2, self.width()*4, self.height()*4)
        #painter.drawPixmap(-200, -200, self.img)
        painter.drawPixmap(dest, self.img, source)
        painter.restore()