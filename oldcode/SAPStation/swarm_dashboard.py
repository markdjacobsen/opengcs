__author__ = 'markjacobsen'

import  wx, sys, glob, serial, threading, os, subprocess
from pymavlink import mavutil

#----------------------------------------------------------------------

class ConnectionPanel(wx.Panel):
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
        self.connect_hooks.append(func)

    def EvtListBox(self, event):
        return

    def EvtCheckListBox(self, event):
        index = event.GetSelection()
        label = self.lb.GetString(index)
        status = 'un'
        if self.lb.IsChecked(index):
            status = ''

        self.lb.SetSelection(index)    # so that (un)checking also selects (moves the highlight)


    def OnConnectButton(self, evt):
        ports = self.lb.GetCheckedStrings()
        for hook in self.connect_hooks:
            hook(ports)
        return

    def OnDoHitTest(self, evt):
        item = self.lb.HitTest(evt.GetPosition())

# This is available for testing sizer layouts
class ColorPanel(wx.Panel):
    def __init__(self, parent, color):
        wx.Panel.__init__(self, parent, -1)
        self.BackgroundColour = color

class AircraftPanel(wx.Panel):
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

        self.expandButton = wx.Button(self,-1,"Command")
        self.expandButton.Bind(wx.EVT_BUTTON, self.on_command)


        self.horz_sizer.Add(self.vert_sizer_left, 0, wx.EXPAND|wx.ALL)
        self.horz_sizer.Add(self.vert_sizer_right, 1, wx.EXPAND|wx.ALL)
        self.horz_sizer.Add(self.expandButton, 0, wx.EXPAND|wx.ALL)

        self.SetAutoLayout(True)
        self.SetSizer(self.horz_sizer)
        self.Layout()

        self.connection.master.message_hooks.append(self.log_message)
        self.connection.hooks_updateinterface.append(self.on_update_interface)

    def on_update_interface(self):
        self.system_id.SetLabel("System: " + str(self.connection.system_id))
        self.altitude.SetLabel("Altitude: " + str(self.connection.altitude))
        self.airspeed.SetLabel("Airspeed: " + str(self.connection.airspeed))
        self.heading.SetLabel("Heading: " + str(self.connection.heading))
        self.Layout()


    def log_message(self,caller,msg):
        if msg.get_type() != 'BAD_DATA':
            self.textOutput.SetValue(str(msg))
        return

    def on_command(self,evt):
        print("Command")
        cmd = "mavproxy.py --master=" + self.connection.port
        #subprocess.call("mavproxy.py")
        os.system("mavproxy.py")


class DashboardFrame(wx.Frame):
    def __init__(self, parent, id=-1, title='MAV Dashboard',
                 pos=wx.DefaultPosition, size=(500, 500),
                 style=wx.DEFAULT_FRAME_STYLE):
        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        self.connection_panel = ConnectionPanel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.connection_panel,0,wx.EXPAND)
        self.connection_panel.add_connect_hook(self.on_connect)


        self.SetSizer(self.sizer)

    def on_connect(self,ports):

        self.connections = []
        self.aircraft_panels = []

        for child in self.sizer.Children:
            print(child)
            self.sizer.Detach(child.Window)

        self.sizer.Add(self.connection_panel,0,wx.EXPAND)

        for port in ports:
            new_connection = VehicleConnection(port,115200)
            self.connections.append(new_connection)
            aircraft_panel = AircraftPanel(self, new_connection)
            self.aircraft_panels.append(aircraft_panel)
            self.sizer.Add(aircraft_panel,0,wx.EXPAND)

        self.SetSizer(self.sizer)
        self.Layout()

class VehicleConnection:
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