# TODO: this will validate a checklist XML file to make sure it has internal integrity, no missing data, etc.

__author__ = 'markjacobsen'

from sap_frame_preflight import *
import serial, glob

class ChecklistPanelConnect(SAPPanelCode):
    def __init__(self,parent):
        SAPPanelCode.__init__(self,parent)

    def InitUI(self):
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


