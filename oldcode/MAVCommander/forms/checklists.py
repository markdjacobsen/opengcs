# checklists.py
# Mark Jacobsen
#
# This file contains classes for a MAVProxy preflight checklist module.
# We design the forms using wxFormBuilder, which auto-generates the code in
# baseforms.py. We name these classes ChecklistPanelBase, ChecklistItemPanelBase, etc.
#
# We then inherit from these classes in this file.

from baseforms import *

STATUS_RED = 0
STATUS_YELLOW = 1
STATUS_GREEN = 2

class ChecklistPanel (ChecklistPanelBase):
    def __init__(self, parent, master, system_id):
        super(ChecklistPanel, self).__init__(parent)
        self.master = master
        self.system_id = system_id

        # A list of (message type, subscriber function)
        # Checklist items can subscribe to specific types of messages...
        # i.e. the "zeroize airspeed sensor" step just subscribes to VFR_HUD messages
        self.subscribers = []

        self.master.message_hooks.append(self.process_packet)

        # Update the header with information about the aircraft and connection
        # TODO aircraft name
        #self.staticPort.SetLabel(TODO... not sure where to get a value for this)
        self.staticSystem.SetLabel(str(system_id))

    def add_subscriber(self, msg, func):
        self.subscribers.append([msg, func])

    def remove_subscriber(self, msg, func):
        for subscriber in self.subscribers:
            if subscriber[0] == msg and subscriber[1] == func:
                self.subscribers.remove(subscriber)

    def process_packet(self, caller, msg):
        # As each packet comes in, check the message type against the list of
        # subscribers. Call any callback functions as necessary.
        mtype = msg.get_type()
        for subscriber in self.subscribers:
             if mtype == subscriber[0]:
                 subscriber[1](msg)

class ChecklistItemPanel (ChecklistItemPanelBase):
    def __init__(self, parent):
        super(ChecklistItemPanel, self).__init__(parent)
        self.parent = parent
        self.status = STATUS_RED
        # Can get the MAVlink connection through self.parent.master and self.parent.system_id

    def on_text_double_click( self, event ):
        wx.MessageBox('Further Information', 'Override the on_text_double_click() method in your checklist item to provide expanded guidance about this step.',
            wx.OK | wx.ICON_INFORMATION)

    def set_green(self):
        self.panelStatus.SetBackgroundColour( wx.Colour( 0, 255, 0 ) )
        self.panelStatus.Refresh()
        self.status = STATUS_GREEN


    def set_red(self):
        self.panelStatus.SetBackgroundColour( wx.Colour( 255, 0, 0 ) )
        self.status = STATUS_RED

    def set_yellow(self):
        self.panelStatus.SetBackgroundColour( wx.Colour( 255, 255, 0 ) )
        self.status = STATUS_YELLOW