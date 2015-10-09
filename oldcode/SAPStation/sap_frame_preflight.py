__author__ = 'markjacobsen'

# TODO support enable/visible for buttons

import wx
import config
from strings import *
import checklist
import os.path
import sys
import flightplan
from apm import *
import threading
import mavutil

ID_BTN_PREV = 10
ID_BTN_NEXT = 20

SPACER_BETWEENPANELS = 20
SPACER_LEFTEDGE = 30
SPACER_RIGHTEDGE = 30
SPACER_ABOVETITLE = 20
SPACER_BELOWTITLE = 20

colors = {}

def build_colors():
    """
    This builds a dictionary local to this file, for translating color string from the XML
    file into wxPython colors.
    """
    colors["green"] = wx.GREEN
    colors["red"] = wx.RED
    colors["black"] = wx.BLACK

class SAPFramePreflight(wx.Frame):

    def __init__(self, parent, flight, id=-1, title=sapstring("str_aircraft_preflight"),
                 pos=wx.DefaultPosition, size=(config.preflight_width, config.preflight_height),
                 style=wx.DEFAULT_FRAME_STYLE):
        wx.Frame.__init__(self, parent, id, title, pos, size, style)
        build_colors()
        self.flight = flight
        self.load_checklist()
        self.init_ui()

    def load_checklist(self):
        checklist_file = "Aircraft/" + self.flight.swarm.aircraft + "/checklist.xml"
        print(checklist_file)
        if os.path.isfile(checklist_file) == False:
            dial = wx.MessageDialog(None, 'Checklist file not found:\n' + checklist_file, 'Error', wx.OK|wx.ICON_ERROR)
            dial.ShowModal()
            self.Close()
            return

        self.checklist = checklist.Checklist()
        self.checklist.load(checklist_file)
        self.checklist.print_all() # DEBUG
        self.active_step = self.checklist.first

    def init_ui(self):
        self.st_title = wx.StaticText(self, -1, "This is the title",style=wx.CENTER|wx.EXPAND)
        font = wx.Font(24,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_NORMAL)
        self.st_title.SetFont(font)

        self.panel_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # This generates a vertical array of buttons
        self.button_sizer = wx.BoxSizer(wx.VERTICAL)

        # Now, create a vertical sizer to hold everything we've created
        # and add the individual components
        self.box = wx.BoxSizer(wx.VERTICAL)

        # TODO: this is a pretty clunky way of dealing with the small tape graphic, and it's not seamless
        # replace with a single wider graphic
        cautionimg = wx.Image("Artwork/emergencytape2.PNG", wx.BITMAP_TYPE_ANY)
        self.cautionsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.caution_bitmap1 = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(cautionimg))
        self.caution_bitmap2 = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(cautionimg))
        self.cautionsizer.Add(self.caution_bitmap1)
        self.cautionsizer.Add(self.caution_bitmap2)
        self.box.Add(self.cautionsizer,0,wx.CENTER)
        self.box.Hide(self.cautionsizer)
        abortimg = wx.Image("Artwork/redstripe.jpg",wx.BITMAP_TYPE_ANY)
        self.abortstripe_bitmap = wx.StaticBitmap(self,wx.ID_ANY, wx.BitmapFromImage(abortimg))
        self.box.Add(self.abortstripe_bitmap,0,wx.CENTER)
        self.box.Hide(self.abortstripe_bitmap)

        self.box.AddSpacer(SPACER_ABOVETITLE)
        self.box.Add(self.st_title,0,wx.CENTER|wx.EXPAND|wx.CENTER_FRAME,border=0)
        self.box.AddSpacer(SPACER_BELOWTITLE)
        self.box.Add(self.panel_sizer,1,wx.EXPAND)
        self.box.Add(self.button_sizer,0,wx.EXPAND)
        self.SetSizer(self.box)

        self.sb = SAPStatusBar(self)
        self.SetStatusBar(self.sb)

        # Now, populate this frame with data from the first checklist item
        self.load_current_step()

    def load_current_step(self):
        """
        Populates the frame with data for the currently active checklist step
        """
        # Destroy old
        #for p in self.panel_sizer.GetChildren():
        #    self.panel_sizer.Remove(p)
        #    print(type(p))
        #    self.panel_sizer.Detach(p)
        #    p.Destroy()
        #for b in self.button_sizer.GetChildren():
        #    self.button_sizer.Remove(b)
        #    self.button_sizer.Detach(b)
        #    b.Destroy()


        # TODO I cannot get the old buttons to destroy without causing a bad access
        # problem and crash. This code detaches the old buttons from the sizer
        # but doesn't destroy them. It needs to be fixed.
        for item in self.button_sizer.GetChildren():
            try:
                b = item.GetWindow()
                print("unbinding")
                #b.Unbind(wx.EVT_BUTTON)
                print self.Unbind(wx.EVT_BUTTON, b)
                b.Hide()
            except:
                continue

        self.panel_sizer.Clear(True)
        self.button_sizer.Clear(False)


        # Get the current checklist step
        step = self.step = self.checklist.steps[self.active_step]

        # Initialize data
        self.st_title.SetLabelText(step.title)
        if self.step.type == checklist.TYPE_PROBLEM:
            self.box.Show(self.cautionsizer)
            self.box.Hide(self.abortstripe_bitmap)
        elif self.step.type == checklist.TYPE_NORMAL:
            self.box.Hide(self.cautionsizer)
            self.box.Hide(self.abortstripe_bitmap)
        elif self.step.type == checklist.TYPE_ABORT:
            self.box.Hide(self.cautionsizer)
            self.box.Show(self.abortstripe_bitmap)
        #self.panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.panel_sizer.AddSpacer(SPACER_BETWEENPANELS)

        # Generate content panels
        for p in self.step.panels:
            if p.type == checklist.PANEL_TEXT:
                newpanel = SAPPanelText(self, p)
            elif p.type == checklist.PANEL_MEDIA:
                newpanel = SAPPanelMedia(self, p)
            elif p.type == checklist.PANEL_CODE:
                #newpanel = SAPPanelText(self, p)
                current_module = sys.modules[__name__]
                code_class = getattr(current_module, p.resource)
                newpanel = code_class(self, self.step)
            else:
                continue
            self.panel_sizer.Add(newpanel,1,wx.EXPAND)
            self.panel_sizer.AddSpacer(SPACER_BETWEENPANELS)

        # Generate buttons

        self.button_sizer.AddSpacer(20)
        for b in step.buttons:
            button = wx.Button(self, wx.ID_ANY, b.text, style=wx.CENTER)
            button.SetBackgroundColour(colors[b.color])
            self.button_sizer.Add(button,1,wx.CENTER)
            self.button_sizer.AddSpacer(20)
            self.Bind(wx.EVT_BUTTON, self.on_button, button)
            button.checklistbutton = b
        self.Layout()

    def on_button(self,evt):
        checklistbutton = evt.GetEventObject().checklistbutton
        if checklistbutton.enabled == True:
            self.active_step = checklistbutton.link
            print(self.active_step)
            if self.active_step == "abort":
                # TODO implement abort codes
                self.on_abort(1)
            elif self.active_step == "launch":
                self.on_launch()
            elif self.active_step == "cancel":
                self.on_cancel()
            elif self.active_step == "preflight":
                self.on_preflighted()
            else:
                self.load_current_step()

    def on_preflighted(self):
        """
        Called when a checklist step commands the aircraft to exit in a "Preflighted" status
        """
        self.flight.status = flightplan.STATUS_PREFLIGHTED
        self.Close()
        return

    def on_launch(self):
        """
        Called when a checklist step commands the aircraft to exit in a "Launched" status
        """
        self.flight.status = flightplan.STATUS_AIRBORNE
        # TODO set ATD
        self.Close()
        return

    def on_cancel(self,code):
        """
        Called when a checklist step commands exiting without a change in status
        """
        self.Close()
        return

    def on_abort(self,code):
        """
        Called when a checklist step commands the aircraft to exit in an "Aborted" status
        """
        self.flight.status = flightplan.STATUS_ABORTED
        self.Close()
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



