# TODO Need to kill threads properly... causes runtime error upon exit
# TODO Right now the baud rate is hard-coded to 115,200

import  wx, sys, glob, serial, threading, os, subprocess
from pymavlink import mavutil
from preflight import PreflightFrame
from db_layer import *

mybaudrate = 115200
#----------------------------------------------------------------------

class ConnectionPanel(wx.Panel):
    """
    This panel displays a checklistbox for selecting multiple serial ports and connecting.

    It keeps a list of functions called "hooks." Once the user hits the CONNECT button, all
    these hook functions are called and provided with a list of the desired serial ports.
    That is how the function passes the port list to the calling code that needs it.
    """

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        lb = wx.CheckListBox(self, -1, (0,0), (300,100), serial_ports())
        self.Bind(wx.EVT_LISTBOX, self.EvtListBox, lb)
        self.Bind(wx.EVT_CHECKLISTBOX, self.EvtCheckListBox, lb)
        lb.SetSelection(0)
        self.lb = lb

        lb.Bind(wx.EVT_RIGHT_DOWN, self.OnDoHitTest)

        pos = lb.GetPosition().x + lb.GetSize().width + 25
        btn = wx.Button(self, -1, "Connect", (pos, 0))
        self.Bind(wx.EVT_BUTTON, self.OnConnectButton, btn)

        self.connect_hooks = []

    def add_connect_hook(self,func):
        """
        The calling code can call this function to add a callback.
        :param func: The function to call after the user selects CONNECT
        """
        self.connect_hooks.append(func)

    def EvtListBox(self, event):
        return

    def EvtCheckListBox(self, event):
        # TODO I think this is leftover code from a wxPython example
        index = event.GetSelection()
        label = self.lb.GetString(index)
        status = 'un'
        if self.lb.IsChecked(index):
            status = ''

        self.lb.SetSelection(index)    # so that (un)checking also selects (moves the highlight)


    def OnConnectButton(self, evt):
        """
        When the user selects CONNECT, call all the callback functions and give them the list of serial connections
        """
        ports = self.lb.GetCheckedStrings()
        for hook in self.connect_hooks:
            hook(ports)
        return

    def OnDoHitTest(self, evt):
        # TODO I think this is leftover from an earlier example
        item = self.lb.HitTest(evt.GetPosition())

# TODO This is junk code, available for testing sizer layouts by displaying a colored panel
class ColorPanel(wx.Panel):
    def __init__(self, parent, color):
        wx.Panel.__init__(self, parent, -1)
        self.BackgroundColour = color

class MAVPanel(wx.Panel):
    """
    This panel displays information for a single MAV. Each panel is provided with a mavlink
    connection object at initialization. For multi-MAV ops, multiple panels can be displayed, each
    with a separate serial connection.
    """
    def __init__(self, parent, connection):
        wx.Panel.__init__(self, parent, -1)

        self.connection = connection

        self.BackgroundColour = (150,150,150)
        self.horz_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.vert_sizer_right = wx.BoxSizer(wx.VERTICAL)
        self.vert_sizer_left = wx.BoxSizer(wx.VERTICAL)

        # Aircraft properties for display
        self.aircraft_name = wx.StaticText(self,-1,"Aircraft")
        self.system_id = wx.StaticText(self,-1,"System NNN")
        self.mode = wx.StaticText(self,-1,"Mode")
        self.range = wx.StaticText(self,-1,"Range")
        self.altitude = wx.StaticText(self,-1,"Altitude: ")
        self.airspeed = wx.StaticText(self,-1,"Airspeed: ")
        self.heading = wx.StaticText(self,-1,"Heading: ")


        font = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.aircraft_name.SetFont(font)
        self.vert_sizer_left.Add(self.aircraft_name, 0, wx.EXPAND|wx.ALL)
        self.vert_sizer_left.Add(self.system_id, 0, wx.EXPAND|wx.ALL)
        self.vert_sizer_left.Add(self.mode, 0, wx.EXPAND|wx.ALL)
        self.vert_sizer_left.Add(self.range, 0, wx.EXPAND|wx.ALL)
        self.vert_sizer_left.Add(self.altitude, 0, wx.EXPAND|wx.ALL)
        self.vert_sizer_left.Add(self.airspeed, 0, wx.EXPAND|wx.ALL)
        self.vert_sizer_left.Add(self.heading, 0, wx.EXPAND|wx.ALL)


        self.textOutput = wx.TextCtrl(self, -1, "This is the output area")
        self.vert_sizer_right.Add(self.textOutput, 2, wx.EXPAND|wx.ALL)

        self.expandButton = wx.Button(self,-1,"Preflight")
        self.expandButton.Bind(wx.EVT_BUTTON, self.on_preflight)


        self.horz_sizer.Add(self.vert_sizer_left, 0, wx.EXPAND|wx.ALL)
        self.horz_sizer.Add(self.vert_sizer_right, 1, wx.EXPAND|wx.ALL)
        self.horz_sizer.Add(self.expandButton, 0, wx.EXPAND|wx.ALL)

        self.SetAutoLayout(True)
        self.SetSizer(self.horz_sizer)
        self.Layout()

        self.connection.master.message_hooks.append(self.log_message)
        self.connection.hooks_updateinterface.append(self.on_update_interface)

    def on_update_interface(self):
        """
        This is called whenever something signals that the panel needs to be updated
        with the most current information.
        """
        self.system_id.SetLabel("System: " + str(self.connection.system_id))
        self.altitude.SetLabel("Altitude: " + str(self.connection.altitude))
        self.airspeed.SetLabel("Airspeed: " + str(self.connection.airspeed))
        self.heading.SetLabel("Heading: " + str(self.connection.heading))
        self.Layout()


    def log_message(self,caller,msg):
        # TODO This is a temporary function that displays the most recent mavlink packet in a
        # TODO text output window
        if msg.get_type() != 'BAD_DATA':
            self.textOutput.SetValue(str(msg))
        return

    def on_preflight(self,evt):
        """
        If the user hits the preflight button, launch the preflight frame for that MAV
        """
        preflight_frame = PreflightFrame(None, self.connection.master, self.connection.system_id )
        preflight_frame.Show()


