__author__ = 'markjacobsen'

import wx

class SAPPanelMap(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self, parent = parent)


        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(wx.StaticText(self, -1, "Map"),1,wx.EXPAND)
        self.SetSizer(box)
