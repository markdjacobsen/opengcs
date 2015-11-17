# TODO colorize messages
# TODO remove icon in dialog titlebar
# TODO settings dialog
# TODO autoscroll to bottom

from GCSWidget import *
from PyQt4.QtGui import *
from opengcs import *
from gcs_state import *

class GCSWidgetMavlinkMessages (GCSWidget):

    widget_name_plaintext = 'Mavlink Message Traffic'

    def __init__(self, state, parent):

        super(GCSWidgetMavlinkMessages, self).__init__(state, parent)
        self.set_datasource_allowable(WidgetDataSource.SINGLE)
        self.setWindowTitle('Mavlink Message Traffic')
        self.setMinimumSize(100, 100)

        self.set_datasource_allowable(WidgetDataSource.SINGLE|WidgetDataSource.SWARM)

        # Widget settings
        self.max_messages = 500
        self.muted_messages = []

        self.init_ui()

    def init_ui(self):

        # We use a QTextDocument(), which allows us to insert messages as "blocks" of text
        # This class has a handy maximum block count, and automatically removes blocks from
        # the beginning as the maximum is exceeded.
        self.doc = QTextDocument()
        self.doc.setMaximumBlockCount(self.max_messages)

        # We use a cursor object to navigate the text document
        self.cursor = QTextCursor(self.doc)

        self.textedit = QTextEdit(self)
        self.textedit.setReadOnly(True)
        self.textedit.setLineWrapMode(QTextEdit.NoWrap)
        self.textedit.setDocument(self.doc)

        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(16,16))

        self.action_pause = QAction(QIcon(gcsfile('art/16x16/pause.png')), '&Pause', self)
        self.action_pause.setStatusTip('Pause message traffic')
        self.action_pause.setToolTip('Pause message traffic')
        self.action_pause.setCheckable(True)

        self.action_filter = QAction(QIcon(gcsfile('art/16x16/filter.png')), '&Filter', self)
        self.action_filter.setStatusTip('Filter messages by type')
        self.action_filter.setToolTip('Filter messages by type')
        self.action_filter.triggered.connect(self.on_button_filter)

        self.action_settings = QAction(QIcon(gcsfile('art/16x16/settings.png')), '&Settings', self)
        self.action_settings.setStatusTip('Edit widget settings')
        self.action_settings.setToolTip('Edit widget settings')
        self.action_settings.triggered.connect(self.on_button_settings)

        self.toolbar.addAction(self.action_pause)
        self.toolbar.addAction(self.action_filter)
        self.toolbar.addAction(self.action_settings)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.textedit)
        mylayout = QWidget()
        mylayout.setLayout(vbox)
        vbox.setMenuBar(self.toolbar)
        self.setWidget(mylayout)

        self.dlg_filter = GCSWidgetMavlinkMessagesFilterDialog(self)

    def resizeEvent(self, event):
        super(GCSWidgetMavlinkMessages, self).refresh()
        self.refresh()

    def refresh(self):
        super(GCSWidgetMavlinkMessages, self).refresh()
        self.dlg_filter.refresh()
        return

    def process_messages(self, m):

        if self.action_pause.isChecked():
            return

        mtype = m.get_type()

        if mtype not in self.muted_messages:
            self.cursor.insertBlock()
            self.cursor.insertText(QString(str(m.get_header().srcSystem)) + QString(': ') + QString(str(m)))

        return

    def read_settings(self, settings):

        self.max_messages = settings.value('max_messages')

    def write_settings(self, settings):

        settings.setValue('max_messages', 500)

    def on_button_filter(self):

        print('on_button_filter')
        self.dlg_filter.show() # Run modeless
        self.dlg_filter.raise_()

    def on_button_settings(self):

        d = GCSWidgetMavlinkMessagesSettingsDialog(self)
        d.exec_() # Run modal

class GCSWidgetMavlinkMessagesFilterDialog (QDialog):

    '''
    This dialog lets the user choose which mavlink messages to monitor. It operates
    directly on the PARENT allowable_messages variable
    '''

    def __init__(self, parent):
        super(GCSWidgetMavlinkMessagesFilterDialog, self).__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Filter Mavlink Messages')
        self.resize(300,600)

        vbox = QVBoxLayout()

        self.list_messages = QListWidget()
        self.list_messages.itemChanged.connect(self.on_item_changed)

        btn_select_all = QPushButton('All')
        btn_select_all.clicked.connect(self.on_button_select_all)
        btn_select_none = QPushButton('None')
        btn_select_none.clicked.connect(self.on_button_select_none)

        box_screen_buttons = QHBoxLayout()
        box_screen_buttons.addWidget(btn_select_all)
        box_screen_buttons.addWidget(btn_select_none)


        vbox.addLayout(box_screen_buttons)
        vbox.addWidget(self.list_messages)

        self.setLayout(vbox)

    def showEvent(self, QShowEvent):

        self.refresh()

    def refresh(self):
        print('refresh')
        self.list_messages.clear()

        # Initialize by checking allowable messages if a filter is applied, or checking
        # all messages if a filter is not applied.
        firstmav = None
        if isinstance(self.parent.get_datasource(), MAV):
            firstmav = self.parent.get_datasource()
        elif isinstance(self.parent.get_datasource(), Swarm):
            if len(self.parent.get_datasource().mavs) > 0:
                firstmav = self.parent.get_datasource().mavs[0]

        if firstmav is not None:
            for msg in firstmav.msg_types:
                item = QListWidgetItem(msg)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                if msg not in self.parent.muted_messages:
                    item.setCheckState(Qt.Checked)
                else:
                    item.setCheckState(Qt.Unchecked)
                self.list_messages.addItem(item)

        # If no filter was applied at the time of initialize, this changes
        # allowable_messages to include ALL message types
        for item in self.list_items():
            if item.checkState() != Qt.Checked:
                self.parent.muted_messages.append(str(item.text()))


    def on_button_select_all(self):

        for item in self.list_items():
            item.setCheckState(Qt.Checked)

    def on_button_select_none(self):

        for item in self.list_items():
            item.setCheckState(Qt.Unchecked)

    def list_items(self):
        '''
        QListWidget has no method to return all the items, so we write our own
        '''
        items = []
        for index in xrange(self.list_messages.count()):
            items.append(self.list_messages.item(index))
        return items

    def on_item_changed(self):
        print('on_item_changed')
        self.parent.muted_messages = []
        items = self.list_items()
        for item in items:
            if item.checkState() != Qt.Checked:
                self.parent.muted_messages.append(str(item.text()))

class GCSWidgetMavlinkMessagesSettingsDialog (QDialog):

    def __init__(self, parent):
        super(GCSWidgetMavlinkMessagesSettingsDialog, self).__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Mavlink Messages Widget Settings')
        self.resize(300,600)

        layout = QFormLayout(self)

        self.dlg_background_color = QColorDialog(self)
        self.spin_block_count = QSpinBox(self)
        layout.addRow(QString('Background Color'), self.dlg_background_color)
        layout.addRow(QString('Max Messages to Display'), self.spin_block_count)


        self.setLayout(layout)