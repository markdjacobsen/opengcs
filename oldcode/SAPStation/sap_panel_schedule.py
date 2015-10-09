__author__ = 'markjacobsen'

import wx

class SAPPanelSchedule(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self, parent = parent)


        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(wx.StaticText(self, -1, "Schedule"),1,wx.EXPAND)
        self.SetSizer(box)