class SAPPanelText(wx.Panel):
    """
    A text panel to be drawn as part of a checklist step
    """
    def __init__(self,parent,checklistpanel):
        wx.Panel.__init__(self, parent = parent)
        step = parent.step
        self.checklistpanel = checklistpanel

        self.box = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.box)

        self.text_expanded = wx.TextCtrl(self, -1, checklistpanel.resource, style=wx.TE_MULTILINE|wx.TE_RICH2)
        self.box.Add(self.text_expanded, 1, wx.EXPAND)

    def set_text(self,text):
        print(text)
        self.text_expanded.SetValue(text)

class SAPPanelMedia(wx.Panel):
    """
    This panel is used for displaying media like video or image files
    """
    def __init__(self,parent,checklistpanel):
        wx.Panel.__init__(self, parent = parent)
        self.checklistpanel = checklistpanel
        self.set_content(checklistpanel.resource)
        self.Bind(wx.EVT_SIZE,self.on_size)

    def set_content(self,filename):
        # TODO support video
        # TODO error checking for filename
        # TODO actual filename image = wx.Image(filename, wx.BITMAP_TYPE_ANY)
        image = wx.Image("Aircraft/Fx61/aircraft_photo.JPG", wx.BITMAP_TYPE_ANY)
        image = image.Scale(300,300)
        imageBitmap = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(image))
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(imageBitmap)
        self.SetSizer(box)


    def on_size(self,event):
        # TODO scaling http://stackoverflow.com/questions/13705981/wxpython-automatically-resize-a-static-image-staticbitmap-to-fit-into-size
        return