class DashboardFrame(wx.Frame):
    """
    This is the main window for the dashboard application. It displays a ConnectionPanel. Once the user
    connects to one or more serial devices, it loads MAVPanel(s) for each connection.
    """
    def __init__(self, parent, id=-1, title='MAV Dashboard',
                 pos=wx.DefaultPosition, size=(500, 500),
                 style=wx.DEFAULT_FRAME_STYLE):
        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        self.connection_panel = ConnectionPanel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.connection_panel,0,wx.EXPAND)

        # Register self.on_connect, so that it will be called when the user selects the CONNECT
        # button on the ConnectionPanel
        self.connection_panel.add_connect_hook(self.on_connect)

        db = MAVCommanderDB()
        db.test_db()

        self.SetSizer(self.sizer)

    def on_connect(self,ports):
        """
        This is the callback that is called when the user selects the CONNECT button on the
        connection panel. It redraws the GUI, showing a MAVPanel for each serial connection.
        :param ports: A list of desired serial ports provided by the ConnectionPanel
        """
        self.connections = []
        self.aircraft_panels = []

        for child in self.sizer.Children:
            self.sizer.Detach(child.Window)

        self.sizer.Add(self.connection_panel,0,wx.EXPAND)

        for port in ports:
            new_connection = VehicleConnection(port,mybaudrate)
            self.connections.append(new_connection)
            aircraft_panel = MAVPanel(self, new_connection)
            self.aircraft_panels.append(aircraft_panel)
            self.sizer.Add(aircraft_panel,0,wx.EXPAND)

        self.SetSizer(self.sizer)
        self.Layout()

class VehicleConnection:
    """
    This object embodies a connection to a single MAV. Each instance of VehicleConnection
    is initialized with its own serial connection, then launches a separate thread to monitor
    incoming mavlink messages.
    """
    # TODO: This may not be the most efficient way to store mavlink connections and merits revisiting
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        # These are the vehicle attributes that are tracked
        self.system_id = -1
        self.airspeed = 0
        self.heading = 0
        self.altitude = 0

        self.msg_types = ["VFR_HUD"]

        self.hooks_updateinterface = []


        self.master = mavutil.mavlink_connection(port, baud=baudrate)
        self.thread = threading.Thread(target=self.process_messages)
        self.thread.setDaemon(True)
        self.thread.start()

        self.master.message_hooks.append(self.check_heartbeat)


        print("Connecting to " + port + " at " + str(baudrate) + " baud, waiting for heartbeat")
        return

    def process_messages(self):
        """
        This runs continuously. The mavutil.recv_match() function will call mavutil.post_message()
        any time a new message is received, and will notify all functions in the master.message_hooks list.
        """
        while True:
            msg = self.master.recv_match(blocking=True)
            if not msg:
                return
            if msg.get_type() == "BAD_DATA":
                if mavutil.all_printable(msg.data):
                    sys.stdout.write(msg.data)
                    sys.stdout.flush()

            mtype = msg.get_type()
            if mtype == "VFR_HUD":
                self.altitude = mavutil.evaluate_expression("VFR_HUD.alt", self.master.messages)
                self.airspeed = mavutil.evaluate_expression("VFR_HUD.airspeed", self.master.messages)
                self.heading = mavutil.evaluate_expression("VFR_HUD.heading", self.master.messages)
                self.update_interfaces()

    def check_heartbeat(self,caller,msg):
        """
        Listens for a heartbeat message

        Once this function is subscribed to the dispatcher, it listens to every
        incoming MAVLINK message and watches for a 'HEARTBEAT' message. Once
        that message is received, the function updates the GUI and then
        unsubscribes itself.
        """

        if msg.get_type() ==  'HEARTBEAT':
            print("Heartbeat received from APM (system %u component %u)\n" % (self.master.target_system, self.master.target_system))
            self.system_id = self.master.target_system
            self.master.message_hooks.remove(self.check_heartbeat)
            self.update_interfaces()

    def update_interfaces(self):
        for hook in self.hooks_updateinterface:
            hook()


def serial_ports():
    """Lists all available serial ports

    :raises EnvironmentError:
        On unsupported or unknown platforms
    :returns:
        A list of available serial ports
    """

    if sys.platform.startswith('win'):
        ports = ['COM' + str(i + 1) for i in range(256)]

    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this is to exclude your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')

    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')

    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


# Create our wxPython application and show our frame
app = wx.App()
frame = DashboardFrame(None)
frame.Show()
app.MainLoop()