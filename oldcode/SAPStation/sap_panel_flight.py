__author__ = 'markjacobsen'

import wx

class SAPPanelFlight(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self, parent = parent)

        self.notebook = wx.Notebook(self)

        self.page1 = SAPPanelFlightPage1(self.notebook)
        self.page2 = SAPPanelFlightPage2(self.notebook)
        self.notebook.AddPage(self.page1,"Flight Page 1")
        self.notebook.AddPage(self.page2,"Flight Page 2")

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.notebook,1,wx.EXPAND)
        self.SetSizer(box)


class SAPPanelFlightPage1(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self, parent = parent)
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(wx.StaticText(self, -1, "Page 1 blah blah blah blah blah blah"),wx.EXPAND)
        self.SetSizer(box)

class SAPPanelFlightPage2(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self, parent = parent)
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(wx.StaticText(self, -1, "Page 2"),wx.EXPAND)
        self.SetSizer(box)