class SAPPanelCode(wx.Panel):
    """
    This is used for displaying an interactive panel in a checklist step, which executes code
    (for example, communicating with the APM or accepting user input). Customized code panels
    will inherit from this.
    """
    def __init__(self,parent,checklistpanel):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.checklistpanel = checklistpanel
        self.box = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.box)

        self.text_expanded = wx.TextCtrl(self, -1, "This is where the expanded text goes", style=wx.TE_MULTILINE|wx.TE_RICH2)

        self.box.Add(self.text_expanded)

class SAPPanelConnect(SAPPanelCode):
    def __init__(self,parent,checklistpanel):
        SAPPanelCode.__init__(self,parent,checklistpanel)

        sizer = wx.BoxSizer(wx.VERTICAL)

        # Port combo boxes
        box_ports = wx.BoxSizer(wx.HORIZONTAL)
        baudList = ['57600', '115200']
        label_port = wx.StaticText(self, -1, "Port",size=(80,-1))
        self.cb_port = wx.ComboBox(self, 500, "default value", (90, 50),
                         (160, -1), serial_ports(),
                         wx.CB_DROPDOWN
                         )
        label_baud = wx.StaticText(self, -1, "Baud",size=(50,-1))
        self.cb_baud = wx.ComboBox(self, 500, "115200", (90, 50),
                         (160, -1), baudList,
                         wx.CB_DROPDOWN
                         )

        box_ports.Add(label_port, 0, wx.TOP|wx.RIGHT, 5)
        box_ports.Add(self.cb_port, 1, wx.EXPAND|wx.ALL)
        box_ports.Add(label_baud, 0, wx.TOP|wx.RIGHT, 5)
        box_ports.Add(self.cb_baud, 1, wx.EXPAND|wx.ALL)
        sizer.Add(box_ports, 0, wx.EXPAND|wx.ALL)

        btn_connect = wx.Button(self, -1, "Connect")
        sizer.Add(btn_connect, 0, wx.EXPAND|wx.ALL)

        # Divider line
        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

        # All traffic text box
        self.textOutput = wx.TextCtrl(self, -1, "", size=(125, 300))
        sizer.Add(self.textOutput, 1, wx.EXPAND|wx.ALL)

        # Wire up buttons
        self.Bind(wx.EVT_BUTTON, self.on_click_connect, btn_connect)

        self.SetSizer(sizer)
        sizer.Fit(self)
        return

    def on_click_connect(self,e):
        """
        Process a click on the CONNECT button

        Attempt to connect to the MAV using the specified port and baud rate,
        then subscribe a function called check_heartbeat that will listen for
        a heartbeat message, as well as a function that will print all incoming
        MAVLink messages to the console.
        """
        # TODO timeout checking

        port = self.cb_port.GetValue()
        baud = int(self.cb_baud.GetValue())
        self.textOutput.AppendText("Connecting to " + port + " at " + str(baud) + " baud\n")

        self.master = self.parent.master = mavutil.mavlink_connection(port, baud=baud)
        thread = self.parent.thread = threading.Thread(target=self.parent.process_messages)
        thread.setDaemon(True)
        thread.start()

        self.master.message_hooks.append(self.check_heartbeat)
        #self.master.message_hooks.append(self.log_message)


        print("Connecting to " + port + " at " + str(baud) + "baud")
        self.textOutput.AppendText("Waiting for APM heartbeat\n")
        return

    def check_heartbeat(self,caller,msg):
        """
        Listens for a heartbeat message

        Once this function is subscribed to the dispatcher, it listens to every
        incoming MAVLINK message and watches for a 'HEARTBEAT' message. Once
        that message is received, the function updates the GUI and then
        unsubscribes itself.
        """

        if msg.get_type() ==  'HEARTBEAT':
            self.textOutput.AppendText("Heartbeat received from APM (system %u component %u)\n" % (self.master.target_system, self.master.target_system))
            self.master.message_hooks.remove(self.check_heartbeat)
            self.parent.sb.SetStatusText("Connected to APM")


class SAPPanelFlightPlan(SAPPanelCode):
    def __init__(self,parent,checklistpanel):
        SAPPanelCode.__init__(self,parent,checklistpanel)



class SAPStatusBar(wx.StatusBar):
    def __init__(self, parent):
        wx.StatusBar.__init__(self, parent, -1)
        self.SetFieldsCount(1)
        self.SetStatusText("Disconnected", 0)
